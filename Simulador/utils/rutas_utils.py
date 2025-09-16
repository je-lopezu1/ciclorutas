"""
Utilidades para cálculo de rutas inteligentes.

Este módulo contiene funciones para calcular rutas óptimas
basadas en perfiles de ciclistas y atributos del grafo.
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from scipy.optimize import minimize
import heapq


class RutasUtils:
    """Utilidades para cálculo de rutas inteligentes"""
    
    @staticmethod
    def calcular_ruta_optima(grafo: nx.Graph, origen: str, destino: str, 
                           perfil: Dict[str, float], rangos_atributos: Dict[str, Tuple[float, float]]) -> List[str]:
        """
        Calcula la ruta óptima basada en el perfil del ciclista y atributos del grafo.
        
        Args:
            grafo: Grafo NetworkX
            origen: Nodo de origen
            destino: Nodo de destino
            perfil: Perfil del ciclista con pesos para cada atributo
            rangos_atributos: Rangos normalizados de atributos del grafo
        
        Returns:
            Lista de nodos que forman la ruta óptima
        """
        try:
            # Verificar que los nodos existen
            if origen not in grafo.nodes() or destino not in grafo.nodes():
                return []
            
            # Si origen y destino son iguales
            if origen == destino:
                return [origen]
            
            # Calcular pesos compuestos para cada arco
            pesos_compuestos = RutasUtils._calcular_pesos_compuestos(
                grafo, perfil, rangos_atributos
            )
            
            # Crear grafo temporal con pesos compuestos
            G_temp = grafo.copy()
            for (u, v), peso in pesos_compuestos.items():
                G_temp[u][v]['weight'] = peso
            
            # Calcular ruta usando Dijkstra
            try:
                ruta = nx.shortest_path(G_temp, origen, destino, weight='weight')
                return ruta
            except nx.NetworkXNoPath:
                # Si no hay camino, intentar con ruta más simple
                return RutasUtils._calcular_ruta_simple(grafo, origen, destino)
                
        except Exception as e:
            print(f"⚠️ Error calculando ruta óptima: {e}")
            return RutasUtils._calcular_ruta_simple(grafo, origen, destino)
    
    @staticmethod
    def _calcular_pesos_compuestos(grafo: nx.Graph, perfil: Dict[str, float], 
                                 rangos_atributos: Dict[str, Tuple[float, float]]) -> Dict[Tuple[str, str], float]:
        """Calcula pesos compuestos para cada arco basado en el perfil"""
        pesos_compuestos = {}
        
        for u, v in grafo.edges():
            atributos = grafo[u][v]
            peso_compuesto = 0.0
            
            # Peso base: distancia
            distancia = atributos.get('distancia', atributos.get('weight', 1.0))
            peso_compuesto += perfil.get('distancia', 0.4) * distancia
            
            # Atributos adicionales
            for atributo, peso_perfil in perfil.items():
                if atributo == 'distancia':
                    continue
                
                if atributo in atributos:
                    valor = atributos[atributo]
                    # Normalizar valor según rango
                    if atributo in rangos_atributos:
                        min_val, max_val = rangos_atributos[atributo]
                        if max_val > min_val:
                            valor_normalizado = (valor - min_val) / (max_val - min_val)
                        else:
                            valor_normalizado = 0.5
                    else:
                        valor_normalizado = valor / 10.0  # Asumir escala 0-10
                    
                    # Invertir para atributos positivos (mayor valor = menor peso)
                    if atributo in ['seguridad', 'luminosidad']:
                        valor_normalizado = 1.0 - valor_normalizado
                    
                    peso_compuesto += peso_perfil * valor_normalizado * distancia
            
            pesos_compuestos[(u, v)] = peso_compuesto
        
        return pesos_compuestos
    
    @staticmethod
    def _calcular_ruta_simple(grafo: nx.Graph, origen: str, destino: str) -> List[str]:
        """Calcula una ruta simple usando distancia mínima"""
        try:
            return nx.shortest_path(grafo, origen, destino)
        except nx.NetworkXNoPath:
            return []
    
    @staticmethod
    def calcular_rutas_alternativas(grafo: nx.Graph, origen: str, destino: str, 
                                  perfil: Dict[str, float], rangos_atributos: Dict[str, Tuple[float, float]], 
                                  num_alternativas: int = 3) -> List[List[str]]:
        """Calcula rutas alternativas para un par origen-destino"""
        rutas_alternativas = []
        
        try:
            # Ruta óptima
            ruta_optima = RutasUtils.calcular_ruta_optima(grafo, origen, destino, perfil, rangos_atributos)
            if ruta_optima:
                rutas_alternativas.append(ruta_optima)
            
            # Calcular rutas alternativas usando k-shortest paths
            if len(rutas_alternativas) < num_alternativas:
                try:
                    # Usar algoritmo de k-shortest paths
                    k_rutas = list(nx.shortest_simple_paths(grafo, origen, destino))
                    for ruta in k_rutas[:num_alternativas]:
                        if ruta not in rutas_alternativas:
                            rutas_alternativas.append(ruta)
                        if len(rutas_alternativas) >= num_alternativas:
                            break
                except:
                    pass
            
            # Si no hay suficientes rutas, generar variaciones
            if len(rutas_alternativas) < num_alternativas:
                rutas_alternativas.extend(
                    RutasUtils._generar_rutas_variaciones(grafo, origen, destino, num_alternativas - len(rutas_alternativas))
                )
            
            return rutas_alternativas[:num_alternativas]
            
        except Exception as e:
            print(f"⚠️ Error calculando rutas alternativas: {e}")
            return [ruta_optima] if ruta_optima else []
    
    @staticmethod
    def _generar_rutas_variaciones(grafo: nx.Graph, origen: str, destino: str, num_variaciones: int) -> List[List[str]]:
        """Genera variaciones de rutas para aumentar opciones"""
        variaciones = []
        
        try:
            # Intentar rutas con diferentes nodos intermedios
            nodos_intermedios = [n for n in grafo.nodes() if n not in [origen, destino]]
            
            for i, nodo_intermedio in enumerate(nodos_intermedios[:num_variaciones]):
                try:
                    ruta1 = nx.shortest_path(grafo, origen, nodo_intermedio)
                    ruta2 = nx.shortest_path(grafo, nodo_intermedio, destino)
                    
                    # Combinar rutas (sin duplicar nodo intermedio)
                    ruta_combinada = ruta1 + ruta2[1:]
                    if ruta_combinada not in variaciones:
                        variaciones.append(ruta_combinada)
                except:
                    continue
            
            return variaciones
            
        except Exception as e:
            print(f"⚠️ Error generando variaciones: {e}")
            return []
    
    @staticmethod
    def evaluar_calidad_ruta(grafo: nx.Graph, ruta: List[str], perfil: Dict[str, float], 
                           rangos_atributos: Dict[str, Tuple[float, float]]) -> Dict[str, float]:
        """Evalúa la calidad de una ruta según el perfil del ciclista"""
        if len(ruta) < 2:
            return {'distancia_total': 0, 'peso_compuesto': 0, 'calidad': 0}
        
        distancia_total = 0
        peso_compuesto = 0
        atributos_promedio = {}
        
        # Calcular métricas para cada segmento
        for i in range(len(ruta) - 1):
            u, v = ruta[i], ruta[i + 1]
            if grafo.has_edge(u, v):
                atributos = grafo[u][v]
                
                # Distancia
                distancia = atributos.get('distancia', atributos.get('weight', 1.0))
                distancia_total += distancia
                
                # Peso compuesto
                peso_segmento = perfil.get('distancia', 0.4) * distancia
                
                # Atributos adicionales
                for atributo, peso_perfil in perfil.items():
                    if atributo == 'distancia':
                        continue
                    
                    if atributo in atributos:
                        valor = atributos[atributo]
                        # Normalizar
                        if atributo in rangos_atributos:
                            min_val, max_val = rangos_atributos[atributo]
                            if max_val > min_val:
                                valor_normalizado = (valor - min_val) / (max_val - min_val)
                            else:
                                valor_normalizado = 0.5
                        else:
                            valor_normalizado = valor / 10.0
                        
                        # Invertir para atributos positivos
                        if atributo in ['seguridad', 'luminosidad']:
                            valor_normalizado = 1.0 - valor_normalizado
                        
                        peso_segmento += peso_perfil * valor_normalizado * distancia
                        
                        # Acumular para promedio
                        if atributo not in atributos_promedio:
                            atributos_promedio[atributo] = []
                        atributos_promedio[atributo].append(valor)
                
                peso_compuesto += peso_segmento
        
        # Calcular promedios
        for atributo in atributos_promedio:
            atributos_promedio[atributo] = np.mean(atributos_promedio[atributo])
        
        # Calcular calidad general (menor peso = mejor calidad)
        calidad = 1.0 / (1.0 + peso_compuesto) if peso_compuesto > 0 else 1.0
        
        return {
            'distancia_total': distancia_total,
            'peso_compuesto': peso_compuesto,
            'calidad': calidad,
            'atributos_promedio': atributos_promedio
        }
    
    @staticmethod
    def precalcular_rutas_por_perfil(grafo: nx.Graph, perfiles: List[Dict[str, float]], 
                                   rangos_atributos: Dict[str, Tuple[float, float]], 
                                   max_rutas_por_perfil: int = 100) -> Dict[int, Dict[Tuple[str, str], List[str]]]:
        """Precalcula rutas para cada perfil para optimizar rendimiento"""
        rutas_por_perfil = {}
        
        for perfil_id, perfil in enumerate(perfiles):
            rutas_perfil = {}
            nodos = list(grafo.nodes())
            
            # Calcular rutas para pares de nodos
            for i, origen in enumerate(nodos):
                for j, destino in enumerate(nodos):
                    if origen != destino:
                        ruta = RutasUtils.calcular_ruta_optima(grafo, origen, destino, perfil, rangos_atributos)
                        if ruta:
                            rutas_perfil[(origen, destino)] = ruta
                            
                            # Limitar número de rutas por perfil
                            if len(rutas_perfil) >= max_rutas_por_perfil:
                                break
                
                if len(rutas_perfil) >= max_rutas_por_perfil:
                    break
            
            rutas_por_perfil[perfil_id] = rutas_perfil
        
        return rutas_por_perfil
    
    @staticmethod
    def obtener_ruta_desde_cache(rutas_por_perfil: Dict[int, Dict[Tuple[str, str], List[str]]], 
                                perfil_id: int, origen: str, destino: str) -> Optional[List[str]]:
        """Obtiene una ruta desde el cache precalculado"""
        if perfil_id in rutas_por_perfil:
            return rutas_por_perfil[perfil_id].get((origen, destino))
        return None
