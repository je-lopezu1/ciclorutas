import simpy
import random
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
import matplotlib.colors as mcolors
import networkx as nx
from scipy import stats

@dataclass
class ConfiguracionSimulacion:
    """Clase para almacenar la configuración de la simulación"""
    num_ciclistas: int = 20
    velocidad_min: float = 10.0
    velocidad_max: float = 15.0

class DistribucionNodo:
    """Clase para manejar distribuciones de probabilidad para tasas de arribo por nodo"""
    
    def __init__(self, tipo: str = 'exponencial', parametros: Dict = None):
        self.tipo = tipo.lower()
        self.parametros = parametros or {}
        self._validar_parametros()
    
    def _validar_parametros(self):
        """Valida y ajusta los parámetros según el tipo de distribución"""
        if self.tipo == 'exponencial':
            self.parametros.setdefault('lambda', 0.5)
            if self.parametros['lambda'] <= 0:
                self.parametros['lambda'] = 0.5
        elif self.tipo == 'poisson':
            self.parametros.setdefault('lambda', 2.0)
            if self.parametros['lambda'] <= 0:
                self.parametros['lambda'] = 2.0
        elif self.tipo == 'uniforme':
            self.parametros.setdefault('min', 1.0)
            self.parametros.setdefault('max', 5.0)
            if self.parametros['min'] >= self.parametros['max']:
                self.parametros['min'] = 1.0
                self.parametros['max'] = 5.0
    
    def generar_tiempo_arribo(self) -> float:
        """Genera un tiempo de arribo basado en la distribución configurada"""
        try:
            if self.tipo == 'exponencial':
                # Distribución exponencial: tiempo entre arribos
                return np.random.exponential(1.0 / self.parametros['lambda'])
            elif self.tipo == 'poisson':
                # Distribución de Poisson: número de eventos por unidad de tiempo
                eventos = np.random.poisson(self.parametros['lambda'])
                return max(0.1, eventos)  # Mínimo 0.1 segundos
            elif self.tipo == 'uniforme':
                # Distribución uniforme: tiempo constante entre min y max
                return np.random.uniform(self.parametros['min'], self.parametros['max'])
            else:
                return 1.0  # Fallback
        except Exception:
            return 1.0  # Fallback en caso de error
    
    def obtener_descripcion(self) -> str:
        """Retorna una descripción legible de la distribución"""
        if self.tipo == 'exponencial':
            return f"Exponencial (λ={self.parametros['lambda']:.2f})"
        elif self.tipo == 'poisson':
            return f"Poisson (λ={self.parametros['lambda']:.2f})"
        elif self.tipo == 'uniforme':
            return f"Uniforme ({self.parametros['min']:.1f}-{self.parametros['max']:.1f}s)"
        else:
            return "Desconocida"
    
    def actualizar_parametros(self, nuevos_parametros: Dict):
        """Actualiza los parámetros de la distribución"""
        self.parametros.update(nuevos_parametros)
        self._validar_parametros()

class SimuladorCiclorutas:
    """Clase principal para manejar la simulación de ciclorutas"""
    
    def __init__(self, config: ConfiguracionSimulacion, grafo_networkx: Optional[nx.Graph] = None):
        self.config = config
        self.env = None
        self.coordenadas = []
        self.rutas = []
        self.colores = []
        self.trayectorias = []
        self.velocidades = []
        self.procesos = []
        self.estado = "detenido"  # detenido, ejecutando, pausado
        self.tiempo_actual = 0
        self.tiempo_total = 0
        
        # Integración con NetworkX
        self.grafo = grafo_networkx
        self.pos_grafo = None
        self.usar_grafo_real = grafo_networkx is not None
        
        # Sistema de distribuciones de probabilidad
        self.distribuciones_nodos = {}  # Dict[nodo_id, DistribucionNodo]
        self.tasas_arribo = {}  # Dict[nodo_id, tasa_actual]
        
        # Sistema de colores dinámico basado en nodos
        self.colores_nodos = {}  # Dict[nodo_id, color]
        self.rutas_dinamicas = []  # Lista de rutas calculadas dinámicamente
    
    def configurar_distribuciones_nodos(self, distribuciones: Dict[str, Dict]):
        """Configura las distribuciones de probabilidad para cada nodo"""
        self.distribuciones_nodos = {}
        
        for nodo_id, config_dist in distribuciones.items():
            tipo = config_dist.get('tipo', 'exponencial')
            parametros = config_dist.get('parametros', {})
            self.distribuciones_nodos[nodo_id] = DistribucionNodo(tipo, parametros)
        
        print(f"✅ Distribuciones configuradas para {len(self.distribuciones_nodos)} nodos")
    
    def obtener_distribuciones_nodos(self) -> Dict[str, Dict]:
        """Retorna la configuración actual de distribuciones"""
        resultado = {}
        for nodo_id, distribucion in self.distribuciones_nodos.items():
            resultado[nodo_id] = {
                'tipo': distribucion.tipo,
                'parametros': distribucion.parametros.copy(),
                'descripcion': distribucion.obtener_descripcion()
            }
        return resultado
    
    def actualizar_distribucion_nodo(self, nodo_id: str, tipo: str, parametros: Dict):
        """Actualiza la distribución de un nodo específico"""
        self.distribuciones_nodos[nodo_id] = DistribucionNodo(tipo, parametros)
        print(f"✅ Distribución actualizada para nodo {nodo_id}: {tipo}")
    
    def generar_tiempo_arribo_nodo(self, nodo_id: str) -> float:
        """Genera un tiempo de arribo para un nodo específico"""
        if nodo_id in self.distribuciones_nodos:
            return self.distribuciones_nodos[nodo_id].generar_tiempo_arribo()
        else:
            # Distribución por defecto si no está configurada
            return np.random.exponential(2.0)  # 0.5 arribos por segundo
    
    def configurar_grafo(self, grafo: nx.Graph, posiciones: Dict):
        """Configura el grafo NetworkX y sus posiciones para la simulación"""
        if not self._validar_grafo(grafo):
            print("⚠️ Advertencia: El grafo no es válido")
            self.usar_grafo_real = False
            return False
            
        self.grafo = grafo
        self.pos_grafo = posiciones
        self.usar_grafo_real = True
        self._inicializar_grafo()
        return True
    
    def _validar_grafo(self, grafo: nx.Graph) -> bool:
        """Valida que el grafo sea adecuado para la simulación"""
        if not grafo or len(grafo.nodes()) < 2:
            return False
        
        # Verificar que hay al menos algunos arcos
        if len(grafo.edges()) == 0:
            return False
        
        # Verificar que todos los arcos tienen peso
        for edge in grafo.edges(data=True):
            if 'weight' not in edge[2] or edge[2]['weight'] <= 0:
                print(f"⚠️ Advertencia: Arco {edge[0]}-{edge[1]} no tiene peso válido")
                return False
        
        return True
    
    def _inicializar_grafo(self):
        """Inicializa el grafo y configura distribuciones por defecto"""
        if not self.grafo or not self.pos_grafo:
            return
        
        nodos = list(self.grafo.nodes())
        if len(nodos) < 2:
            print("⚠️ Advertencia: El grafo necesita al menos 2 nodos para la simulación")
            return
        
        # Inicializar distribuciones por defecto para todos los nodos
        self._inicializar_distribuciones_por_defecto(nodos)
        
        # Inicializar colores para cada nodo
        self._inicializar_colores_nodos(nodos)
        
        # Calcular rutas dinámicas
        self._calcular_rutas_dinamicas()
        
        print(f"✅ Grafo inicializado con {len(nodos)} nodos")
    
    def _inicializar_distribuciones_por_defecto(self, nodos: List[str]):
        """Inicializa distribuciones por defecto para todos los nodos"""
        for i, nodo in enumerate(nodos):
            if nodo not in self.distribuciones_nodos:
                # Distribución exponencial por defecto con tasas variadas
                lambda_val = 0.3 + (i * 0.2)  # Tasas de 0.3 a 0.9
                self.distribuciones_nodos[nodo] = DistribucionNodo('exponencial', {'lambda': lambda_val})
        
        print(f"✅ Distribuciones por defecto inicializadas para {len(nodos)} nodos")
    
    def _inicializar_colores_nodos(self, nodos: List[str]):
        """Inicializa colores únicos para cada nodo"""
        colores_base = [
            '#FF6B35', '#FF1744', '#00E676', '#2979FF', '#9C27B0',
            '#FF9800', '#4CAF50', '#2196F3', '#E91E63', '#795548'
        ]
        
        for i, nodo in enumerate(nodos):
            color = colores_base[i % len(colores_base)]
            self.colores_nodos[nodo] = color
        
        print(f"✅ Colores asignados a {len(nodos)} nodos")
    
    def _calcular_rutas_dinamicas(self):
        """Calcula todas las rutas posibles entre nodos del grafo"""
        if not self.grafo:
            return
        
        self.rutas_dinamicas = []
        nodos = list(self.grafo.nodes())
        
        # Calcular rutas entre todos los pares de nodos
        for origen in nodos:
            for destino in nodos:
                if origen != destino:
                    # Verificar si hay conexión directa o ruta
                    try:
                        if self.grafo.has_edge(origen, destino):
                            # Conexión directa
                            self.rutas_dinamicas.append((origen, destino))
                        else:
                            # Verificar si hay ruta usando pathfinding
                            if nx.has_path(self.grafo, origen, destino):
                                self.rutas_dinamicas.append((origen, destino))
                    except:
                        continue
        
        print(f"✅ {len(self.rutas_dinamicas)} rutas dinámicas calculadas")
    
    def _obtener_coordenada_nodo(self, nodo_id: str) -> Tuple[float, float]:
        """Obtiene las coordenadas reales del nodo en el grafo"""
        if self.pos_grafo and nodo_id in self.pos_grafo:
            return self.pos_grafo[nodo_id]
        return (0.0, 0.0)  # Fallback
    
    def _obtener_distancia_arco(self, origen: str, destino: str) -> float:
        """Obtiene la distancia real del arco entre dos nodos"""
        if not self.grafo:
            return 50.0  # Distancia por defecto
        
        try:
            if self.grafo.has_edge(origen, destino):
                return self.grafo[origen][destino].get('weight', 50.0)
            else:
                # Si no hay arco directo, calcular distancia euclidiana
                pos_origen = self._obtener_coordenada_nodo(origen)
                pos_destino = self._obtener_coordenada_nodo(destino)
                return np.sqrt((pos_destino[0] - pos_origen[0])**2 + (pos_destino[1] - pos_origen[1])**2)
        except Exception:
            return 50.0  # Fallback
    
    def _interpolar_movimiento(self, origen: Tuple[float, float], destino: Tuple[float, float], 
                             distancia: float, velocidad: float, ciclista_id: int):
        """Interpola el movimiento suave entre dos puntos del grafo"""
        if distancia <= 0 or velocidad <= 0:
            return
        
        # Optimización: calcular pasos de manera más eficiente
        tiempo_total = distancia / velocidad
        pasos = max(1, min(int(tiempo_total / 0.1), 1000))  # Limitar a 1000 pasos máximo
        
        # Pre-calcular incrementos para eficiencia
        dx = (destino[0] - origen[0]) / pasos
        dy = (destino[1] - origen[1]) / pasos
        
        for i in range(pasos + 1):
            yield self.env.timeout(0.1)
            
            # Interpolación lineal optimizada
            x = origen[0] + i * dx
            y = origen[1] + i * dy
            
            self.coordenadas[ciclista_id] = (x, y)
            
            # Optimización: limitar trayectorias para evitar uso excesivo de memoria
            if len(self.trayectorias[ciclista_id]) < 1000:
                self.trayectorias[ciclista_id].append((x, y))
            else:
                # Mantener solo los últimos 500 puntos
                self.trayectorias[ciclista_id] = self.trayectorias[ciclista_id][-500:]
                self.trayectorias[ciclista_id].append((x, y))
        
    def inicializar_simulacion(self):
        """Inicializa una nueva simulación con los parámetros configurados"""
        # Limpiar datos anteriores
        self.coordenadas = [(0, 0)] * self.config.num_ciclistas
        self.rutas = [None] * self.config.num_ciclistas  # Se asignarán dinámicamente
        self.colores = ['#6C757D'] * self.config.num_ciclistas  # Se asignarán dinámicamente
        self.trayectorias = [[] for _ in range(self.config.num_ciclistas)]
        self.velocidades = [random.uniform(self.config.velocidad_min, self.config.velocidad_max) 
                           for _ in range(self.config.num_ciclistas)]
        
        # Crear entorno SimPy
        self.env = simpy.Environment()
        self.procesos = []
        
        # Crear procesos de ciclistas
        if self.usar_grafo_real and self.distribuciones_nodos:
            # Usar generación realista con distribuciones
            self.env.process(self._generador_ciclistas_realista())
        else:
            print("⚠️ No hay grafo cargado. Carga un grafo para iniciar la simulación.")
            return
        
        self.estado = "detenido"
        self.tiempo_actual = 0
        self.tiempo_total = 0
    
    def _generador_ciclistas_realista(self):
        """Genera ciclistas de manera realista usando las distribuciones de arribo"""
        ciclista_id = 0
        
        while ciclista_id < self.config.num_ciclistas:
            # Seleccionar nodo origen basado en las distribuciones
            nodo_origen = self._seleccionar_nodo_origen()
            
            if nodo_origen:
                # Generar tiempo de arribo para este nodo
                tiempo_arribo = self.generar_tiempo_arribo_nodo(nodo_origen)
                yield self.env.timeout(tiempo_arribo)
                
                # Crear ciclista en este nodo
                if ciclista_id < self.config.num_ciclistas:
                    # Asignar ruta basada en el nodo origen
                    ruta = self._asignar_ruta_desde_nodo(nodo_origen)
                    velocidad = random.uniform(self.config.velocidad_min, self.config.velocidad_max)
                    
                    # Actualizar datos del ciclista
                    self.rutas[ciclista_id] = ruta
                    self.colores[ciclista_id] = self.colores_nodos.get(nodo_origen, '#6C757D')
                    self.velocidades[ciclista_id] = velocidad
                    
                    # Crear proceso del ciclista
                    proceso = self.env.process(self._ciclista(ciclista_id, velocidad))
                    self.procesos.append(proceso)
                    
                    ciclista_id += 1
            else:
                # Fallback: crear ciclista con distribución por defecto
                yield self.env.timeout(1.0)
                if ciclista_id < self.config.num_ciclistas:
                    ruta = random.choice(self.rutas_posibles)
                    velocidad = random.uniform(self.config.velocidad_min, self.config.velocidad_max)
                    
                    self.rutas[ciclista_id] = ruta
                    self.colores[ciclista_id] = self.color_map.get(ruta, '#6C757D')
                    self.velocidades[ciclista_id] = velocidad
                    
                    proceso = self.env.process(self._ciclista(ciclista_id, velocidad))
                    self.procesos.append(proceso)
                    
                    ciclista_id += 1
    
    def _seleccionar_nodo_origen(self) -> Optional[str]:
        """Selecciona un nodo origen basado en las distribuciones configuradas"""
        if not self.distribuciones_nodos:
            return None
        
        # Seleccionar nodo basado en las tasas de arribo (lambda)
        nodos = list(self.distribuciones_nodos.keys())
        tasas = []
        
        for nodo in nodos:
            distribucion = self.distribuciones_nodos[nodo]
            if distribucion.tipo in ['exponencial', 'poisson']:
                tasas.append(distribucion.parametros.get('lambda', 0.5))
            else:
                # Para uniforme, usar tasa promedio
                min_val = distribucion.parametros.get('min', 1.0)
                max_val = distribucion.parametros.get('max', 5.0)
                tasas.append(2.0 / ((min_val + max_val) / 2))  # Aproximación
        
        # Selección ponderada por tasas
        if tasas:
            total_tasa = sum(tasas)
            if total_tasa > 0:
                probabilidades = [tasa / total_tasa for tasa in tasas]
                return np.random.choice(nodos, p=probabilidades)
        
        return random.choice(nodos) if nodos else None
    
    def _asignar_ruta_desde_nodo(self, nodo_origen: str) -> str:
        """Asigna una ruta basada en el nodo origen usando rutas dinámicas"""
        # Filtrar rutas que empiecen desde el nodo origen
        rutas_desde_origen = [ruta for ruta in self.rutas_dinamicas if ruta[0] == nodo_origen]
        
        if rutas_desde_origen:
            # Seleccionar ruta aleatoria desde el nodo origen
            origen, destino = random.choice(rutas_desde_origen)
            return f"{origen}->{destino}"
        else:
            # Fallback: seleccionar cualquier ruta disponible
            if self.rutas_dinamicas:
                origen, destino = random.choice(self.rutas_dinamicas)
                return f"{origen}->{destino}"
            else:
                return "N/A"
        
    def _ciclista(self, id: int, velocidad: float):
        """Lógica de movimiento de un ciclista individual usando grafo real"""
        ruta = self.rutas[id]
        if not ruta or ruta == "N/A":
            return
            
        origen, destino = ruta.split('->')
        yield from self._ciclista_grafo_real(id, origen, destino, velocidad)
    
    def _ciclista_grafo_real(self, id: int, origen: str, destino: str, velocidad: float):
        """Movimiento usando coordenadas reales del grafo NetworkX con distribuciones de arribo"""
        # Verificar que los nodos existen en el grafo
        if origen not in self.grafo.nodes() or destino not in self.grafo.nodes():
            print(f"⚠️ Error: Nodos {origen} o {destino} no existen en el grafo")
            return
        
        # Esperar tiempo de arribo basado en la distribución del nodo origen
        tiempo_arribo = self.generar_tiempo_arribo_nodo(origen)
        yield self.env.timeout(tiempo_arribo)
        
        # Posición inicial en el nodo origen
        pos_inicial = self._obtener_coordenada_nodo(origen)
        self.coordenadas[id] = pos_inicial
        self.trayectorias[id].append(pos_inicial)
        
        # Obtener distancia real del arco
        distancia_real = self._obtener_distancia_arco(origen, destino)
        
        # Posición final en el nodo destino
        pos_final = self._obtener_coordenada_nodo(destino)
        
        # Movimiento interpolado suave
        yield from self._interpolar_movimiento(pos_inicial, pos_final, distancia_real, velocidad, id)
    
    
    def ejecutar_paso(self):
        """Ejecuta un paso de la simulación"""
        if self.env and self.estado == "ejecutando":
            self.env.step()
            self.tiempo_actual = self.env.now
            return True
        return False
    
    def pausar_simulacion(self):
        """Pausa la simulación"""
        if self.estado == "ejecutando":
            self.estado = "pausado"
    
    def reanudar_simulacion(self):
        """Reanuda la simulación pausada"""
        if self.estado == "pausado":
            self.estado = "ejecutando"
    
    def detener_simulacion(self):
        """Detiene la simulación"""
        self.estado = "detenido"
        self.tiempo_actual = 0
    
    def reiniciar_simulacion(self):
        """Reinicia la simulación desde el principio"""
        self.inicializar_simulacion()
    
    def obtener_estado_actual(self) -> Dict:
        """Retorna el estado actual de la simulación"""
        return {
            'estado': self.estado,
            'tiempo_actual': self.tiempo_actual,
            'coordenadas': self.coordenadas.copy(),
            'colores': self.colores.copy(),
            'ruta_actual': self.rutas.copy()
        }
    
    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas de la simulación"""
        stats = {
            'total_ciclistas': self.config.num_ciclistas,
            'velocidad_promedio': np.mean(self.velocidades) if self.velocidades else 0,
            'velocidad_minima': min(self.velocidades) if self.velocidades else 0,
            'velocidad_maxima': max(self.velocidades) if self.velocidades else 0,
            'usando_grafo_real': self.usar_grafo_real
        }
        
        # Agregar estadísticas del grafo si está disponible
        if self.usar_grafo_real and self.grafo:
            stats.update({
                'grafo_nodos': len(self.grafo.nodes()),
                'grafo_arcos': len(self.grafo.edges()),
                'grafo_conectado': nx.is_connected(self.grafo)
            })
            
            # Calcular distancia promedio de arcos
            if self.grafo.edges():
                distancias = [self.grafo[u][v].get('weight', 0) for u, v in self.grafo.edges()]
                stats['distancia_promedio_arcos'] = np.mean(distancias) if distancias else 0
            
            # Estadísticas de distribuciones
            if self.distribuciones_nodos:
                tipos_distribucion = {}
                tasas_promedio = []
                
                for nodo_id, distribucion in self.distribuciones_nodos.items():
                    tipo = distribucion.tipo
                    tipos_distribucion[tipo] = tipos_distribucion.get(tipo, 0) + 1
                    
                    if tipo in ['exponencial', 'poisson']:
                        tasas_promedio.append(distribucion.parametros.get('lambda', 0))
                
                stats.update({
                    'distribuciones_configuradas': len(self.distribuciones_nodos),
                    'tipos_distribucion': tipos_distribucion,
                    'tasa_arribo_promedio': np.mean(tasas_promedio) if tasas_promedio else 0
                })
        
        return stats
