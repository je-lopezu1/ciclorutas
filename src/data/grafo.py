#!/usr/bin/env python3
"""
🕸️ MÓDULO DE GRAFO - SIMULADOR DE CICLORUTAS 🕸️

Este módulo contiene las funciones para cargar, validar, inicializar y trabajar
con grafos de red de carreteras usando NetworkX.

Autor: Sistema de Simulación de Ciclorutas
Versión: 2.0 (Refactorizado)
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Optional, Set, Any
import pandas as pd


class ValidadorGrafo:
    """Clase para validar grafos de red de carreteras."""
    
    @staticmethod
    def validar_grafo(grafo: nx.Graph) -> Tuple[bool, List[str]]:
        """
        Valida que el grafo sea adecuado para la simulación.
        
        Args:
            grafo: Grafo de NetworkX a validar
            
        Returns:
            Tuple[bool, List[str]]: (es_valido, lista_de_errores)
        """
        errores = []
        
        if not grafo:
            errores.append("El grafo es None")
            return False, errores
        
        if len(grafo.nodes()) < 2:
            errores.append("El grafo debe tener al menos 2 nodos")
            return False, errores
        
        # Verificar que hay al menos algunos arcos
        if len(grafo.edges()) == 0:
            errores.append("El grafo debe tener al menos un arco")
            return False, errores
        
        # Verificar que todos los arcos tienen peso válido
        for edge in grafo.edges(data=True):
            if 'weight' not in edge[2] or edge[2]['weight'] <= 0:
                errores.append(f"Arco {edge[0]}-{edge[1]} no tiene peso válido")
        
        # Verificar conectividad
        if not nx.is_connected(grafo):
            errores.append("El grafo no está conectado")
        
        return len(errores) == 0, errores
    
    @staticmethod
    def validar_posiciones(posiciones: Dict, grafo: nx.Graph) -> Tuple[bool, List[str]]:
        """
        Valida que las posiciones sean consistentes con el grafo.
        
        Args:
            posiciones: Diccionario de posiciones de nodos
            grafo: Grafo de NetworkX
            
        Returns:
            Tuple[bool, List[str]]: (es_valido, lista_de_errores)
        """
        errores = []
        
        if not posiciones:
            errores.append("Las posiciones están vacías")
            return False, errores
        
        # Verificar que todos los nodos del grafo tienen posición
        for nodo in grafo.nodes():
            if nodo not in posiciones:
                errores.append(f"Nodo {nodo} no tiene posición definida")
        
        # Verificar que las posiciones son tuplas de 2 elementos
        for nodo, pos in posiciones.items():
            if not isinstance(pos, (tuple, list)) or len(pos) != 2:
                errores.append(f"Posición del nodo {nodo} debe ser una tupla de 2 elementos")
            elif not all(isinstance(coord, (int, float)) for coord in pos):
                errores.append(f"Coordenadas del nodo {nodo} deben ser números")
        
        return len(errores) == 0, errores


class CargadorGrafo:
    """Clase para cargar grafos desde diferentes fuentes."""
    
    @staticmethod
    def cargar_desde_excel(archivo: str) -> Tuple[Optional[nx.Graph], Optional[Dict], List[str]]:
        """
        Carga un grafo desde un archivo Excel.
        
        Args:
            archivo: Ruta del archivo Excel
            
        Returns:
            Tuple[Optional[nx.Graph], Optional[Dict], List[str]]: (grafo, posiciones, errores)
        """
        errores = []
        
        try:
            # Leer datos del Excel
            nodos_df = pd.read_excel(archivo, sheet_name="NODOS", engine="openpyxl")
            arcos_df = pd.read_excel(archivo, sheet_name="ARCOS", engine="openpyxl")
            
            # Crear grafo NetworkX
            G = nx.Graph()
            
            # Agregar nodos
            for nodo in nodos_df.iloc[:, 0]:
                G.add_node(nodo)
            
            # Agregar arcos con pesos
            for _, fila in arcos_df.iterrows():
                origen, destino, longitud = fila[0], fila[1], fila[2]
                G.add_edge(origen, destino, weight=longitud)
            
            # Calcular posiciones del grafo
            pos = nx.spring_layout(G, seed=42, k=2, iterations=50)
            
            # Normalizar y escalar las posiciones para mejor visualización
            pos_tuplas = {}
            if pos:
                # Obtener los valores mínimos y máximos
                x_values = [pos[nodo][0] for nodo in pos]
                y_values = [pos[nodo][1] for nodo in pos]
                
                x_min, x_max = min(x_values), max(x_values)
                y_min, y_max = min(y_values), max(y_values)
                
                # Escalar a un rango más amplio para mejor visualización
                x_range = x_max - x_min if x_max != x_min else 1.0
                y_range = y_max - y_min if y_max != y_min else 1.0
                
                # Escalar a un rango de -5 a 5 para mejor visualización
                for nodo in pos:
                    x_scaled = ((pos[nodo][0] - x_min) / x_range) * 10 - 5
                    y_scaled = ((pos[nodo][1] - y_min) / y_range) * 10 - 5
                    pos_tuplas[nodo] = (float(x_scaled), float(y_scaled))
            
            # Validar el grafo
            es_valido, errores_validacion = ValidadorGrafo.validar_grafo(G)
            if not es_valido:
                errores.extend(errores_validacion)
                return None, None, errores
            
            return G, pos_tuplas, errores
            
        except FileNotFoundError:
            errores.append("No se encontró el archivo especificado")
            return None, None, errores
        except KeyError as e:
            errores.append(f"Error en la estructura del archivo Excel: {str(e)}")
            errores.append("Asegúrate de que el archivo tenga las hojas 'NODOS' y 'ARCOS'")
            return None, None, errores
        except Exception as e:
            errores.append(f"Error inesperado cargando el archivo: {str(e)}")
            return None, None, errores
    
    @staticmethod
    def crear_grafo_ejemplo() -> Tuple[nx.Graph, Dict]:
        """
        Crea un grafo de ejemplo para testing.
        
        Returns:
            Tuple[nx.Graph, Dict]: (grafo, posiciones)
        """
        G = nx.Graph()
        
        # Agregar nodos
        nodos = ['A', 'B', 'C', 'D', 'E']
        G.add_nodes_from(nodos)
        
        # Agregar arcos con pesos
        arcos = [
            ('A', 'B', 50.0),
            ('A', 'C', 60.0),
            ('B', 'D', 40.0),
            ('C', 'D', 45.0),
            ('C', 'E', 55.0),
            ('D', 'E', 35.0)
        ]
        
        for origen, destino, peso in arcos:
            G.add_edge(origen, destino, weight=peso)
        
        # Calcular posiciones usando spring_layout
        pos = nx.spring_layout(G, seed=42, k=2, iterations=50)
        
        # Normalizar y escalar las posiciones para mejor visualización
        pos_tuplas = {}
        if pos:
            # Obtener los valores mínimos y máximos
            x_values = [pos[nodo][0] for nodo in pos]
            y_values = [pos[nodo][1] for nodo in pos]
            
            x_min, x_max = min(x_values), max(x_values)
            y_min, y_max = min(y_values), max(y_values)
            
            # Escalar a un rango más amplio para mejor visualización
            x_range = x_max - x_min if x_max != x_min else 1.0
            y_range = y_max - y_min if y_max != y_min else 1.0
            
            # Escalar a un rango de -5 a 5 para mejor visualización
            for nodo in pos:
                x_scaled = ((pos[nodo][0] - x_min) / x_range) * 10 - 5
                y_scaled = ((pos[nodo][1] - y_min) / y_range) * 10 - 5
                pos_tuplas[nodo] = (float(x_scaled), float(y_scaled))
        
        return G, pos_tuplas


class AnalizadorGrafo:
    """Clase para analizar propiedades de grafos."""
    
    @staticmethod
    def obtener_estadisticas_basicas(grafo: nx.Graph) -> Dict[str, Any]:
        """
        Obtiene estadísticas básicas del grafo.
        
        Args:
            grafo: Grafo de NetworkX
            
        Returns:
            Dict[str, Any]: Estadísticas del grafo
        """
        if not grafo:
            return {}
        
        # Estadísticas básicas
        num_nodos = len(grafo.nodes())
        num_arcos = len(grafo.edges())
        
        # Conectividad
        es_conectado = nx.is_connected(grafo)
        componentes = nx.number_connected_components(grafo)
        
        # Densidad
        densidad = nx.density(grafo)
        
        # Diámetro (solo si está conectado)
        diametro = nx.diameter(grafo) if es_conectado else None
        
        # Distancias de arcos
        distancias = [grafo[u][v].get('weight', 0) for u, v in grafo.edges()]
        distancia_promedio = np.mean(distancias) if distancias else 0
        distancia_min = np.min(distancias) if distancias else 0
        distancia_max = np.max(distancias) if distancias else 0
        
        return {
            'num_nodos': num_nodos,
            'num_arcos': num_arcos,
            'es_conectado': es_conectado,
            'num_componentes': componentes,
            'densidad': densidad,
            'diametro': diametro,
            'distancia_promedio': distancia_promedio,
            'distancia_minima': distancia_min,
            'distancia_maxima': distancia_max
        }
    
    @staticmethod
    def obtener_nodos_centrales(grafo: nx.Graph, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Obtiene los nodos más centrales del grafo.
        
        Args:
            grafo: Grafo de NetworkX
            top_k: Número de nodos centrales a retornar
            
        Returns:
            List[Tuple[str, float]]: Lista de (nodo, centralidad) ordenada por centralidad
        """
        if not grafo or len(grafo.nodes()) == 0:
            return []
        
        # Calcular centralidad de grado
        centralidad = nx.degree_centrality(grafo)
        
        # Ordenar por centralidad (descendente)
        nodos_centrales = sorted(centralidad.items(), key=lambda x: x[1], reverse=True)
        
        return nodos_centrales[:top_k]
    
    @staticmethod
    def calcular_rutas_todas_parejas(grafo: nx.Graph) -> Dict[Tuple[str, str], List[str]]:
        """
        Calcula las rutas más cortas entre todos los pares de nodos.
        
        Args:
            grafo: Grafo de NetworkX
            
        Returns:
            Dict[Tuple[str, str], List[str]]: Diccionario de rutas por par de nodos
        """
        if not grafo:
            return {}
        
        rutas = {}
        nodos = list(grafo.nodes())
        
        for origen in nodos:
            for destino in nodos:
                if origen != destino:
                    try:
                        ruta = nx.shortest_path(grafo, origen, destino)
                        rutas[(origen, destino)] = ruta
                    except nx.NetworkXNoPath:
                        # No hay camino entre estos nodos
                        continue
        
        return rutas


class UtilidadesGrafo:
    """Clase con utilidades para trabajar con grafos."""
    
    @staticmethod
    def obtener_coordenada_nodo(posiciones: Dict[str, Tuple[float, float]], 
                                nodo_id: str) -> Tuple[float, float]:
        """
        Obtiene las coordenadas reales del nodo en el grafo.
        
        Args:
            posiciones: Diccionario de posiciones de nodos
            nodo_id: Identificador del nodo
            
        Returns:
            Tuple[float, float]: Coordenadas (x, y) del nodo
        """
        if posiciones and nodo_id in posiciones:
            return posiciones[nodo_id]
        return (0.0, 0.0)  # Fallback
    
    @staticmethod
    def obtener_distancia_arco(grafo: nx.Graph, origen: str, destino: str, 
                              distancia_por_defecto: float = 50.0) -> float:
        """
        Obtiene la distancia real del arco entre dos nodos.
        
        Args:
            grafo: Grafo de NetworkX
            origen: Nodo origen
            destino: Nodo destino
            distancia_por_defecto: Distancia por defecto si no hay arco
            
        Returns:
            float: Distancia del arco
        """
        if not grafo:
            return distancia_por_defecto
        
        try:
            if grafo.has_edge(origen, destino):
                return grafo[origen][destino].get('weight', distancia_por_defecto)
            else:
                # Si no hay arco directo, calcular distancia euclidiana
                pos_origen = UtilidadesGrafo.obtener_coordenada_nodo(
                    dict(grafo.nodes(data='pos', default=(0, 0))), origen)
                pos_destino = UtilidadesGrafo.obtener_coordenada_nodo(
                    dict(grafo.nodes(data='pos', default=(0, 0))), destino)
                return np.sqrt((pos_destino[0] - pos_origen[0])**2 + 
                              (pos_destino[1] - pos_origen[1])**2)
        except Exception:
            return distancia_por_defecto
    
    @staticmethod
    def calcular_rutas_dinamicas(grafo: nx.Graph) -> List[Tuple[str, str]]:
        """
        Calcula todas las rutas posibles entre nodos del grafo.
        
        Args:
            grafo: Grafo de NetworkX
            
        Returns:
            List[Tuple[str, str]]: Lista de rutas (origen, destino)
        """
        if not grafo:
            return []
        
        rutas = []
        nodos = list(grafo.nodes())
        
        # Calcular rutas entre todos los pares de nodos
        for origen in nodos:
            for destino in nodos:
                if origen != destino:
                    # Verificar si hay conexión directa o ruta
                    try:
                        if grafo.has_edge(origen, destino):
                            # Conexión directa
                            rutas.append((origen, destino))
                        else:
                            # Verificar si hay ruta usando pathfinding
                            if nx.has_path(grafo, origen, destino):
                                rutas.append((origen, destino))
                    except:
                        continue
        
        return rutas
    
    @staticmethod
    def asignar_colores_nodos(nodos: List[str]) -> Dict[str, str]:
        """
        Asigna colores únicos para cada nodo.
        
        Args:
            nodos: Lista de identificadores de nodos
            
        Returns:
            Dict[str, str]: Mapeo de nodo a color
        """
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
        
        colores_nodos = {}
        for i, nodo in enumerate(nodos):
            color = colores_base[i % len(colores_base)]
            colores_nodos[nodo] = color
        
        return colores_nodos


class GestorGrafo:
    """
    Gestor principal para manejar grafos en la simulación.
    
    Esta clase orquesta todas las operaciones relacionadas con grafos
    y mantiene el estado del grafo actual.
    """
    
    def __init__(self):
        """Inicializa el gestor de grafo."""
        self.grafo_actual: Optional[nx.Graph] = None
        self.posiciones_actuales: Optional[Dict[str, Tuple[float, float]]] = None
        self.colores_nodos: Dict[str, str] = {}
        self.rutas_dinamicas: List[Tuple[str, str]] = []
        self.estadisticas: Dict[str, Any] = {}
    
    def cargar_grafo_desde_excel(self, archivo: str) -> Tuple[bool, List[str]]:
        """
        Carga un grafo desde un archivo Excel.
        
        Args:
            archivo: Ruta del archivo Excel
            
        Returns:
            Tuple[bool, List[str]]: (exitoso, lista_de_errores)
        """
        grafo, posiciones, errores = CargadorGrafo.cargar_desde_excel(archivo)
        
        if grafo and posiciones:
            self.grafo_actual = grafo
            self.posiciones_actuales = posiciones
            self._inicializar_grafo()
            return True, errores
        else:
            return False, errores
    
    def crear_grafo_ejemplo(self):
        """Crea un grafo de ejemplo para testing."""
        self.grafo_actual, self.posiciones_actuales = CargadorGrafo.crear_grafo_ejemplo()
        self._inicializar_grafo()
    
    def _inicializar_grafo(self):
        """Inicializa el grafo cargado."""
        if not self.grafo_actual or not self.posiciones_actuales:
            return
        
        # Asignar colores a los nodos
        nodos = list(self.grafo_actual.nodes())
        self.colores_nodos = UtilidadesGrafo.asignar_colores_nodos(nodos)
        
        # Calcular rutas dinámicas
        self.rutas_dinamicas = UtilidadesGrafo.calcular_rutas_dinamicas(self.grafo_actual)
        
        # Calcular estadísticas
        self.estadisticas = AnalizadorGrafo.obtener_estadisticas_basicas(self.grafo_actual)
    
    def obtener_grafo(self) -> Optional[nx.Graph]:
        """Retorna el grafo actual."""
        return self.grafo_actual
    
    def obtener_posiciones(self) -> Optional[Dict[str, Tuple[float, float]]]:
        """Retorna las posiciones actuales."""
        return self.posiciones_actuales
    
    def obtener_colores_nodos(self) -> Dict[str, str]:
        """Retorna el mapeo de colores por nodo."""
        return self.colores_nodos.copy()
    
    def obtener_rutas_dinamicas(self) -> List[Tuple[str, str]]:
        """Retorna las rutas dinámicas calculadas."""
        return self.rutas_dinamicas.copy()
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Retorna las estadísticas del grafo."""
        return self.estadisticas.copy()
    
    def limpiar_grafo(self):
        """Limpia el grafo actual."""
        self.grafo_actual = None
        self.posiciones_actuales = None
        self.colores_nodos.clear()
        self.rutas_dinamicas.clear()
        self.estadisticas.clear()
    
    def tiene_grafo_cargado(self) -> bool:
        """Verifica si hay un grafo cargado."""
        return self.grafo_actual is not None
    
    def __str__(self) -> str:
        """Representación string del gestor."""
        if self.grafo_actual:
            return f"GestorGrafo({len(self.grafo_actual.nodes())} nodos, {len(self.grafo_actual.edges())} arcos)"
        else:
            return "GestorGrafo(sin grafo cargado)"
