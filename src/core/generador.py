#!/usr/bin/env python3
"""
🏭 MÓDULO GENERADOR - SIMULADOR DE CICLORUTAS 🏭

Este módulo contiene las clases y funciones para generar ciclistas
de manera realista basada en distribuciones de probabilidad.

Autor: Sistema de Simulación de Ciclorutas
Versión: 2.0 (Refactorizado)
"""

import simpy
import random
import numpy as np
from typing import Dict, List, Tuple, Optional, Generator, Any
from dataclasses import dataclass
import networkx as nx

from ..data import GestorDistribuciones, DistribucionNodo, UtilidadesGrafo
from .ciclista import GestorCiclistas, InformacionCiclista, EstadoCiclista


@dataclass
class ConfiguracionGeneracion:
    """Configuración para la generación de ciclistas."""
    duracion_simulacion: float = 300.0
    max_ciclistas_simultaneos: int = 100
    usar_distribuciones: bool = True
    tasa_generacion_por_defecto: float = 0.5


class SelectorNodoOrigen:
    """Clase para seleccionar nodos origen basado en distribuciones."""
    
    def __init__(self, gestor_distribuciones: GestorDistribuciones):
        """
        Inicializa el selector de nodos origen.
        
        Args:
            gestor_distribuciones: Gestor de distribuciones de probabilidad
        """
        self.gestor_distribuciones = gestor_distribuciones
    
    def seleccionar_nodo_origen(self) -> Optional[str]:
        """
        Selecciona un nodo origen basado en las distribuciones configuradas.
        
        Returns:
            Optional[str]: ID del nodo origen seleccionado
        """
        if not self.gestor_distribuciones.distribuciones:
            return None
        
        # Seleccionar nodo basado en las tasas de arribo (lambda)
        nodos = list(self.gestor_distribuciones.distribuciones.keys())
        tasas = []
        
        for nodo in nodos:
            distribucion = self.gestor_distribuciones.distribuciones[nodo]
            if distribucion.tipo.value in ['exponencial', 'poisson']:
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


class AsignadorRutas:
    """Clase para asignar rutas a los ciclistas."""
    
    def __init__(self, grafo: nx.Graph, rutas_dinamicas: List[Tuple[str, str]]):
        """
        Inicializa el asignador de rutas.
        
        Args:
            grafo: Grafo de la red de carreteras
            rutas_dinamicas: Lista de rutas disponibles
        """
        self.grafo = grafo
        self.rutas_dinamicas = rutas_dinamicas
    
    def asignar_ruta_desde_nodo(self, nodo_origen: str) -> Tuple[Optional[str], Optional[str], List[str]]:
        """
        Genera una ruta aleatoria desde el nodo origen hasta cualquier otro nodo.
        
        Args:
            nodo_origen: Nodo de origen
            
        Returns:
            Tuple[Optional[str], Optional[str], List[str]]: (origen, destino, ruta_detallada)
        """
        if not self.grafo or nodo_origen not in self.grafo.nodes():
            return None, None, []
        
        # Obtener todos los nodos excepto el origen
        nodos_destino = [nodo for nodo in self.grafo.nodes() if nodo != nodo_origen]
        
        if not nodos_destino:
            return None, None, []
        
        # Seleccionar nodo destino aleatorio
        nodo_destino = random.choice(nodos_destino)
        
        # Generar ruta usando NetworkX (puede ser directa o con múltiples arcos)
        try:
            # Usar el algoritmo de camino más corto de NetworkX
            ruta_nodos = nx.shortest_path(self.grafo, nodo_origen, nodo_destino)
            return nodo_origen, nodo_destino, ruta_nodos
        except nx.NetworkXNoPath:
            # Si no hay camino, intentar con otro nodo destino
            for destino_alt in nodos_destino:
                try:
                    ruta_nodos = nx.shortest_path(self.grafo, nodo_origen, destino_alt)
                    return nodo_origen, destino_alt, ruta_nodos
                except nx.NetworkXNoPath:
                    continue
            return None, None, []
    
    def obtener_rutas_disponibles(self) -> List[Tuple[str, str]]:
        """
        Obtiene todas las rutas disponibles.
        
        Returns:
            List[Tuple[str, str]]: Lista de rutas (origen, destino)
        """
        return self.rutas_dinamicas.copy()
    
    def verificar_ruta_valida(self, origen: str, destino: str) -> bool:
        """
        Verifica si una ruta es válida.
        
        Args:
            origen: Nodo origen
            destino: Nodo destino
            
        Returns:
            bool: True si la ruta es válida
        """
        if not self.grafo:
            return False
        
        try:
            return nx.has_path(self.grafo, origen, destino)
        except:
            return False


class GeneradorCiclistas:
    """
    Clase principal para generar ciclistas de manera realista.
    
    Esta clase coordina la generación de ciclistas basada en distribuciones
    de probabilidad y asigna rutas apropiadas.
    """
    
    def __init__(self, configuracion: ConfiguracionGeneracion, 
                 gestor_distribuciones: GestorDistribuciones,
                 gestor_ciclistas: GestorCiclistas,
                 asignador_rutas: AsignadorRutas):
        """
        Inicializa el generador de ciclistas.
        
        Args:
            configuracion: Configuración de generación
            gestor_distribuciones: Gestor de distribuciones
            gestor_ciclistas: Gestor de ciclistas
            asignador_rutas: Asignador de rutas
        """
        self.configuracion = configuracion
        self.gestor_distribuciones = gestor_distribuciones
        self.gestor_ciclistas = gestor_ciclistas
        self.asignador_rutas = asignador_rutas
        self.selector_nodo = SelectorNodoOrigen(gestor_distribuciones)
        
        # Estadísticas de generación
        self.ciclistas_generados = 0
        self.rutas_utilizadas: Dict[str, int] = {}
        self.ciclistas_por_nodo: Dict[str, int] = {}
    
    def generar_ciclistas_realista(self, env: simpy.Environment, 
                                  grafo: nx.Graph, 
                                  posiciones: Dict[str, Tuple[float, float]],
                                  colores_nodos: Dict[str, str]) -> Generator:
        """
        Genera ciclistas de manera realista usando las distribuciones de arribo.
        
        Args:
            env: Entorno de SimPy
            grafo: Grafo de la red
            posiciones: Posiciones de los nodos
            colores_nodos: Colores asignados a los nodos
            
        Yields:
            simpy.Timeout: Eventos de timeout para la generación
        """
        while env.now < self.configuracion.duracion_simulacion:
            # Verificar límite de ciclistas simultáneos
            if len(self.gestor_ciclistas) >= self.configuracion.max_ciclistas_simultaneos:
                yield env.timeout(1.0)  # Esperar un poco
                continue
            
            # Seleccionar nodo origen
            nodo_origen = self.selector_nodo.seleccionar_nodo_origen()
            
            if nodo_origen:
                # Generar tiempo de arribo para este nodo
                tiempo_arribo = self.gestor_distribuciones.generar_tiempo_arribo_nodo(nodo_origen)
                yield env.timeout(tiempo_arribo)
                
                # Asignar ruta
                origen, destino, ruta_detallada = self.asignador_rutas.asignar_ruta_desde_nodo(nodo_origen)
                
                if origen and destino and ruta_detallada:
                    # Generar velocidad aleatoria
                    velocidad = random.uniform(8.0, 18.0)  # Velocidad realista para ciclistas
                    
                    # Obtener color del nodo origen
                    color = colores_nodos.get(nodo_origen, '#6C757D')
                    
                    # Crear ciclista
                    ciclista_id = self.gestor_ciclistas.crear_ciclista(
                        origen, destino, ruta_detallada, velocidad, color
                    )
                    
                    # Iniciar viaje del ciclista
                    self.gestor_ciclistas.iniciar_viaje_ciclista(
                        ciclista_id, env, grafo, posiciones
                    )
                    
                    # Actualizar estadísticas
                    self._actualizar_estadisticas_generacion(origen, destino, ruta_detallada)
                    
                    self.ciclistas_generados += 1
                else:
                    # No se pudo asignar ruta, esperar un poco
                    yield env.timeout(1.0)
            else:
                # No hay nodos disponibles, esperar un poco
                yield env.timeout(1.0)
    
    def _actualizar_estadisticas_generacion(self, origen: str, destino: str, ruta_detallada: List[str]):
        """
        Actualiza las estadísticas de generación.
        
        Args:
            origen: Nodo origen
            destino: Nodo destino
            ruta_detallada: Ruta detallada utilizada
        """
        # Rastrear ruta utilizada
        ruta_str = "->".join(ruta_detallada)
        if ruta_str not in self.rutas_utilizadas:
            self.rutas_utilizadas[ruta_str] = 0
        self.rutas_utilizadas[ruta_str] += 1
        
        # Rastrear ciclistas por nodo de origen
        if origen not in self.ciclistas_por_nodo:
            self.ciclistas_por_nodo[origen] = 0
        self.ciclistas_por_nodo[origen] += 1
    
    def obtener_estadisticas_generacion(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la generación de ciclistas.
        
        Returns:
            Dict[str, Any]: Estadísticas de generación
        """
        return {
            'ciclistas_generados': self.ciclistas_generados,
            'rutas_utilizadas': len(self.rutas_utilizadas),
            'total_viajes': sum(self.rutas_utilizadas.values()) if self.rutas_utilizadas else 0,
            'ruta_mas_usada': self._obtener_ruta_mas_usada(),
            'nodo_mas_activo': self._obtener_nodo_mas_activo(),
            'ciclistas_por_nodo': self.ciclistas_por_nodo.copy(),
            'rutas_por_frecuencia': self._obtener_rutas_por_frecuencia()
        }
    
    def _obtener_ruta_mas_usada(self) -> str:
        """Obtiene la ruta más utilizada."""
        if not self.rutas_utilizadas:
            return "N/A"
        
        ruta_mas_usada = max(self.rutas_utilizadas.items(), key=lambda x: x[1])
        return f"{ruta_mas_usada[0]} ({ruta_mas_usada[1]} viajes)"
    
    def _obtener_rutas_por_frecuencia(self) -> List[Tuple[str, int]]:
        """Obtiene las rutas ordenadas por frecuencia de uso."""
        if not self.rutas_utilizadas:
            return []
        
        # Ordenar rutas por frecuencia (descendente)
        rutas_ordenadas = sorted(self.rutas_utilizadas.items(), key=lambda x: x[1], reverse=True)
        
        # Retornar las top 5 rutas
        return rutas_ordenadas[:5]
    
    def _obtener_nodo_mas_activo(self) -> str:
        """Obtiene el nodo que ha generado más ciclistas."""
        if not self.ciclistas_por_nodo:
            return "N/A"
        
        nodo_mas_activo = max(self.ciclistas_por_nodo.items(), key=lambda x: x[1])
        return f"Nodo {nodo_mas_activo[0]} ({nodo_mas_activo[1]} ciclistas)"
    
    def reiniciar_estadisticas(self):
        """Reinicia las estadísticas de generación."""
        self.ciclistas_generados = 0
        self.rutas_utilizadas.clear()
        self.ciclistas_por_nodo.clear()


class GeneradorSimple:
    """
    Generador simple para casos de prueba o cuando no hay distribuciones configuradas.
    
    Este generador crea ciclistas de manera uniforme sin usar distribuciones
    de probabilidad complejas.
    """
    
    def __init__(self, configuracion: ConfiguracionGeneracion,
                 gestor_ciclistas: GestorCiclistas,
                 asignador_rutas: AsignadorRutas):
        """
        Inicializa el generador simple.
        
        Args:
            configuracion: Configuración de generación
            gestor_ciclistas: Gestor de ciclistas
            asignador_rutas: Asignador de rutas
        """
        self.configuracion = configuracion
        self.gestor_ciclistas = gestor_ciclistas
        self.asignador_rutas = asignador_rutas
    
    def generar_ciclistas_uniforme(self, env: simpy.Environment,
                                  grafo: nx.Graph,
                                  posiciones: Dict[str, Tuple[float, float]],
                                  colores_nodos: Dict[str, str]) -> Generator:
        """
        Genera ciclistas de manera uniforme.
        
        Args:
            env: Entorno de SimPy
            grafo: Grafo de la red
            posiciones: Posiciones de los nodos
            colores_nodos: Colores asignados a los nodos
            
        Yields:
            simpy.Timeout: Eventos de timeout para la generación
        """
        nodos = list(grafo.nodes()) if grafo else []
        
        while env.now < self.configuracion.duracion_simulacion:
            # Verificar límite de ciclistas simultáneos
            if len(self.gestor_ciclistas) >= self.configuracion.max_ciclistas_simultaneos:
                yield env.timeout(1.0)
                continue
            
            if nodos:
                # Seleccionar nodo origen aleatorio
                nodo_origen = random.choice(nodos)
                
                # Asignar ruta
                origen, destino, ruta_detallada = self.asignador_rutas.asignar_ruta_desde_nodo(nodo_origen)
                
                if origen and destino and ruta_detallada:
                    # Generar velocidad aleatoria
                    velocidad = random.uniform(8.0, 18.0)
                    
                    # Obtener color del nodo origen
                    color = colores_nodos.get(nodo_origen, '#6C757D')
                    
                    # Crear ciclista
                    ciclista_id = self.gestor_ciclistas.crear_ciclista(
                        origen, destino, ruta_detallada, velocidad, color
                    )
                    
                    # Iniciar viaje del ciclista
                    self.gestor_ciclistas.iniciar_viaje_ciclista(
                        ciclista_id, env, grafo, posiciones
                    )
                
                # Esperar tiempo uniforme
                yield env.timeout(random.uniform(1.0, 5.0))
            else:
                yield env.timeout(1.0)
    
    def obtener_estadisticas_generacion(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la generación de ciclistas.
        
        Returns:
            Dict[str, Any]: Estadísticas de generación
        """
        return {
            'ciclistas_generados': 0,
            'rutas_utilizadas': 0,
            'total_viajes': 0,
            'ruta_mas_usada': 'N/A',
            'nodo_mas_activo': 'N/A',
            'ciclistas_por_nodo': {},
            'rutas_por_frecuencia': []
        }


# Funciones de utilidad para crear generadores
def crear_generador_realista(configuracion: ConfiguracionGeneracion,
                           gestor_distribuciones: GestorDistribuciones,
                           gestor_ciclistas: GestorCiclistas,
                           asignador_rutas: AsignadorRutas) -> GeneradorCiclistas:
    """Crea un generador realista de ciclistas."""
    return GeneradorCiclistas(configuracion, gestor_distribuciones, gestor_ciclistas, asignador_rutas)


def crear_generador_simple(configuracion: ConfiguracionGeneracion,
                          gestor_ciclistas: GestorCiclistas,
                          asignador_rutas: AsignadorRutas) -> GeneradorSimple:
    """Crea un generador simple de ciclistas."""
    return GeneradorSimple(configuracion, gestor_ciclistas, asignador_rutas)
