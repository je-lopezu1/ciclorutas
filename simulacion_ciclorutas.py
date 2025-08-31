import simpy
import random
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
import matplotlib.colors as mcolors

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
    
    def __init__(self, config: ConfiguracionSimulacion):
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
        
        # Paleta de colores moderna y vibrante
        self.color_map = {
            'A->B': '#FF6B35',  # Naranja brillante y llamativo
            'A->C': '#FF1744',  # Rojo vibrante y energético
            'B->A': '#00E676',  # Verde neón brillante
            'C->A': '#2979FF'   # Azul eléctrico intenso
        }
        
        self.rutas_posibles = ['A->B', 'A->C', 'B->A', 'C->A']
        
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
        """Lógica de movimiento de un ciclista individual"""
        ruta = self.rutas[id]
        origen, destino = ruta.split('->')

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
        return {
            'total_ciclistas': self.config.num_ciclistas,
            'velocidad_promedio': np.mean(self.velocidades) if self.velocidades else 0,
            'velocidad_minima': min(self.velocidades) if self.velocidades else 0,
            'velocidad_maxima': max(self.velocidades) if self.velocidades else 0,
            'distancia_total_a': self.config.distancia_a,
            'distancia_total_b': self.config.distancia_b,
            'distancia_total_c': self.config.distancia_c
        }
