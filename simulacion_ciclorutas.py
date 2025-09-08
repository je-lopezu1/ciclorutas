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

@dataclass
class ConfiguracionSimulacion:
    """Clase para almacenar la configuración de la simulación"""
    num_ciclistas: int = 20
    velocidad_min: float = 10.0
    velocidad_max: float = 15.0
    distancia_a: float = 50.0
    distancia_b: float = 30.0
    distancia_c: float = 40.0

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
        self.mapa_nodos = {}  # Mapeo entre nodos del grafo y puntos A,B,C
        self.usar_grafo_real = grafo_networkx is not None
        
        # Paleta de colores moderna y vibrante
        self.color_map = {
            'A->B': '#FF6B35',  # Naranja brillante y llamativo
            'A->C': '#FF1744',  # Rojo vibrante y energético
            'B->A': '#00E676',  # Verde neón brillante
            'C->A': '#2979FF'   # Azul eléctrico intenso
        }
        
        self.rutas_posibles = ['A->B', 'A->C', 'B->A', 'C->A']
    
    def configurar_grafo(self, grafo: nx.Graph, posiciones: Dict):
        """Configura el grafo NetworkX y sus posiciones para la simulación"""
        if not self._validar_grafo(grafo):
            print("⚠️ Advertencia: El grafo no es válido, usando sistema original")
            self.usar_grafo_real = False
            return False
            
        self.grafo = grafo
        self.pos_grafo = posiciones
        self.usar_grafo_real = True
        self._mapear_nodos_grafo()
        return True
    
    def _validar_grafo(self, grafo: nx.Graph) -> bool:
        """Valida que el grafo sea adecuado para la simulación"""
        if not grafo or len(grafo.nodes()) < 3:
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
    
    def _mapear_nodos_grafo(self):
        """Mapea automáticamente nodos del grafo a puntos A, B, C de la simulación"""
        if not self.grafo or not self.pos_grafo:
            return
        
        nodos = list(self.grafo.nodes())
        if len(nodos) < 3:
            print("⚠️ Advertencia: El grafo necesita al menos 3 nodos para la simulación")
            return
        
        # Mapeo automático: primeros 3 nodos = A, B, C
        self.mapa_nodos = {
            'A': nodos[0],
            'B': nodos[1], 
            'C': nodos[2]
        }
        
        print(f"✅ Mapeo de nodos configurado:")
        print(f"   A -> {self.mapa_nodos['A']}")
        print(f"   B -> {self.mapa_nodos['B']}")
        print(f"   C -> {self.mapa_nodos['C']}")
    
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
        self.rutas = ['A->B'] * self.config.num_ciclistas
        self.colores = ['blue'] * self.config.num_ciclistas
        self.trayectorias = [[] for _ in range(self.config.num_ciclistas)]
        self.velocidades = [random.uniform(self.config.velocidad_min, self.config.velocidad_max) 
                           for _ in range(self.config.num_ciclistas)]
        
        # Asignar rutas y colores
        for i in range(self.config.num_ciclistas):
            ruta = random.choice(self.rutas_posibles)
            self.rutas[i] = ruta
            self.colores[i] = self.color_map.get(ruta, '#6C757D')
        
        # Crear entorno SimPy
        self.env = simpy.Environment()
        self.procesos = []
        
        # Crear procesos de ciclistas
        for i in range(self.config.num_ciclistas):
            proceso = self.env.process(self._ciclista(i, self.velocidades[i]))
            self.procesos.append(proceso)
        
        self.estado = "detenido"
        self.tiempo_actual = 0
        self.tiempo_total = 0
        
    def _ciclista(self, id: int, velocidad: float):
        """Lógica de movimiento de un ciclista individual usando grafo real o sistema original"""
        ruta = self.rutas[id]
        origen, destino = ruta.split('->')

        if self.usar_grafo_real and self.grafo and self.pos_grafo:
            # Usar grafo NetworkX real
            yield from self._ciclista_grafo_real(id, origen, destino, velocidad)
        else:
            # Usar sistema original hardcodeado
            yield from self._ciclista_sistema_original(id, origen, destino, velocidad)
    
    def _ciclista_grafo_real(self, id: int, origen: str, destino: str, velocidad: float):
        """Movimiento usando coordenadas reales del grafo NetworkX"""
        # Obtener nodos reales del grafo
        nodo_origen = self.mapa_nodos.get(origen)
        nodo_destino = self.mapa_nodos.get(destino)
        
        if not nodo_origen or not nodo_destino:
            print(f"⚠️ Error: No se encontraron nodos para {origen} -> {destino}")
            return
        
        # Posición inicial en el nodo origen
        pos_inicial = self._obtener_coordenada_nodo(nodo_origen)
        self.coordenadas[id] = pos_inicial
        self.trayectorias[id].append(pos_inicial)
        
        # Obtener distancia real del arco
        distancia_real = self._obtener_distancia_arco(nodo_origen, nodo_destino)
        
        # Posición final en el nodo destino
        pos_final = self._obtener_coordenada_nodo(nodo_destino)
        
        # Movimiento interpolado suave
        yield from self._interpolar_movimiento(pos_inicial, pos_final, distancia_real, velocidad, id)
    
    def _ciclista_sistema_original(self, id: int, origen: str, destino: str, velocidad: float):
        """Sistema original hardcodeado como fallback"""
        # Posición inicial
        if origen == 'A':
            x, y = 0, 0
        elif origen == 'B':
            x = self.config.distancia_a + self.config.distancia_b
            y = self.config.distancia_b * 0.5
        elif origen == 'C':
            x = self.config.distancia_a + self.config.distancia_c
            y = -self.config.distancia_c * 0.5

        self.coordenadas[id] = (x, y)
        self.trayectorias[id].append((x, y))

        # Movimiento hacia bifurcación (punto X)
        if origen in ['B', 'C']:
            distancia = 0
            tramo = self.config.distancia_b if origen == 'B' else self.config.distancia_c
            angulo = 0.5 if origen == 'B' else -0.5
            
            while distancia < tramo:
                yield self.env.timeout(0.1)
                distancia += velocidad * 0.1
                x = self.config.distancia_a + (tramo - distancia)
                y = (tramo - distancia) * angulo
                self.coordenadas[id] = (x, y)
                self.trayectorias[id].append((x, y))

        # Movimiento desde A hacia bifurcación X
        if origen == 'A':
            distancia = 0
            while distancia < self.config.distancia_a:
                yield self.env.timeout(0.1)
                distancia += velocidad * 0.1
                x = distancia
                y = 0
                self.coordenadas[id] = (x, y)
                self.trayectorias[id].append((x, y))

        # Movimiento desde bifurcación X hacia destino
        if destino == 'B':
            distancia = 0
            while distancia < self.config.distancia_b:
                yield self.env.timeout(0.1)
                distancia += velocidad * 0.1
                x = self.config.distancia_a + distancia
                y = distancia * 0.5
                self.coordenadas[id] = (x, y)
                self.trayectorias[id].append((x, y))
        elif destino == 'C':
            distancia = 0
            while distancia < self.config.distancia_c:
                yield self.env.timeout(0.1)
                distancia += velocidad * 0.1
                x = self.config.distancia_a + distancia
                y = -distancia * 0.5
                self.coordenadas[id] = (x, y)
                self.trayectorias[id].append((x, y))
        elif destino == 'A':
            distancia = 0
            while distancia < self.config.distancia_a:
                yield self.env.timeout(0.1)
                distancia += velocidad * 0.1
                x = self.config.distancia_a - distancia
                y = 0
                self.coordenadas[id] = (x, y)
                self.trayectorias[id].append((x, y))
    
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
            'distancia_total_a': self.config.distancia_a,
            'distancia_total_b': self.config.distancia_b,
            'distancia_total_c': self.config.distancia_c,
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
        
        return stats
