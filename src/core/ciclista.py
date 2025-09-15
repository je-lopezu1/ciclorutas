#!/usr/bin/env python3
"""
🚴 MÓDULO DE CICLISTA - SIMULADOR DE CICLORUTAS 🚴

Este módulo contiene las clases y funciones para manejar el movimiento
y comportamiento de los ciclistas en la simulación.

Autor: Sistema de Simulación de Ciclorutas
Versión: 2.0 (Refactorizado)
"""

import simpy
import numpy as np
from typing import List, Tuple, Dict, Optional, Generator, Any
from dataclasses import dataclass
from enum import Enum
import networkx as nx


class EstadoCiclista(Enum):
    """Estados posibles de un ciclista."""
    ESPERANDO = "esperando"
    MOVIENDOSE = "movimiendose"
    COMPLETADO = "completado"
    PAUSADO = "pausado"


@dataclass
class InformacionCiclista:
    """Información básica de un ciclista."""
    id: int
    velocidad: float
    origen: str
    destino: str
    ruta_detallada: List[str]
    color: str
    estado: EstadoCiclista = EstadoCiclista.ESPERANDO
    tiempo_inicio: float = 0.0
    tiempo_fin: float = 0.0
    distancia_recorrida: float = 0.0


class InterpoladorMovimiento:
    """Clase para manejar la interpolación suave del movimiento de ciclistas."""
    
    def __init__(self, configuracion: Any):
        """
        Inicializa el interpolador.
        
        Args:
            configuracion: Configuración de la simulación
        """
        self.configuracion = configuracion
    
    def interpolar_movimiento(self, origen: Tuple[float, float], 
                            destino: Tuple[float, float], 
                            distancia: float, 
                            velocidad: float, 
                            ciclista_id: int,
                            env: simpy.Environment,
                            coordenadas: List[Tuple[float, float]],
                            trayectorias: List[List[Tuple[float, float]]]) -> Generator:
        """
        Interpola el movimiento suave entre dos puntos.
        
        Args:
            origen: Coordenadas de origen (x, y)
            destino: Coordenadas de destino (x, y)
            distancia: Distancia total a recorrer
            velocidad: Velocidad del ciclista
            ciclista_id: ID del ciclista
            env: Entorno de SimPy
            coordenadas: Lista de coordenadas actuales de todos los ciclistas
            trayectorias: Lista de trayectorias de todos los ciclistas
            
        Yields:
            simpy.Timeout: Eventos de timeout para el movimiento
        """
        if distancia <= 0 or velocidad <= 0:
            return
        
        # Calcular tiempo total y número de pasos
        tiempo_total = distancia / velocidad
        pasos = max(1, min(int(tiempo_total / self.configuracion.intervalo_actualizacion), 
                          self.configuracion.max_trayectorias_por_ciclista))
        
        # Pre-calcular incrementos para eficiencia
        dx = (destino[0] - origen[0]) / pasos
        dy = (destino[1] - origen[1]) / pasos
        
        for i in range(pasos + 1):
            yield env.timeout(self.configuracion.intervalo_actualizacion)
            
            # Interpolación lineal optimizada
            x = origen[0] + i * dx
            y = origen[1] + i * dy
            
            # Actualizar coordenadas del ciclista
            coordenadas[ciclista_id] = (x, y)
            
            # Actualizar trayectoria (con límite de memoria)
            if len(trayectorias[ciclista_id]) < self.configuracion.max_trayectorias_por_ciclista:
                trayectorias[ciclista_id].append((x, y))
            else:
                # Mantener solo los últimos puntos
                puntos_a_mantener = self.configuracion.max_trayectorias_por_ciclista // 2
                trayectorias[ciclista_id] = trayectorias[ciclista_id][-puntos_a_mantener:]
                trayectorias[ciclista_id].append((x, y))


class Ciclista:
    """
    Clase que representa un ciclista individual en la simulación.
    
    Esta clase encapsula toda la lógica de movimiento y comportamiento
    de un ciclista específico.
    """
    
    def __init__(self, info: InformacionCiclista, configuracion: Any):
        """
        Inicializa un ciclista.
        
        Args:
            info: Información básica del ciclista
            configuracion: Configuración de la simulación
        """
        self.info = info
        self.configuracion = configuracion
        self.interpolador = InterpoladorMovimiento(configuracion)
        self.distancia_recorrida = 0.0
    
    def ejecutar_viaje(self, env: simpy.Environment, 
                      grafo: nx.Graph, 
                      posiciones: Dict[str, Tuple[float, float]],
                      coordenadas: List[Tuple[float, float]],
                      trayectorias: List[List[Tuple[float, float]]]) -> Generator:
        """
        Ejecuta el viaje completo del ciclista.
        
        Args:
            env: Entorno de SimPy
            grafo: Grafo de la red de carreteras
            posiciones: Posiciones de los nodos
            coordenadas: Lista de coordenadas actuales
            trayectorias: Lista de trayectorias
            
        Yields:
            simpy.Timeout: Eventos de timeout durante el viaje
        """
        self.info.estado = EstadoCiclista.MOVIENDOSE
        self.info.tiempo_inicio = env.now
        
        # Verificar que los nodos existen en el grafo
        if (self.info.origen not in grafo.nodes() or 
            self.info.destino not in grafo.nodes()):
            print(f"⚠️ Error: Nodos {self.info.origen} o {self.info.destino} no existen en el grafo")
            self.info.estado = EstadoCiclista.COMPLETADO
            return
        
        # Posición inicial en el nodo origen
        pos_inicial = self._obtener_coordenada_nodo(posiciones, self.info.origen)
        coordenadas[self.info.id] = pos_inicial
        trayectorias[self.info.id].append(pos_inicial)
        
        # Mover a través de cada segmento de la ruta
        for i in range(len(self.info.ruta_detallada) - 1):
            nodo_actual = self.info.ruta_detallada[i]
            nodo_siguiente = self.info.ruta_detallada[i + 1]
            
            # Obtener coordenadas de los nodos
            pos_actual = self._obtener_coordenada_nodo(posiciones, nodo_actual)
            pos_siguiente = self._obtener_coordenada_nodo(posiciones, nodo_siguiente)
            
            # Obtener distancia real del arco
            distancia_real = self._obtener_distancia_arco(grafo, nodo_actual, nodo_siguiente)
            
            # Movimiento interpolado suave entre nodos
            yield from self.interpolador.interpolar_movimiento(
                pos_actual, pos_siguiente, distancia_real, 
                self.info.velocidad, self.info.id, env, 
                coordenadas, trayectorias
            )
            
            # Actualizar distancia recorrida
            self.distancia_recorrida += distancia_real
        
        # Marcar ciclista como completado
        self.info.estado = EstadoCiclista.COMPLETADO
        self.info.tiempo_fin = env.now
        
        # Mover ciclista fuera de la vista
        coordenadas[self.info.id] = (-1000, -1000)
    
    def _obtener_coordenada_nodo(self, posiciones: Dict[str, Tuple[float, float]], 
                                nodo_id: str) -> Tuple[float, float]:
        """
        Obtiene las coordenadas de un nodo.
        
        Args:
            posiciones: Diccionario de posiciones
            nodo_id: ID del nodo
            
        Returns:
            Tuple[float, float]: Coordenadas (x, y)
        """
        if posiciones and nodo_id in posiciones:
            return posiciones[nodo_id]
        return (0.0, 0.0)
    
    def _obtener_distancia_arco(self, grafo: nx.Graph, origen: str, destino: str) -> float:
        """
        Obtiene la distancia de un arco.
        
        Args:
            grafo: Grafo de la red
            origen: Nodo origen
            destino: Nodo destino
            
        Returns:
            float: Distancia del arco
        """
        if not grafo:
            return self.configuracion.distancia_por_defecto
        
        try:
            if grafo.has_edge(origen, destino):
                return grafo[origen][destino].get('weight', self.configuracion.distancia_por_defecto)
            else:
                # Calcular distancia euclidiana si no hay arco directo
                pos_origen = self._obtener_coordenada_nodo(
                    dict(grafo.nodes(data='pos', default=(0, 0))), origen)
                pos_destino = self._obtener_coordenada_nodo(
                    dict(grafo.nodes(data='pos', default=(0, 0))), destino)
                return np.sqrt((pos_destino[0] - pos_origen[0])**2 + 
                              (pos_destino[1] - pos_origen[1])**2)
        except Exception:
            return self.configuracion.distancia_por_defecto
    
    def pausar(self):
        """Pausa el movimiento del ciclista."""
        if self.info.estado == EstadoCiclista.MOVIENDOSE:
            self.info.estado = EstadoCiclista.PAUSADO
    
    def reanudar(self):
        """Reanuda el movimiento del ciclista."""
        if self.info.estado == EstadoCiclista.PAUSADO:
            self.info.estado = EstadoCiclista.MOVIENDOSE
    
    def obtener_estado_actual(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del ciclista.
        
        Returns:
            Dict[str, Any]: Estado actual del ciclista
        """
        return {
            'id': self.info.id,
            'velocidad': self.info.velocidad,
            'origen': self.info.origen,
            'destino': self.info.destino,
            'ruta_detallada': self.info.ruta_detallada,
            'color': self.info.color,
            'estado': self.info.estado.value,
            'tiempo_inicio': self.info.tiempo_inicio,
            'tiempo_fin': self.info.tiempo_fin,
            'distancia_recorrida': self.distancia_recorrida,
            'tiempo_transcurrido': self.info.tiempo_fin - self.info.tiempo_inicio if self.info.tiempo_fin > 0 else 0
        }
    
    def __str__(self) -> str:
        """Representación string del ciclista."""
        return (f"Ciclista(id={self.info.id}, "
                f"origen={self.info.origen}, "
                f"destino={self.info.destino}, "
                f"estado={self.info.estado.value})")


class GestorCiclistas:
    """
    Gestor para manejar múltiples ciclistas en la simulación.
    
    Esta clase coordina el comportamiento de todos los ciclistas
    y mantiene el estado global de la simulación.
    """
    
    def __init__(self, configuracion: Any):
        """
        Inicializa el gestor de ciclistas.
        
        Args:
            configuracion: Configuración de la simulación
        """
        self.configuracion = configuracion
        self.ciclistas: Dict[int, Ciclista] = {}
        self.coordenadas: List[Tuple[float, float]] = []
        self.trayectorias: List[List[Tuple[float, float]]] = []
        self.colores: List[str] = []
        self.velocidades: List[float] = []
        self.rutas: List[str] = []
        self.procesos: List[simpy.Process] = []
        self.contador_id = 0
    
    def crear_ciclista(self, origen: str, destino: str, ruta_detallada: List[str], 
                      velocidad: float, color: str) -> int:
        """
        Crea un nuevo ciclista.
        
        Args:
            origen: Nodo origen
            destino: Nodo destino
            ruta_detallada: Ruta detallada del viaje
            velocidad: Velocidad del ciclista
            color: Color del ciclista
            
        Returns:
            int: ID del ciclista creado
        """
        ciclista_id = self.contador_id
        self.contador_id += 1
        
        # Crear información del ciclista
        info = InformacionCiclista(
            id=ciclista_id,
            velocidad=velocidad,
            origen=origen,
            destino=destino,
            ruta_detallada=ruta_detallada,
            color=color
        )
        
        # Crear ciclista
        ciclista = Ciclista(info, self.configuracion)
        self.ciclistas[ciclista_id] = ciclista
        
        # Agregar a las listas globales
        self.coordenadas.append((-1000, -1000))  # Posición inicial invisible
        self.trayectorias.append([])
        self.colores.append(color)
        self.velocidades.append(velocidad)
        self.rutas.append(f"{origen}->{destino}")
        
        return ciclista_id
    
    def iniciar_viaje_ciclista(self, ciclista_id: int, env: simpy.Environment, 
                              grafo: nx.Graph, posiciones: Dict[str, Tuple[float, float]]) -> simpy.Process:
        """
        Inicia el viaje de un ciclista.
        
        Args:
            ciclista_id: ID del ciclista
            env: Entorno de SimPy
            grafo: Grafo de la red
            posiciones: Posiciones de los nodos
            
        Returns:
            simpy.Process: Proceso del viaje
        """
        if ciclista_id not in self.ciclistas:
            raise ValueError(f"Ciclista {ciclista_id} no existe")
        
        ciclista = self.ciclistas[ciclista_id]
        proceso = env.process(ciclista.ejecutar_viaje(
            env, grafo, posiciones, self.coordenadas, self.trayectorias
        ))
        
        self.procesos.append(proceso)
        return proceso
    
    def obtener_ciclistas_activos(self) -> Dict[str, Any]:
        """
        Obtiene información de los ciclistas activos.
        
        Returns:
            Dict[str, Any]: Información de ciclistas activos
        """
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
            if (i in self.ciclistas and 
                self.ciclistas[i].info.estado == EstadoCiclista.MOVIENDOSE):
                ciclistas_activos['coordenadas'].append(coords)
                ciclistas_activos['colores'].append(color)
                ciclistas_activos['ruta_actual'].append(ruta)
                ciclistas_activos['velocidades'].append(velocidad)
                ciclistas_activos['trayectorias'].append(trayectoria)
        
        return ciclistas_activos
    
    def obtener_estadisticas_ciclistas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de todos los ciclistas.
        
        Returns:
            Dict[str, Any]: Estadísticas de ciclistas
        """
        if not self.ciclistas:
            return {
                'total_ciclistas': 0,
                'ciclistas_activos': 0,
                'ciclistas_completados': 0,
                'velocidad_promedio': 0,
                'velocidad_minima': 0,
                'velocidad_maxima': 0
            }
        
        # Contar por estado
        estados = {}
        velocidades_activas = []
        
        for ciclista in self.ciclistas.values():
            estado = ciclista.info.estado.value
            estados[estado] = estados.get(estado, 0) + 1
            
            if estado == EstadoCiclista.MOVIENDOSE.value:
                velocidades_activas.append(ciclista.info.velocidad)
        
        return {
            'total_ciclistas': len(self.ciclistas),
            'ciclistas_activos': estados.get(EstadoCiclista.MOVIENDOSE.value, 0),
            'ciclistas_completados': estados.get(EstadoCiclista.COMPLETADO.value, 0),
            'velocidad_promedio': np.mean(velocidades_activas) if velocidades_activas else 0,
            'velocidad_minima': min(velocidades_activas) if velocidades_activas else 0,
            'velocidad_maxima': max(velocidades_activas) if velocidades_activas else 0,
            'estados': estados
        }
    
    def pausar_todos(self):
        """Pausa todos los ciclistas activos."""
        for ciclista in self.ciclistas.values():
            ciclista.pausar()
    
    def reanudar_todos(self):
        """Reanuda todos los ciclistas pausados."""
        for ciclista in self.ciclistas.values():
            ciclista.reanudar()
    
    def limpiar_ciclistas(self):
        """Limpia todos los ciclistas."""
        self.ciclistas.clear()
        self.coordenadas.clear()
        self.trayectorias.clear()
        self.colores.clear()
        self.velocidades.clear()
        self.rutas.clear()
        self.procesos.clear()
        self.contador_id = 0
    
    def obtener_ciclista(self, ciclista_id: int) -> Optional[Ciclista]:
        """
        Obtiene un ciclista por su ID.
        
        Args:
            ciclista_id: ID del ciclista
            
        Returns:
            Optional[Ciclista]: Ciclista o None si no existe
        """
        return self.ciclistas.get(ciclista_id)
    
    def __len__(self) -> int:
        """Retorna el número de ciclistas."""
        return len(self.ciclistas)
    
    def __str__(self) -> str:
        """Representación string del gestor."""
        return f"GestorCiclistas({len(self.ciclistas)} ciclistas)"
