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
import time

@dataclass
class ConfiguracionSimulacion:
    """Clase para almacenar la configuración de la simulación"""
    velocidad_min: float = 10.0
    velocidad_max: float = 15.0
    duracion_simulacion: float = 300.0  # Duración en segundos

class Ciclista:
    """Clase optimizada para ciclistas con gestión de memoria"""
    
    def __init__(self, id):
        self.id = id
        self.coordenadas = (-1000, -1000)
        self.trayectoria = []
        self.velocidad = 0
        self.estado = 'inactivo'
        self.ruta = ""
        self.color = '#6C757D'
        self.tiempo_creacion = time.time()
        self.tiempo_ultima_actividad = time.time()
        
        # Límites de memoria por ciclista
        self.max_trayectoria_puntos = 50
        self.max_tiempo_inactivo = 300  # 5 minutos
    
    def reset(self):
        """Resetea el ciclista para reutilización"""
        self.coordenadas = (-1000, -1000)
        self.trayectoria = []
        self.velocidad = 0
        self.estado = 'inactivo'
        self.ruta = ""
        self.color = '#6C757D'
        self.tiempo_creacion = time.time()
        self.tiempo_ultima_actividad = time.time()
    
    def actualizar_posicion(self, x, y):
        """Actualiza la posición del ciclista"""
        self.coordenadas = (x, y)
        self.tiempo_ultima_actividad = time.time()
        
        # Limitar trayectoria para evitar uso excesivo de memoria
        if len(self.trayectoria) >= self.max_trayectoria_puntos:
            self.trayectoria = self.trayectoria[-self.max_trayectoria_puntos//2:]
        
        self.trayectoria.append((x, y))
    
    def es_antiguo(self):
        """Verifica si el ciclista es muy antiguo"""
        return time.time() - self.tiempo_ultima_actividad > self.max_tiempo_inactivo
    
    def completar_viaje(self):
        """Marca el ciclista como completado"""
        self.estado = 'completado'
        self.coordenadas = (-1000, -1000)  # Posición invisible

class PoolCiclistas:
    """Pool inteligente de ciclistas para reutilización"""
    
    def __init__(self, tamaño_inicial=100, tamaño_maximo=1000):
        self.tamaño_inicial = tamaño_inicial
        self.tamaño_maximo = tamaño_maximo
        self.ciclistas_disponibles = []
        self.ciclistas_activos = {}
        self.contador_id = 0
        self.estadisticas = {
            'creados': 0,
            'reutilizados': 0,
            'liberados': 0,
            'eliminados': 0
        }
        
        # Crear pool inicial
        self._inicializar_pool()
    
    def _inicializar_pool(self):
        """Inicializa el pool con ciclistas pre-creados"""
        for _ in range(self.tamaño_inicial):
            ciclista = Ciclista(self.contador_id)
            self.ciclistas_disponibles.append(ciclista)
            self.contador_id += 1
            self.estadisticas['creados'] += 1
    
    def obtener_ciclista(self):
        """Obtiene un ciclista del pool o crea uno nuevo"""
        if self.ciclistas_disponibles:
            # Reutilizar ciclista existente
            ciclista = self.ciclistas_disponibles.pop()
            ciclista.reset()
            self.ciclistas_activos[ciclista.id] = ciclista
            self.estadisticas['reutilizados'] += 1
            return ciclista
        else:
            # Crear nuevo ciclista si el pool está vacío
            if len(self.ciclistas_activos) < self.tamaño_maximo:
                ciclista = Ciclista(self.contador_id)
                self.contador_id += 1
                self.ciclistas_activos[ciclista.id] = ciclista
                self.estadisticas['creados'] += 1
                return ciclista
            else:
                # Pool lleno, reutilizar el más antiguo
                return self._reutilizar_mas_antiguo()
    
    def _reutilizar_mas_antiguo(self):
        """Reutiliza el ciclista más antiguo cuando el pool está lleno"""
        if not self.ciclistas_activos:
            return None
        
        # Encontrar el ciclista más antiguo
        id_mas_antiguo = min(self.ciclistas_activos.keys())
        ciclista = self.ciclistas_activos[id_mas_antiguo]
        
        # Resetear y reutilizar
        ciclista.reset()
        self.estadisticas['reutilizados'] += 1
        return ciclista
    
    def liberar_ciclista(self, ciclista):
        """Libera un ciclista al pool"""
        if ciclista.id in self.ciclistas_activos:
            del self.ciclistas_activos[ciclista.id]
            
            if len(self.ciclistas_disponibles) < self.tamaño_inicial:
                # Mantener pool mínimo
                self.ciclistas_disponibles.append(ciclista)
                self.estadisticas['liberados'] += 1
            else:
                # Pool lleno, eliminar ciclista
                del ciclista
                self.estadisticas['eliminados'] += 1
    
    def obtener_estadisticas(self):
        """Retorna estadísticas del pool"""
        return {
            'ciclistas_activos': len(self.ciclistas_activos),
            'ciclistas_disponibles': len(self.ciclistas_disponibles),
            'total_creados': self.estadisticas['creados'],
            'total_reutilizados': self.estadisticas['reutilizados'],
            'total_liberados': self.estadisticas['liberados'],
            'total_eliminados': self.estadisticas['eliminados'],
            'eficiencia': self.estadisticas['reutilizados'] / max(1, self.estadisticas['creados'])
        }

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
        
        # Sistema de rastreo de rutas
        self.rutas_utilizadas = {}  # Dict[ruta_str, contador] para contar uso de rutas
        self.rutas_por_ciclista = {}  # Dict[ciclista_id, ruta_info] para rastrear rutas individuales
        
        # Sistema de rastreo de estado de ciclistas
        self.estado_ciclistas = {}  # Dict[ciclista_id, estado] para rastrear si están activos o completados
        self.ciclistas_por_nodo = {}  # Dict[nodo_origen, contador] para contar ciclistas por nodo de origen
        
        # Sistema de perfiles y rutas
        self.perfiles_df = None  # DataFrame con perfiles de ciclistas
        self.rutas_df = None  # DataFrame con matriz de probabilidades de destino
        self.perfiles_ciclistas = {}  # Dict[ciclista_id, perfil] para rastrear perfil de cada ciclista
        
        # ✅ OPTIMIZACIÓN: Cache de rendimiento
        self.rangos_atributos = {}  # Rangos pre-calculados de atributos
        self.rangos_calculados = False  # Flag para evitar recálculos
        self.grafos_por_perfil = {}  # Cache de grafos optimizados por perfil
        self.grafo_base = None  # Referencia al grafo original
        
        # ✅ OPTIMIZACIÓN: Cache inteligente de rutas
        self.rutas_por_perfil = {}  # Cache de rutas por perfil
        self.max_rutas_por_perfil = 100  # Límite de rutas por perfil
        self.max_rutas_total = 500  # Límite total de rutas en cache
        
        # ✅ OPTIMIZACIÓN: Pool de objetos para ciclistas
        self.pool_ciclistas = PoolCiclistas()
        self.estadisticas_persistentes = {
            'total_ciclistas_creados': 0,
            'total_ciclistas_completados': 0,
            'total_ciclistas_eliminados': 0,
            'total_viajes_completados': 0,
            'total_distancia_recorrida': 0.0
        }
    
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
    
    def configurar_grafo(self, grafo: nx.Graph, posiciones: Dict, perfiles_df=None, rutas_df=None):
        """Configura el grafo NetworkX y sus posiciones para la simulación - OPTIMIZADO"""
        if not self._validar_grafo(grafo):
            print("⚠️ Advertencia: El grafo no es válido")
            self.usar_grafo_real = False
            return False
            
        self.grafo = grafo
        self.pos_grafo = posiciones
        self.usar_grafo_real = True
        
        # ✅ OPTIMIZACIÓN: Guardar referencia al grafo base para cache
        self.grafo_base = grafo.copy()
        
        # Configurar perfiles y rutas si están disponibles
        self.perfiles_df = perfiles_df
        self.rutas_df = rutas_df
        
        # ✅ OPTIMIZACIÓN: Pre-calcular rangos al cargar el grafo
        self._precalcular_rangos_atributos()
        
        # ✅ OPTIMIZACIÓN: Configurar límites adaptativos
        self._configurar_limites_adaptativos()
        
        # Limpiar cache de grafos por perfil al cambiar grafo
        self.grafos_por_perfil = {}
        self.rutas_por_perfil = {}
        
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
        # Paleta de colores más oscuros y distintivos
        colores_base = [
            '#CC0000',  # Rojo oscuro
            '#006666',  # Verde azulado oscuro
            '#003366',  # Azul marino
            '#006600',  # Verde oscuro
            '#CC6600',  # Naranja oscuro
            '#660066',  # Púrpura oscuro
            '#006633',  # Verde bosque
            '#CC9900',  # Dorado oscuro
            '#663399',  # Violeta oscuro
            '#003399',  # Azul oscuro
            '#CC3300',  # Rojo naranja oscuro
            '#006600',  # Verde esmeralda oscuro
            '#990000',  # Rojo vino
            '#4B0082',  # Índigo
            '#2F4F2F',  # Verde oliva oscuro
            '#8B4513',  # Marrón oscuro
            '#800080',  # Púrpura
            '#191970',  # Azul medianoche
            '#2E8B57',  # Verde mar
            '#8B0000'   # Rojo oscuro intenso
        ]
        
        for i, nodo in enumerate(nodos):
            color = colores_base[i % len(colores_base)]
            self.colores_nodos[nodo] = color
        
        print(f"🎨 Colores asignados a {len(nodos)} nodos: {self.colores_nodos}")
    
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
        """Obtiene la distancia real del arco entre dos nodos para simulación
        
        IMPORTANTE: Esta función SIEMPRE devuelve distancias reales en metros
        para garantizar tiempos de simulación realistas, independientemente
        de qué se muestre en la visualización.
        """
        if not self.grafo:
            return 50.0  # Distancia por defecto
        
        try:
            if self.grafo.has_edge(origen, destino):
                # SIEMPRE priorizar distancia_real para simulación (tiempos realistas)
                if 'distancia_real' in self.grafo[origen][destino]:
                    return self.grafo[origen][destino]['distancia_real']
                
                # Fallback: usar distancia original si no hay distancia_real
                elif 'distancia' in self.grafo[origen][destino]:
                    return self.grafo[origen][destino]['distancia']
                
                # Fallback: usar weight si es una distancia real (no normalizada)
                else:
                    peso = self.grafo[origen][destino].get('weight', 50.0)
                    if peso >= 10.0:  # Es distancia real directa
                        return peso
                    else:  # Es peso compuesto normalizado, convertir a distancia real
                        # Convertir peso compuesto (0-1) a distancia real (20-200m)
                        return 20 + (1 - peso) * 180
            else:
                # Si no hay arco directo, calcular distancia euclidiana
                pos_origen = self._obtener_coordenada_nodo(origen)
                pos_destino = self._obtener_coordenada_nodo(destino)
                return np.sqrt((pos_destino[0] - pos_origen[0])**2 + (pos_destino[1] - pos_origen[1])**2)
        except Exception:
            return 50.0  # Fallback
    
    def _obtener_atributos_arco(self, origen: str, destino: str) -> dict:
        """Obtiene todos los atributos del arco entre dos nodos"""
        if not self.grafo or not self.grafo.has_edge(origen, destino):
            return {}
        
        try:
            return dict(self.grafo[origen][destino])
        except Exception:
            return {}
    
    def _calcular_velocidad_ajustada(self, velocidad_base: float, origen: str, destino: str) -> float:
        """Calcula la velocidad ajustada basada en los atributos del arco
        
        Esta función respeta los límites de velocidad configurados por el usuario,
        asegurando que la velocidad ajustada nunca sea menor a la velocidad mínima
        ni mayor a la velocidad máxima configuradas.
        """
        atributos = self._obtener_atributos_arco(origen, destino)
        
        if not atributos:
            return velocidad_base
        
        # Importar GrafoUtils para usar la función optimizada
        from Simulador.utils.grafo_utils import GrafoUtils
        
        # Calcular velocidad ajustada respetando la configuración del usuario
        return GrafoUtils.calcular_velocidad_ajustada(
            velocidad_base=velocidad_base,
            atributos_arco=atributos,
            velocidad_min_config=self.config.velocidad_min,
            velocidad_max_config=self.config.velocidad_max
        )
    
    def _seleccionar_perfil_ciclista(self) -> dict:
        """Selecciona un perfil aleatorio para un nuevo ciclista"""
        if self.perfiles_df is None:
            # Perfil por defecto si no hay perfiles disponibles
            return {
                'id': 0,
                'pesos': {
                    'distancia': 0.4,
                    'seguridad': 0.3,
                    'luminosidad': 0.2,
                    'inclinacion': 0.1
                }
            }
        
        # Seleccionar perfil aleatorio
        perfil_id = np.random.choice(self.perfiles_df['PERFILES'])
        perfil_data = self.perfiles_df[self.perfiles_df['PERFILES'] == perfil_id].iloc[0]
        
        return {
            'id': int(perfil_id),
            'pesos': {
                'distancia': perfil_data['DISTANCIA'],
                'seguridad': perfil_data['SEGURIDAD'],
                'luminosidad': perfil_data['LUMINOSIDAD'],
                'inclinacion': perfil_data['INCLINACION']
            }
        }
    
    def _seleccionar_destino(self, nodo_origen: str) -> str:
        """Selecciona un destino basado en las probabilidades de la matriz RUTAS"""
        if self.rutas_df is None:
            # Selección aleatoria simple si no hay matriz de rutas
            nodos_destino = [nodo for nodo in self.grafo.nodes() if nodo != nodo_origen]
            return np.random.choice(nodos_destino) if nodos_destino else None
        
        try:
            # Buscar la fila correspondiente al nodo origen
            fila_origen = self.rutas_df[self.rutas_df['NODO'] == nodo_origen]
            if fila_origen.empty:
                # Fallback si no se encuentra el nodo
                nodos_destino = [nodo for nodo in self.grafo.nodes() if nodo != nodo_origen]
                return np.random.choice(nodos_destino) if nodos_destino else None
            
            fila_origen = fila_origen.iloc[0]
            nodos_destino = [col for col in self.rutas_df.columns if col != 'NODO']
            probabilidades = [fila_origen[nodo] for nodo in nodos_destino]
            
            # Seleccionar destino basado en probabilidades
            return np.random.choice(nodos_destino, p=probabilidades)
            
        except Exception as e:
            print(f"⚠️ Error seleccionando destino: {e}")
            # Fallback en caso de error
            nodos_destino = [nodo for nodo in self.grafo.nodes() if nodo != nodo_origen]
            return np.random.choice(nodos_destino) if nodos_destino else None
    
    def _calcular_peso_compuesto_perfil(self, atributos_arco: dict, perfil_ciclista: dict) -> float:
        """Calcula peso compuesto dinámicamente usando los pesos del perfil del ciclista
        
        IMPORTANTE: Esta función normaliza los atributos en tiempo real basándose en:
        1. Los rangos de valores del grafo completo
        2. Los pesos de preferencia del perfil del ciclista específico
        """
        peso = 0.0
        
        # Obtener rangos de normalización del grafo completo
        if not self.grafo:
            return 0.0
            
        rangos = self._obtener_rangos_atributos()
        
        for attr, valor in atributos_arco.items():
            # Solo procesar atributos que están en el perfil del ciclista
            if attr in perfil_ciclista['pesos'] and attr in rangos:
                min_val, max_val = rangos[attr]
                
                if max_val > min_val and isinstance(valor, (int, float)):
                    # Normalizar atributo según su tipo
                    if attr == 'distancia':
                        # Para distancia, valores más altos = peor (invertir)
                        norm_val = 1 - (valor - min_val) / (max_val - min_val)
                    elif attr in ['seguridad', 'luminosidad']:
                        # Para seguridad y luminosidad, valores más altos = mejor
                        norm_val = (valor - min_val) / (max_val - min_val)
                    elif attr == 'inclinacion':
                        # Para inclinación, valores más altos = peor (invertir)
                        norm_val = 1 - (valor - min_val) / (max_val - min_val)
                    else:
                        # Para otros atributos, asumir que valores más altos = mejor
                        norm_val = (valor - min_val) / (max_val - min_val)
                    
                    # Aplicar peso del perfil del ciclista
                    peso += norm_val * perfil_ciclista['pesos'][attr]
        
        return peso
    
    def _precalcular_rangos_atributos(self):
        """Pre-calcula los rangos de atributos una sola vez al cargar el grafo"""
        if self.rangos_calculados or not self.grafo:
            return
        
        self.rangos_atributos = {}
        atributos_valores = {}
        
        # Recopilar todos los valores una sola vez
        for edge in self.grafo.edges(data=True):
            for attr, valor in edge[2].items():
                if attr not in ['weight'] and isinstance(valor, (int, float)):
                    if attr not in atributos_valores:
                        atributos_valores[attr] = []
                    atributos_valores[attr].append(valor)
        
        # Calcular rangos una sola vez
        for attr, valores in atributos_valores.items():
            if valores:
                self.rangos_atributos[attr] = (min(valores), max(valores))
        
        self.rangos_calculados = True
        print(f"✅ Rangos pre-calculados para {len(self.rangos_atributos)} atributos")
    
    def _obtener_rangos_atributos(self) -> dict:
        """Obtiene los rangos min/max de cada atributo en el grafo - OPTIMIZADO"""
        # ✅ USAR rangos pre-calculados en lugar de calcular cada vez
        if not self.rangos_calculados:
            self._precalcular_rangos_atributos()
        
        return self.rangos_atributos.copy()
    
    def _obtener_grafo_para_perfil(self, perfil_ciclista: dict) -> nx.Graph:
        """Obtiene o crea un grafo optimizado para un perfil específico - CACHE OPTIMIZADO"""
        perfil_id = perfil_ciclista['id']
        
        # ✅ USAR cache si ya existe
        if perfil_id in self.grafos_por_perfil:
            return self.grafos_por_perfil[perfil_id]
        
        # ✅ CREAR grafo optimizado para este perfil
        grafo_optimizado = self.grafo_base.copy()
        
        # Calcular pesos una sola vez para este perfil
        for edge in grafo_optimizado.edges(data=True):
            origen, destino, datos = edge
            atributos_arco = {k: v for k, v in datos.items() if k not in ['weight', 'distancia_real']}
            
            nuevo_peso = self._calcular_peso_compuesto_perfil(atributos_arco, perfil_ciclista)
            grafo_optimizado[origen][destino]['weight'] = nuevo_peso
        
        # ✅ GUARDAR en cache
        self.grafos_por_perfil[perfil_id] = grafo_optimizado
        print(f"✅ Grafo optimizado creado para perfil {perfil_id}")
        return grafo_optimizado
    
    def _obtener_ruta_inteligente(self, nodo_origen: str, nodo_destino: str, perfil_ciclista: dict) -> List[str]:
        """Cache inteligente que solo calcula rutas cuando es necesario - OPTIMIZADO"""
        perfil_id = perfil_ciclista['id']
        ruta_key = (nodo_origen, nodo_destino)
        
        # Inicializar cache si no existe
        if perfil_id not in self.rutas_por_perfil:
            self.rutas_por_perfil[perfil_id] = {}
        
        # ✅ USAR cache si existe
        if ruta_key in self.rutas_por_perfil[perfil_id]:
            return self.rutas_por_perfil[perfil_id][ruta_key]
        
        # ✅ CALCULAR y guardar en cache
        grafo_optimizado = self._obtener_grafo_para_perfil(perfil_ciclista)
        try:
            ruta = nx.shortest_path(grafo_optimizado, nodo_origen, nodo_destino, weight='weight')
            self.rutas_por_perfil[perfil_id][ruta_key] = ruta
            
            # ✅ LIMPIAR cache si es necesario
            self._limpiar_cache_si_necesario()
            
            return ruta
        except nx.NetworkXNoPath:
            return None
    
    def _limpiar_cache_si_necesario(self):
        """Limpia cache si usa demasiada memoria - OPTIMIZACIÓN DE MEMORIA"""
        total_rutas = sum(len(rutas) for rutas in self.rutas_por_perfil.values())
        
        # Límite: máximo 500 rutas en cache
        if total_rutas > self.max_rutas_total:
            # Limpiar 50% de las rutas menos usadas
            for perfil_id in self.rutas_por_perfil:
                rutas = self.rutas_por_perfil[perfil_id]
                if len(rutas) > 10:  # Mantener al menos 10 rutas por perfil
                    # Eliminar la mitad de las rutas
                    rutas_a_eliminar = list(rutas.keys())[:len(rutas)//2]
                    for ruta_key in rutas_a_eliminar:
                        del rutas[ruta_key]
            
            print(f"✅ Cache limpiado: {total_rutas} → {sum(len(rutas) for rutas in self.rutas_por_perfil.values())} rutas")
    
    def _configurar_limites_adaptativos(self):
        """Configura límites según el tamaño del grafo - OPTIMIZACIÓN ADAPTATIVA"""
        if not self.grafo:
            return
        
        num_nodos = len(self.grafo.nodes())
        num_perfiles = len(self.perfiles_df) if self.perfiles_df is not None else 1
        
        # Límites adaptativos
        if num_nodos <= 10:
            self.max_rutas_por_perfil = 50
            self.max_rutas_total = 200
        elif num_nodos <= 20:
            self.max_rutas_por_perfil = 100
            self.max_rutas_total = 500
        else:
            self.max_rutas_por_perfil = 200
            self.max_rutas_total = 1000
        
        print(f"✅ Límites adaptativos: {self.max_rutas_por_perfil} rutas/perfil, {self.max_rutas_total} total")
    
    def _interpolar_movimiento(self, origen: Tuple[float, float], destino: Tuple[float, float], 
                             distancia: float, velocidad: float, ciclista_id: int):
        """Interpola el movimiento suave entre dos puntos del grafo - OPTIMIZADO"""
        if distancia <= 0 or velocidad <= 0:
            return
        
        # ✅ OPTIMIZACIÓN CRÍTICA: Reducir frecuencia de 0.1s a 0.5s por paso
        tiempo_total = distancia / velocidad
        pasos = max(1, min(int(tiempo_total / 0.5), 200))  # Máximo 200 pasos (5x menos)
        
        # Pre-calcular incrementos para eficiencia
        dx = (destino[0] - origen[0]) / pasos
        dy = (destino[1] - origen[1]) / pasos
        
        for i in range(pasos + 1):
            yield self.env.timeout(0.5)  # ✅ 0.5 segundos por paso (5x menos operaciones)
            
            # Interpolación lineal optimizada
            x = origen[0] + i * dx
            y = origen[1] + i * dy
            
            self.coordenadas[ciclista_id] = (x, y)
            
            # ✅ OPTIMIZACIÓN: Solo guardar cada 5to punto para reducir memoria
            if i % 5 == 0 and len(self.trayectorias[ciclista_id]) < 100:
                self.trayectorias[ciclista_id].append((x, y))
        
    def inicializar_simulacion(self):
        """Inicializa una nueva simulación con los parámetros configurados"""
        # Limpiar datos anteriores
        self.coordenadas = []
        self.rutas = []
        self.colores = []
        self.trayectorias = []
        self.velocidades = []
        self.procesos = []
        self.ciclista_id_counter = 0
        
        # Crear entorno SimPy
        self.env = simpy.Environment()
        
        # Crear procesos de ciclistas
        if self.usar_grafo_real and self.distribuciones_nodos:
            # Usar generación realista con distribuciones
            self.env.process(self._generador_ciclistas_realista())
            # Proceso para detener la simulación después de la duración
            self.env.process(self._detener_por_tiempo())
        else:
            print("⚠️ No hay grafo cargado. Carga un grafo para iniciar la simulación.")
            return
        
        self.estado = "detenido"
        self.tiempo_actual = 0
        self.tiempo_total = self.config.duracion_simulacion
    
    def _detener_por_tiempo(self):
        """Detiene la simulación después del tiempo configurado"""
        yield self.env.timeout(self.config.duracion_simulacion)
        self.estado = "completada"
        print(f"✅ Simulación completada después de {self.config.duracion_simulacion} segundos")
    
    def _generador_ciclistas_realista(self):
        """Genera ciclistas de manera realista usando las distribuciones de arribo"""
        while self.estado != "completada":
            # Seleccionar nodo origen basado en las distribuciones
            nodo_origen = self._seleccionar_nodo_origen()
            
            if nodo_origen:
                # Generar tiempo de arribo para este nodo
                tiempo_arribo = self.generar_tiempo_arribo_nodo(nodo_origen)
                yield self.env.timeout(tiempo_arribo)
                
                # Crear nuevo ciclista
                ciclista_id = self.ciclista_id_counter
                self.ciclista_id_counter += 1
                
                # Generar ruta usando perfiles y matriz de rutas
                origen, destino, ruta_nodos = self._asignar_ruta_desde_nodo(nodo_origen, ciclista_id)
                if origen and destino:
                    velocidad = random.uniform(self.config.velocidad_min, self.config.velocidad_max)
                    
                    # Crear representación de la ruta para almacenar
                    ruta_str = f"{origen}->{destino}"
                    ruta_detallada = "->".join(ruta_nodos)
                    
                    # Rastrear la ruta utilizada
                    if ruta_detallada not in self.rutas_utilizadas:
                        self.rutas_utilizadas[ruta_detallada] = 0
                    self.rutas_utilizadas[ruta_detallada] += 1
                    
                    # Almacenar información de la ruta para este ciclista
                    self.rutas_por_ciclista[ciclista_id] = {
                        'origen': origen,
                        'destino': destino,
                        'ruta_detallada': ruta_detallada,
                        'ruta_simple': ruta_str
                    }
                    
                    # Marcar ciclista como activo
                    self.estado_ciclistas[ciclista_id] = 'activo'
                    
                    # Rastrear ciclistas por nodo de origen
                    if nodo_origen not in self.ciclistas_por_nodo:
                        self.ciclistas_por_nodo[nodo_origen] = 0
                    self.ciclistas_por_nodo[nodo_origen] += 1
                    
                    # Agregar datos del ciclista
                    self.rutas.append(ruta_str)
                    self.colores.append(self.colores_nodos.get(nodo_origen, '#6C757D'))
                    self.velocidades.append(velocidad)
                    self.coordenadas.append((-1000, -1000))  # Posición inicial invisible
                    self.trayectorias.append([])
                    
                    # Crear proceso del ciclista
                    proceso = self.env.process(self._ciclista(ciclista_id, velocidad))
                    self.procesos.append(proceso)
            else:
                # Fallback: esperar un poco y reintentar
                yield self.env.timeout(1.0)
    
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
    
    def _asignar_ruta_desde_nodo(self, nodo_origen: str, ciclista_id: int) -> tuple:
        """Genera una ruta desde el nodo origen usando perfiles y matriz de rutas"""
        if not self.grafo or nodo_origen not in self.grafo.nodes():
            return None, None, None
        
        # Seleccionar perfil para este ciclista
        perfil = self._seleccionar_perfil_ciclista()
        self.perfiles_ciclistas[ciclista_id] = perfil
        
        # Seleccionar destino usando matriz de rutas
        nodo_destino = self._seleccionar_destino(nodo_origen)
        
        if not nodo_destino:
            return None, None, None
        
        # Generar ruta usando pesos del perfil del ciclista - OPTIMIZADO CON CACHE
        try:
            # ✅ OPTIMIZACIÓN: Usar cache inteligente de rutas
            ruta_nodos = self._obtener_ruta_inteligente(nodo_origen, nodo_destino, perfil)
            
            if ruta_nodos is None:
                return None, None, None
            
            return nodo_origen, nodo_destino, ruta_nodos
            
        except nx.NetworkXNoPath:
            # Si no hay camino, intentar con selección aleatoria simple
            nodos_destino = [nodo for nodo in self.grafo.nodes() if nodo != nodo_origen]
            if nodos_destino:
                nodo_destino_alt = random.choice(nodos_destino)
                try:
                    ruta_nodos = nx.shortest_path(self.grafo, nodo_origen, nodo_destino_alt)
                    return nodo_origen, nodo_destino_alt, ruta_nodos
                except nx.NetworkXNoPath:
                    pass
            return None, None, None
        
    def _ciclista(self, id: int, velocidad: float):
        """Lógica de movimiento de un ciclista individual usando grafo real"""
        ruta = self.rutas[id]
        if not ruta or ruta == "N/A":
            return
            
        origen, destino = ruta.split('->')
        yield from self._ciclista_grafo_real(id, origen, destino, velocidad)
    
    def _ciclista_grafo_real(self, id: int, origen: str, destino: str, velocidad: float):
        """Movimiento usando coordenadas reales del grafo NetworkX con rutas dinámicas"""
        # Verificar que los nodos existen en el grafo
        if origen not in self.grafo.nodes() or destino not in self.grafo.nodes():
            print(f"⚠️ Error: Nodos {origen} o {destino} no existen en el grafo")
            return
        
        # Esperar tiempo de arribo basado en la distribución del nodo origen
        tiempo_arribo = self.generar_tiempo_arribo_nodo(origen)
        yield self.env.timeout(tiempo_arribo)
        
        # Obtener la ruta detallada para este ciclista
        if id in self.rutas_por_ciclista:
            ruta_detallada = self.rutas_por_ciclista[id]['ruta_detallada']
            nodos_ruta = ruta_detallada.split('->')
        else:
            # Fallback: ruta directa
            nodos_ruta = [origen, destino]
        
        # Posición inicial en el nodo origen
        pos_inicial = self._obtener_coordenada_nodo(nodos_ruta[0])
        self.coordenadas[id] = pos_inicial
        self.trayectorias[id].append(pos_inicial)
        
        # Mover a través de cada segmento de la ruta
        for i in range(len(nodos_ruta) - 1):
            nodo_actual = nodos_ruta[i]
            nodo_siguiente = nodos_ruta[i + 1]
            
            # Obtener coordenadas de los nodos
            pos_actual = self._obtener_coordenada_nodo(nodo_actual)
            pos_siguiente = self._obtener_coordenada_nodo(nodo_siguiente)
            
            # Obtener distancia real del arco
            distancia_real = self._obtener_distancia_arco(nodo_actual, nodo_siguiente)
            
            # Calcular velocidad ajustada basada en atributos del arco
            velocidad_ajustada = self._calcular_velocidad_ajustada(velocidad, nodo_actual, nodo_siguiente)
            
            # Actualizar velocidad del ciclista para estadísticas
            self.velocidades[id] = velocidad_ajustada
            
            # Movimiento interpolado suave entre nodos con velocidad ajustada
            yield from self._interpolar_movimiento(pos_actual, pos_siguiente, distancia_real, velocidad_ajustada, id)
        
        # Marcar ciclista como completado cuando termine su ruta
        self.estado_ciclistas[id] = 'completado'
        
        # Mover ciclista fuera de la vista (posición invisible)
        self.coordenadas[id] = (-1000, -1000)  # Posición fuera del área visible
    
    
    def ejecutar_paso(self):
        """Ejecuta un paso de la simulación"""
        if self.env and self.estado == "ejecutando":
            self.env.step()
            self.tiempo_actual = self.env.now
            
            # ✅ OPTIMIZACIÓN: Gestión inteligente de memoria cada 10 pasos
            if int(self.tiempo_actual) % 10 == 0:
                self._gestionar_memoria_inteligente()
            
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
    
    def limpiar_cache_optimizaciones(self):
        """Limpia el cache de optimizaciones para liberar memoria"""
        self.grafos_por_perfil = {}
        self.rutas_por_perfil = {}
        self.pool_ciclistas = PoolCiclistas()  # Reiniciar pool
        print("✅ Cache de optimizaciones limpiado")
    
    def obtener_estadisticas_cache(self) -> Dict:
        """Retorna estadísticas del cache para monitoreo"""
        total_rutas = sum(len(rutas) for rutas in self.rutas_por_perfil.values())
        total_grafos = len(self.grafos_por_perfil)
        
        return {
            'rutas_en_cache': total_rutas,
            'grafos_en_cache': total_grafos,
            'max_rutas_total': self.max_rutas_total,
            'max_rutas_por_perfil': self.max_rutas_por_perfil,
            'porcentaje_uso_cache': (total_rutas / self.max_rutas_total) * 100 if self.max_rutas_total > 0 else 0
        }
    
    def _gestionar_memoria_inteligente(self):
        """Gestión inteligente de memoria para múltiples ciclistas"""
        # Calcular uso actual de memoria
        uso_memoria = self._calcular_uso_memoria()
        
        # Limpiar según el uso
        if uso_memoria > 0.9:  # 90% de uso
            self._limpieza_agresiva()
        elif uso_memoria > 0.7:  # 70% de uso
            self._limpieza_moderada()
        elif uso_memoria > 0.5:  # 50% de uso
            self._limpieza_basica()
        
        # Limpiar ciclistas antiguos
        self._limpiar_ciclistas_antiguos()
    
    def _calcular_uso_memoria(self) -> float:
        """Calcula el uso actual de memoria"""
        total_ciclistas = len(self.coordenadas)
        total_trayectorias = sum(len(t) for t in self.trayectorias)
        total_rutas_cache = sum(len(rutas) for rutas in self.rutas_por_perfil.values())
        total_grafos_cache = len(self.grafos_por_perfil)
        
        # Estimación de memoria (valores aproximados)
        memoria_ciclistas = total_ciclistas * 200  # 200 bytes por ciclista
        memoria_trayectorias = total_trayectorias * 16  # 16 bytes por punto
        memoria_cache = (total_rutas_cache * 50) + (total_grafos_cache * 1000)
        
        memoria_total = memoria_ciclistas + memoria_trayectorias + memoria_cache
        memoria_maxima = 100 * 1024 * 1024  # 100MB máximo
        
        return memoria_total / memoria_maxima
    
    def _limpiar_ciclistas_antiguos(self):
        """Limpia ciclistas que han estado inactivos por mucho tiempo"""
        ciclistas_a_limpiar = []
        
        for i, estado in self.estado_ciclistas.items():
            if estado == 'completado' and i < len(self.coordenadas):
                # Verificar si el ciclista es antiguo (simulado)
                if len(self.trayectorias[i]) > 0:
                    ciclistas_a_limpiar.append(i)
        
        for i in ciclistas_a_limpiar[:len(ciclistas_a_limpiar)//2]:  # Limpiar solo la mitad
            # Marcar como eliminado
            self.estado_ciclistas[i] = 'eliminado'
            self.coordenadas[i] = (-1000, -1000)
            self.trayectorias[i] = []
            self.estadisticas_persistentes['total_ciclistas_eliminados'] += 1
        
        if ciclistas_a_limpiar:
            print(f"✅ Limpiados {len(ciclistas_a_limpiar)//2} ciclistas antiguos")
    
    def _limpieza_agresiva(self):
        """Limpieza agresiva de memoria"""
        # Liberar 50% de ciclistas completados
        ciclistas_completados = [i for i, estado in self.estado_ciclistas.items() if estado == 'completado']
        ciclistas_a_liberar = ciclistas_completados[:len(ciclistas_completados)//2]
        
        for i in ciclistas_a_liberar:
            self.estado_ciclistas[i] = 'eliminado'
            self.coordenadas[i] = (-1000, -1000)
            self.trayectorias[i] = []
            self.estadisticas_persistentes['total_ciclistas_eliminados'] += 1
        
        # Limpiar 75% del cache de rutas
        for perfil_id in self.rutas_por_perfil:
            rutas = self.rutas_por_perfil[perfil_id]
            if len(rutas) > 10:
                rutas_a_eliminar = list(rutas.keys())[:len(rutas)*3//4]
                for ruta_key in rutas_a_eliminar:
                    del rutas[ruta_key]
        
        print("✅ Limpieza agresiva de memoria completada")
    
    def _limpieza_moderada(self):
        """Limpieza moderada de memoria"""
        # Liberar 25% de ciclistas completados
        ciclistas_completados = [i for i, estado in self.estado_ciclistas.items() if estado == 'completado']
        ciclistas_a_liberar = ciclistas_completados[:len(ciclistas_completados)//4]
        
        for i in ciclistas_a_liberar:
            self.estado_ciclistas[i] = 'eliminado'
            self.coordenadas[i] = (-1000, -1000)
            self.trayectorias[i] = []
            self.estadisticas_persistentes['total_ciclistas_eliminados'] += 1
        
        # Limpiar 50% del cache de rutas
        for perfil_id in self.rutas_por_perfil:
            rutas = self.rutas_por_perfil[perfil_id]
            if len(rutas) > 20:
                rutas_a_eliminar = list(rutas.keys())[:len(rutas)//2]
                for ruta_key in rutas_a_eliminar:
                    del rutas[ruta_key]
        
        print("✅ Limpieza moderada de memoria completada")
    
    def _limpieza_basica(self):
        """Limpieza básica de memoria"""
        # Solo limpiar trayectorias largas
        for i, trayectoria in enumerate(self.trayectorias):
            if len(trayectoria) > 100:
                self.trayectorias[i] = trayectoria[-50:]
        
        print("✅ Limpieza básica de memoria completada")
    
    def obtener_estado_actual(self) -> Dict:
        """Retorna el estado actual de la simulación"""
        return {
            'estado': self.estado,
            'tiempo_actual': self.tiempo_actual,
            'coordenadas': self.coordenadas.copy(),
            'colores': self.colores.copy(),
            'ruta_actual': self.rutas.copy()
        }
    
    def obtener_ciclistas_activos(self) -> Dict:
        """Retorna solo los ciclistas que están activos (no completados)"""
        ciclistas_activos = {
            'coordenadas': [],
            'colores': [],
            'ruta_actual': [],
            'velocidades': [],
            'trayectorias': []
        }
        
        for i, (coords, color, ruta, velocidad, trayectoria) in enumerate(zip(
            self.coordenadas, self.colores, self.rutas, self.velocidades, self.trayectorias)):
            
            # Solo incluir si el ciclista está activo
            if i in self.estado_ciclistas and self.estado_ciclistas[i] == 'activo':
                ciclistas_activos['coordenadas'].append(coords)
                ciclistas_activos['colores'].append(color)
                ciclistas_activos['ruta_actual'].append(ruta)
                ciclistas_activos['velocidades'].append(velocidad)
                ciclistas_activos['trayectorias'].append(trayectoria)
        
        return ciclistas_activos
    
    def obtener_colores_nodos(self) -> Dict[str, str]:
        """Retorna el mapeo de colores por nodo"""
        return self.colores_nodos.copy()
    
    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas de la simulación"""
        # Contar ciclistas activos
        ciclistas_activos = sum(1 for estado in self.estado_ciclistas.values() if estado == 'activo')
        ciclistas_completados = sum(1 for estado in self.estado_ciclistas.values() if estado == 'completado')
        
        # Obtener velocidades solo de ciclistas activos
        velocidades_activas = []
        for i, velocidad in enumerate(self.velocidades):
            if i in self.estado_ciclistas and self.estado_ciclistas[i] == 'activo':
                velocidades_activas.append(velocidad)
        
        stats = {
            'total_ciclistas': len(self.coordenadas),
            'ciclistas_activos': ciclistas_activos,
            'ciclistas_completados': ciclistas_completados,
            'velocidad_promedio': np.mean(velocidades_activas) if velocidades_activas else 0,
            'velocidad_minima': min(velocidades_activas) if velocidades_activas else 0,
            'velocidad_maxima': max(velocidades_activas) if velocidades_activas else 0,
            'usando_grafo_real': self.usar_grafo_real,
            'duracion_simulacion': self.config.duracion_simulacion
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
        
        # Agregar estadísticas de rutas
        stats.update({
            'rutas_utilizadas': len(self.rutas_utilizadas),
            'total_viajes': sum(self.rutas_utilizadas.values()) if self.rutas_utilizadas else 0,
            'ruta_mas_usada': self._obtener_ruta_mas_usada(),
            'rutas_por_frecuencia': self._obtener_rutas_por_frecuencia()
        })
        
        # Agregar estadísticas de ciclistas por nodo
        stats.update({
            'ciclistas_por_nodo': self.ciclistas_por_nodo.copy(),
            'nodo_mas_activo': self._obtener_nodo_mas_activo()
        })
        
        # ✅ OPTIMIZACIÓN: Agregar estadísticas del pool y memoria
        stats.update({
            'estadisticas_persistentes': self.estadisticas_persistentes.copy(),
            'uso_memoria_porcentaje': self._calcular_uso_memoria() * 100,
            'memoria_estimada_mb': self._calcular_uso_memoria() * 100,  # Convertir a MB
            'pool_estadisticas': self.pool_ciclistas.obtener_estadisticas()
        })
        
        return stats
    
    def _obtener_ruta_mas_usada(self) -> str:
        """Obtiene la ruta más utilizada"""
        if not self.rutas_utilizadas:
            return "N/A"
        
        ruta_mas_usada = max(self.rutas_utilizadas.items(), key=lambda x: x[1])
        return f"{ruta_mas_usada[0]} ({ruta_mas_usada[1]} viajes)"
    
    def _obtener_rutas_por_frecuencia(self) -> list:
        """Obtiene las rutas ordenadas por frecuencia de uso"""
        if not self.rutas_utilizadas:
            return []
        
        # Ordenar rutas por frecuencia (descendente)
        rutas_ordenadas = sorted(self.rutas_utilizadas.items(), key=lambda x: x[1], reverse=True)
        
        # Retornar las top 5 rutas
        return rutas_ordenadas[:5]
    
    def _obtener_nodo_mas_activo(self) -> str:
        """Obtiene el nodo que ha generado más ciclistas"""
        if not self.ciclistas_por_nodo:
            return "N/A"
        
        nodo_mas_activo = max(self.ciclistas_por_nodo.items(), key=lambda x: x[1])
        return f"Nodo {nodo_mas_activo[0]} ({nodo_mas_activo[1]} ciclistas)"
