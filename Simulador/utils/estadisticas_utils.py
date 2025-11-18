"""
Módulo de utilidades para el cálculo de estadísticas del simulador.

Este módulo contiene toda la lógica de cálculo de estadísticas,
desacoplada del simulador principal para mejor mantenibilidad.
"""

import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter


class EstadisticasUtils:
    """Clase utilitaria para el cálculo de estadísticas del simulador"""
    
    @staticmethod
    def calcular_estadisticas_basicas(coordenadas: List, velocidades: List, 
                                     estado_ciclistas: Dict, config) -> Dict:
        """Calcula estadísticas básicas de la simulación"""
        # Contar ciclistas por estado
        ciclistas_activos = sum(1 for estado in estado_ciclistas.values() if estado == 'activo')
        ciclistas_completados = sum(1 for estado in estado_ciclistas.values() if estado == 'completado')
        
        # Obtener velocidades de TODOS los ciclistas (activos y completados)
        velocidades_todos = []
        for i, velocidad in enumerate(velocidades):
            if i in estado_ciclistas and estado_ciclistas[i] in ['activo', 'completado']:
                velocidades_todos.append(velocidad)
        
        return {
            'total_ciclistas': len(coordenadas),
            'ciclistas_activos': ciclistas_activos,
            'ciclistas_completados': ciclistas_completados,
            'velocidad_promedio': np.mean(velocidades_todos) if velocidades_todos else 0,
            'velocidad_minima': min(velocidades_todos) if velocidades_todos else 0,
            'velocidad_maxima': max(velocidades_todos) if velocidades_todos else 0,
            'usando_grafo_real': hasattr(config, 'usar_grafo_real') and config.usar_grafo_real,
            'duracion_simulacion': getattr(config, 'duracion_simulacion', 0)
        }
    
    @staticmethod
    def calcular_estadisticas_grafo(grafo: Optional[nx.Graph]) -> Dict:
        """Calcula estadísticas relacionadas con el grafo"""
        if not grafo:
            return {}
        
        stats = {
            'grafo_nodos': len(grafo.nodes()),
            'grafo_arcos': len(grafo.edges()),
            'grafo_conectado': nx.is_connected(grafo)
        }
        
        # Calcular distancia promedio de arcos
        if grafo.edges():
            distancias = [grafo[u][v].get('weight', 0) for u, v in grafo.edges()]
            stats['distancia_promedio_arcos'] = np.mean(distancias) if distancias else 0
        
        return stats
    
    @staticmethod
    def calcular_estadisticas_rutas(rutas_utilizadas: Dict, rutas_por_ciclista: Dict, arcos_utilizados: Dict = None) -> Dict:
        """Calcula estadísticas relacionadas con las rutas"""
        stats = {
            'rutas_utilizadas': len(rutas_utilizadas),
            'total_viajes': sum(rutas_utilizadas.values()) if rutas_utilizadas else 0,
            'ruta_mas_usada': EstadisticasUtils._obtener_ruta_mas_usada(rutas_utilizadas),
            'rutas_por_frecuencia': EstadisticasUtils._obtener_rutas_por_frecuencia(rutas_utilizadas)
        }
        
        # Agregar estadística del tramo más concurrido si hay datos de arcos
        if arcos_utilizados:
            stats['tramo_mas_concurrido'] = EstadisticasUtils._obtener_tramo_mas_concurrido(arcos_utilizados)
        else:
            stats['tramo_mas_concurrido'] = 'N/A'
        
        return stats
    
    @staticmethod
    def calcular_estadisticas_nodos(ciclistas_por_nodo: Dict) -> Dict:
        """Calcula estadísticas relacionadas con los nodos"""
        return {
            'ciclistas_por_nodo': ciclistas_por_nodo.copy(),
            'nodo_mas_activo': EstadisticasUtils._obtener_nodo_mas_activo(ciclistas_por_nodo)
        }
    
    @staticmethod
    def calcular_estadisticas_perfiles(contador_perfiles: Dict) -> Dict:
        """Calcula estadísticas relacionadas con los perfiles de ciclistas"""
        return {
            'distribucion_perfiles': contador_perfiles.copy(),
            'total_ciclistas_con_perfil': sum(contador_perfiles.values()),
            'perfil_mas_usado': EstadisticasUtils._obtener_perfil_mas_usado(contador_perfiles)
        }
    
    @staticmethod
    def calcular_estadisticas_pool(estadisticas_persistentes: Dict, pool_estadisticas: Dict) -> Dict:
        """Calcula estadísticas del pool de ciclistas y memoria"""
        return {
            'estadisticas_persistentes': estadisticas_persistentes.copy(),
            'pool_estadisticas': pool_estadisticas
        }
    
    @staticmethod
    def calcular_ciclistas_por_tramo_tiempo_real(simulador) -> Dict[str, int]:
        """Calcula cuántos ciclistas están en cada tramo en tiempo real"""
        if not hasattr(simulador, 'bicicletas_en_arco'):
            return {}
        
        ciclistas_por_tramo = {}
        for arco_str, conjunto_ciclistas in simulador.bicicletas_en_arco.items():
            if conjunto_ciclistas:  # Solo incluir tramos con ciclistas
                ciclistas_por_tramo[arco_str] = len(conjunto_ciclistas)
        
        return ciclistas_por_tramo
    
    @staticmethod
    def calcular_estadisticas_completas(simulador) -> Dict:
        """Calcula todas las estadísticas del simulador de forma integrada"""
        stats = {}
        
        # Estadísticas básicas
        stats.update(EstadisticasUtils.calcular_estadisticas_basicas(
            simulador.coordenadas, 
            simulador.velocidades, 
            simulador.estado_ciclistas, 
            simulador.config
        ))
        
        # Estadísticas del grafo
        if simulador.usar_grafo_real and simulador.grafo:
            stats.update(EstadisticasUtils.calcular_estadisticas_grafo(simulador.grafo))
            
            # Estadísticas de distribuciones
            if hasattr(simulador, 'gestor_distribuciones'):
                stats_distribuciones = simulador.gestor_distribuciones.obtener_estadisticas()
                stats.update(stats_distribuciones)
        
        # Estadísticas de rutas
        stats.update(EstadisticasUtils.calcular_estadisticas_rutas(
            simulador.rutas_utilizadas, 
            simulador.rutas_por_ciclista,
            simulador.arcos_utilizados
        ))
        
        # Estadísticas de nodos
        stats.update(EstadisticasUtils.calcular_estadisticas_nodos(
            simulador.ciclistas_por_nodo
        ))
        
        # Estadísticas del pool y memoria
        stats.update(EstadisticasUtils.calcular_estadisticas_pool(
            simulador.estadisticas_persistentes,
            simulador.pool_ciclistas.obtener_estadisticas()
        ))
        
        # Estadísticas de perfiles
        stats.update(EstadisticasUtils.calcular_estadisticas_perfiles(
            simulador.contador_perfiles
        ))
        
        # Estadísticas de ciclistas por tramo en tiempo real
        stats['ciclistas_por_tramo_tiempo_real'] = EstadisticasUtils.calcular_ciclistas_por_tramo_tiempo_real(simulador)
        
        return stats
    
    @staticmethod
    def _obtener_ruta_mas_usada(rutas_utilizadas: Dict) -> str:
        """Obtiene la ruta más utilizada"""
        if not rutas_utilizadas:
            return "N/A"
        
        ruta_mas_usada = max(rutas_utilizadas.items(), key=lambda x: x[1])
        return f"{ruta_mas_usada[0]} ({ruta_mas_usada[1]} viajes)"
    
    @staticmethod
    def _obtener_tramo_mas_concurrido(arcos_utilizados: Dict) -> str:
        """Obtiene el tramo/arco más concurrido"""
        if not arcos_utilizados:
            return "N/A"
        
        tramo_mas_concurrido = max(arcos_utilizados.items(), key=lambda x: x[1])
        return f"{tramo_mas_concurrido[0]} ({tramo_mas_concurrido[1]} ciclistas)"
    
    @staticmethod
    def _obtener_rutas_por_frecuencia(rutas_utilizadas: Dict) -> List:
        """Obtiene las rutas ordenadas por frecuencia de uso"""
        if not rutas_utilizadas:
            return []
        
        # Ordenar rutas por frecuencia (descendente)
        rutas_ordenadas = sorted(rutas_utilizadas.items(), key=lambda x: x[1], reverse=True)
        
        # Retornar las top 5 rutas
        return rutas_ordenadas[:5]
    
    @staticmethod
    def _obtener_nodo_mas_activo(ciclistas_por_nodo: Dict) -> str:
        """Obtiene el nodo que ha generado más ciclistas"""
        if not ciclistas_por_nodo:
            return "N/A"
        
        nodo_mas_activo = max(ciclistas_por_nodo.items(), key=lambda x: x[1])
        return f"Nodo {nodo_mas_activo[0]} ({nodo_mas_activo[1]} ciclistas)"
    
    @staticmethod
    def _obtener_perfil_mas_usado(contador_perfiles: Dict) -> str:
        """Obtiene el perfil más utilizado"""
        if not contador_perfiles:
            return "N/A"
        
        perfil_mas_usado = max(contador_perfiles.items(), key=lambda x: x[1])
        total_ciclistas = sum(contador_perfiles.values())
        porcentaje = (perfil_mas_usado[1] / total_ciclistas) * 100 if total_ciclistas > 0 else 0
        
        return f"Perfil {perfil_mas_usado[0]} ({perfil_mas_usado[1]} ciclistas, {porcentaje:.1f}%)"
    
    @staticmethod
    def calcular_estadisticas_tiempo_real(simulador) -> Dict:
        """Calcula estadísticas en tiempo real para visualización"""
        ciclistas_activos = simulador.obtener_ciclistas_activos()
        
        return {
            'tiempo_actual': simulador.tiempo_actual,
            'estado_simulacion': simulador.estado,
            'ciclistas_activos_count': len(ciclistas_activos['coordenadas']),
            'velocidad_promedio_activos': np.mean(ciclistas_activos['velocidades']) if ciclistas_activos['velocidades'] else 0,
            'rutas_unicas_activas': len(set(ciclistas_activos['ruta_actual']))
        }
    
    @staticmethod
    def generar_reporte_detallado(simulador) -> str:
        """Genera un reporte detallado de la simulación"""
        stats = EstadisticasUtils.calcular_estadisticas_completas(simulador)
        
        reporte = f"""
=== REPORTE DETALLADO DE SIMULACIÓN ===
Tiempo de simulación: {stats.get('tiempo_actual', 0):.2f}s / {stats.get('duracion_simulacion', 0):.2f}s

CICLISTAS:
- Total creados: {stats.get('total_ciclistas', 0)}
- Activos: {stats.get('ciclistas_activos', 0)}
- Completados: {stats.get('ciclistas_completados', 0)}

VELOCIDADES:
- Promedio: {stats.get('velocidad_promedio', 0):.2f} km/h
- Mínima: {stats.get('velocidad_minima', 0):.2f} km/h
- Máxima: {stats.get('velocidad_maxima', 0):.2f} km/h

RUTAS:
- Rutas únicas utilizadas: {stats.get('rutas_utilizadas', 0)}
- Total de viajes: {stats.get('total_viajes', 0)}
- Ruta más usada: {stats.get('ruta_mas_usada', 'N/A')}

GRAFO:
- Nodos: {stats.get('grafo_nodos', 0)}
- Arcos: {stats.get('grafo_arcos', 0)}
- Conectado: {stats.get('grafo_conectado', False)}
- Distancia promedio arcos: {stats.get('distancia_promedio_arcos', 0):.2f}

PERFILES:
- Total con perfil: {stats.get('total_ciclistas_con_perfil', 0)}
- Perfil más usado: {stats.get('perfil_mas_usado', 'N/A')}
        """
        
        return reporte.strip()
