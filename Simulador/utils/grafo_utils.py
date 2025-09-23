"""
Utilidades para manejo de grafos NetworkX.

Este módulo contiene funciones auxiliares para trabajar con grafos
en el contexto de la simulación de ciclorutas.
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd


class GrafoUtils:
    """Utilidades para manejo de grafos"""
    
    @staticmethod
    def validar_grafo(grafo: nx.Graph) -> bool:
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
    
    @staticmethod
    def calcular_posiciones_grafo(grafo: nx.Graph, seed: int = 42) -> Dict:
        """Calcula posiciones para visualización del grafo"""
        return nx.spring_layout(grafo, seed=seed, k=2, iterations=50)
    
    @staticmethod
    def obtener_coordenada_nodo(pos_grafo: Dict, nodo_id: str) -> Tuple[float, float]:
        """Obtiene las coordenadas reales del nodo en el grafo"""
        if pos_grafo and nodo_id in pos_grafo:
            coords = pos_grafo[nodo_id]
            # Asegurar que sea una tupla de floats
            if hasattr(coords, '__iter__') and len(coords) == 2:
                return (float(coords[0]), float(coords[1]))
            else:
                return (0.0, 0.0)
        return (0.0, 0.0)  # Fallback
    
    @staticmethod
    def obtener_distancia_arco(grafo: nx.Graph, origen: str, destino: str) -> float:
        """Obtiene la distancia real del arco entre dos nodos para simulación"""
        if not grafo:
            return 50.0  # Distancia por defecto
        
        try:
            if grafo.has_edge(origen, destino):
                # SIEMPRE priorizar distancia_real para simulación (tiempos realistas)
                if 'distancia_real' in grafo[origen][destino]:
                    return grafo[origen][destino]['distancia_real']
                
                # Fallback: usar distancia original si no hay distancia_real
                elif 'distancia' in grafo[origen][destino]:
                    return grafo[origen][destino]['distancia']
                
                # Fallback: usar weight si es una distancia real (no normalizada)
                else:
                    peso = grafo[origen][destino].get('weight', 50.0)
                    if peso >= 10.0:  # Es distancia real directa
                        return peso
                    else:  # Es peso compuesto normalizado, convertir a distancia real
                        # Convertir peso compuesto (0-1) a distancia real (20-200m)
                        return 20 + (1 - peso) * 180
            else:
                # Si no hay arco directo, calcular distancia euclidiana
                pos_origen = grafo.nodes[origen].get('pos', (0, 0))
                pos_destino = grafo.nodes[destino].get('pos', (0, 0))
                return np.sqrt((pos_destino[0] - pos_origen[0])**2 + (pos_destino[1] - pos_origen[1])**2)
        except Exception:
            return 50.0  # Fallback
    
    @staticmethod
    def obtener_atributos_arco(grafo: nx.Graph, origen: str, destino: str) -> dict:
        """Obtiene todos los atributos del arco entre dos nodos"""
        if not grafo or not grafo.has_edge(origen, destino):
            return {}
        
        try:
            return dict(grafo[origen][destino])
        except Exception:
            return {}
    
    @staticmethod
    def calcular_velocidad_ajustada(velocidad_base: float, atributos_arco: dict, 
                                   velocidad_min_config: float = None, 
                                   velocidad_max_config: float = None) -> float:
        """Calcula la velocidad ajustada SOLO por inclinación
        
        Args:
            velocidad_base: Velocidad base del ciclista (m/s)
            atributos_arco: Atributos del arco (solo inclinación afecta velocidad)
            velocidad_min_config: Velocidad mínima configurada (m/s)
            velocidad_max_config: Velocidad máxima configurada (m/s)
        
        Returns:
            Velocidad ajustada solo por inclinación (reducción porcentual)
        """
        if not atributos_arco:
            return velocidad_base
        
        # Solo la inclinación afecta la velocidad
        factor_inclinacion = 1.0
        
        # Ajuste por inclinación: reducción porcentual directa
        if 'inclinacion' in atributos_arco:
            inclinacion = atributos_arco['inclinacion']
            # La inclinación ya viene como porcentaje directo (5 = 5%, 10 = 10%, etc.)
            # Limitar entre 0% y 50% para evitar reducciones excesivas
            porcentaje_reduccion = max(0, min(50, inclinacion))
            factor_inclinacion = 1.0 - (porcentaje_reduccion / 100.0)
        
        # Aplicar solo el factor de inclinación
        velocidad_ajustada = velocidad_base * factor_inclinacion
        
        # Limitar la velocidad ajustada respetando la configuración del usuario
        if velocidad_min_config is not None and velocidad_max_config is not None:
            # Usar límites de configuración si están disponibles
            return max(velocidad_min_config, min(velocidad_max_config, velocidad_ajustada))
        else:
            # Fallback: usar límites relativos a la velocidad base
            return max(velocidad_base * 0.3, min(velocidad_base * 1.0, velocidad_ajustada))
    
    @staticmethod
    def calcular_factor_tiempo_desplazamiento(atributos_arco: dict) -> float:
        """Calcula el factor de tiempo de desplazamiento basado en seguridad e iluminación
        
        Args:
            atributos_arco: Atributos del arco (seguridad, luminosidad)
        
        Returns:
            Factor multiplicador para el tiempo de desplazamiento (>1 = más lento, <1 = más rápido)
        """
        if not atributos_arco:
            return 1.0
        
        # Factores de ajuste para tiempo de desplazamiento
        factor_seguridad = 1.0
        factor_luminosidad = 1.0
        
        # Ajuste por seguridad (valores más bajos = menos confianza = más tiempo)
        if 'seguridad' in atributos_arco:
            seguridad = atributos_arco['seguridad']
            # Seguridad 5-9, factor 1.3-0.8 (menos seguridad = más tiempo)
            factor_seguridad = 1.3 - (seguridad - 5) * 0.125
        
        # Ajuste por luminosidad (valores más bajos = menos visibilidad = más tiempo)
        if 'luminosidad' in atributos_arco:
            luminosidad = atributos_arco['luminosidad']
            # Luminosidad 4-8, factor 1.2-0.9 (menos luminosidad = más tiempo)
            factor_luminosidad = 1.2 - (luminosidad - 4) * 0.075
        
        # Aplicar ambos factores (multiplicativo)
        factor_tiempo = factor_seguridad * factor_luminosidad
        
        # Limitar el factor entre 0.5 y 2.0 (máximo 50% más rápido o 100% más lento)
        return max(0.5, min(2.0, factor_tiempo))
    
    @staticmethod
    def precalcular_rangos_atributos(grafo: nx.Graph) -> Dict[str, Tuple[float, float]]:
        """Pre-calcula los rangos de atributos del grafo completo"""
        rangos_atributos = {}
        atributos_valores = {}
        
        # Recopilar todos los valores una sola vez
        for edge in grafo.edges(data=True):
            for attr, valor in edge[2].items():
                if attr not in ['weight'] and isinstance(valor, (int, float)):
                    if attr not in atributos_valores:
                        atributos_valores[attr] = []
                    atributos_valores[attr].append(valor)
        
        # Calcular rangos una sola vez
        for attr, valores in atributos_valores.items():
            if valores:
                rangos_atributos[attr] = (min(valores), max(valores))
        
        return rangos_atributos
    
    @staticmethod
    def calcular_peso_compuesto_perfil(atributos_arco: dict, perfil_ciclista: dict, 
                                     rangos_atributos: Dict[str, Tuple[float, float]]) -> float:
        """Calcula peso compuesto dinámicamente usando los pesos del perfil del ciclista"""
        peso = 0.0
        
        for attr, valor in atributos_arco.items():
            # Solo procesar atributos que están en el perfil del ciclista
            if attr in perfil_ciclista['pesos'] and attr in rangos_atributos:
                min_val, max_val = rangos_atributos[attr]
                
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
    
    @staticmethod
    def crear_grafo_desde_excel(archivo_excel: str) -> Tuple[nx.Graph, Dict, Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """Crea un grafo NetworkX desde un archivo Excel"""
        # Leer datos del Excel
        nodos_df = pd.read_excel(archivo_excel, sheet_name="NODOS", engine="openpyxl")
        arcos_df = pd.read_excel(archivo_excel, sheet_name="ARCOS", engine="openpyxl")
        
        # Verificar si hay hojas adicionales
        excel_file = pd.ExcelFile(archivo_excel)
        perfiles_df = None
        rutas_df = None
        
        if "PERFILES" in excel_file.sheet_names:
            perfiles_df = pd.read_excel(archivo_excel, sheet_name="PERFILES", engine="openpyxl")
        
        if "RUTAS" in excel_file.sheet_names:
            rutas_df = pd.read_excel(archivo_excel, sheet_name="RUTAS", engine="openpyxl")
        
        # Crear grafo NetworkX
        G = nx.Graph()
        
        # Agregar nodos
        for nodo in nodos_df.iloc[:, 0]:
            G.add_node(nodo)
        
        # Verificar atributos disponibles en arcos
        atributos_disponibles = []
        for attr in ['DISTANCIA', 'SEGURIDAD', 'LUMINOSIDAD', 'INCLINACION']:
            if attr in arcos_df.columns:
                atributos_disponibles.append(attr)
        
        # Agregar arcos con todos los atributos
        for _, fila in arcos_df.iterrows():
            origen, destino = fila[0], fila[1]
            
            # Crear diccionario de atributos
            atributos = {}
            for col in arcos_df.columns:
                if col not in ['ORIGEN', 'DESTINO']:
                    atributos[col.lower()] = fila[col]
            
            # Configurar pesos para diferentes usos
            if 'distancia' in atributos:
                atributos['weight'] = atributos['distancia']
            
            # Asegurar que siempre tengamos distancia_real para simulación
            if 'distancia_real' not in atributos and 'distancia' in atributos:
                atributos['distancia_real'] = atributos['distancia']
            
            G.add_edge(origen, destino, **atributos)
        
        # Calcular posiciones del grafo
        pos = GrafoUtils.calcular_posiciones_grafo(G)
        
        return G, pos, perfiles_df, rutas_df
    
    @staticmethod
    def obtener_ruta_optima(grafo: nx.Graph, origen: str, destino: str, 
                          perfil_ciclista: dict, rangos_atributos: Dict) -> Optional[List[str]]:
        """Obtiene la ruta óptima para un perfil de ciclista específico"""
        try:
            # Crear grafo temporal con pesos ajustados al perfil
            grafo_temp = grafo.copy()
            
            # Recalcular pesos basados en el perfil
            for edge in grafo_temp.edges(data=True):
                origen_edge, destino_edge, datos = edge
                atributos_arco = {k: v for k, v in datos.items() if k not in ['weight', 'distancia_real']}
                
                nuevo_peso = GrafoUtils.calcular_peso_compuesto_perfil(
                    atributos_arco, perfil_ciclista, rangos_atributos
                )
                grafo_temp[origen_edge][destino_edge]['weight'] = nuevo_peso
            
            # Encontrar ruta óptima
            return nx.shortest_path(grafo_temp, origen, destino, weight='weight')
            
        except nx.NetworkXNoPath:
            return None
        except Exception:
            return None
