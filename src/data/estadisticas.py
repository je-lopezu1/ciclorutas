#!/usr/bin/env python3
"""
📈 MÓDULO DE ESTADÍSTICAS - SIMULADOR DE CICLORUTAS 📈

Este módulo contiene las clases y funciones para calcular y analizar
estadísticas de la simulación de ciclorutas.

Autor: Sistema de Simulación de Ciclorutas
Versión: 2.0 (Refactorizado)
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from collections import Counter
import networkx as nx


@dataclass
class EstadisticasSimulacion:
    """Clase para almacenar estadísticas de la simulación."""
    
    # Estadísticas básicas
    tiempo_actual: float = 0.0
    duracion_simulacion: float = 0.0
    
    # Estadísticas de ciclistas
    total_ciclistas: int = 0
    ciclistas_activos: int = 0
    ciclistas_completados: int = 0
    ciclistas_pausados: int = 0
    
    # Estadísticas de velocidad
    velocidad_promedio: float = 0.0
    velocidad_minima: float = 0.0
    velocidad_maxima: float = 0.0
    velocidad_desviacion: float = 0.0
    
    # Estadísticas de grafo
    grafo_nodos: int = 0
    grafo_arcos: int = 0
    grafo_conectado: bool = False
    distancia_promedio_arcos: float = 0.0
    
    # Estadísticas de distribuciones
    distribuciones_configuradas: int = 0
    tasa_arribo_promedio: float = 0.0
    
    # Estadísticas de rutas
    rutas_utilizadas: int = 0
    total_viajes: int = 0
    ruta_mas_usada: str = "N/A"
    
    # Estadísticas de nodos
    nodo_mas_activo: str = "N/A"
    ciclistas_por_nodo: Dict[str, int] = None
    
    def __post_init__(self):
        """Inicializa campos que no pueden ser None."""
        if self.ciclistas_por_nodo is None:
            self.ciclistas_por_nodo = {}


class CalculadorEstadisticas:
    """Clase para calcular estadísticas de la simulación."""
    
    @staticmethod
    def calcular_estadisticas_ciclistas(gestor_ciclistas: Any) -> Dict[str, Any]:
        """
        Calcula estadísticas de los ciclistas.
        
        Args:
            gestor_ciclistas: Gestor de ciclistas
            
        Returns:
            Dict[str, Any]: Estadísticas de ciclistas
        """
        if not gestor_ciclistas or len(gestor_ciclistas) == 0:
            return {
                'total_ciclistas': 0,
                'ciclistas_activos': 0,
                'ciclistas_completados': 0,
                'velocidad_promedio': 0,
                'velocidad_minima': 0,
                'velocidad_maxima': 0,
                'velocidad_desviacion': 0
            }
        
        # Obtener estadísticas del gestor
        stats_ciclistas = gestor_ciclistas.obtener_estadisticas_ciclistas()
        
        # Calcular estadísticas de velocidad
        velocidades = gestor_ciclistas.velocidades
        if velocidades:
            velocidades_array = np.array(velocidades)
            stats_ciclistas.update({
                'velocidad_desviacion': float(np.std(velocidades_array))
            })
        else:
            stats_ciclistas.update({
                'velocidad_desviacion': 0.0
            })
        
        return stats_ciclistas
    
    @staticmethod
    def calcular_estadisticas_grafo(gestor_grafo: Any) -> Dict[str, Any]:
        """
        Calcula estadísticas del grafo.
        
        Args:
            gestor_grafo: Gestor de grafo
            
        Returns:
            Dict[str, Any]: Estadísticas del grafo
        """
        if not gestor_grafo or not gestor_grafo.tiene_grafo_cargado():
            return {
                'grafo_nodos': 0,
                'grafo_arcos': 0,
                'grafo_conectado': False,
                'distancia_promedio_arcos': 0.0
            }
        
        return gestor_grafo.obtener_estadisticas()
    
    @staticmethod
    def calcular_estadisticas_distribuciones(gestor_distribuciones: Any) -> Dict[str, Any]:
        """
        Calcula estadísticas de las distribuciones.
        
        Args:
            gestor_distribuciones: Gestor de distribuciones
            
        Returns:
            Dict[str, Any]: Estadísticas de distribuciones
        """
        if not gestor_distribuciones or len(gestor_distribuciones) == 0:
            return {
                'distribuciones_configuradas': 0,
                'tasa_arribo_promedio': 0.0,
                'tipos_distribucion': {}
            }
        
        distribuciones = gestor_distribuciones.obtener_todas_distribuciones()
        
        # Contar tipos de distribución
        tipos_distribucion = {}
        tasas_promedio = []
        
        for nodo_id, config in distribuciones.items():
            tipo = config['tipo']
            tipos_distribucion[tipo] = tipos_distribucion.get(tipo, 0) + 1
            
            if tipo in ['exponencial', 'poisson']:
                tasas_promedio.append(config['parametros'].get('lambda', 0))
        
        return {
            'distribuciones_configuradas': len(distribuciones),
            'tasa_arribo_promedio': float(np.mean(tasas_promedio)) if tasas_promedio else 0.0,
            'tipos_distribucion': tipos_distribucion
        }
    
    @staticmethod
    def calcular_estadisticas_generacion(generador: Any) -> Dict[str, Any]:
        """
        Calcula estadísticas de la generación de ciclistas.
        
        Args:
            generador: Generador de ciclistas
            
        Returns:
            Dict[str, Any]: Estadísticas de generación
        """
        if not generador:
            return {
                'rutas_utilizadas': 0,
                'total_viajes': 0,
                'ruta_mas_usada': 'N/A',
                'nodo_mas_activo': 'N/A',
                'ciclistas_por_nodo': {},
                'rutas_por_frecuencia': []
            }
        
        return generador.obtener_estadisticas_generacion()


class AnalizadorRutas:
    """Clase para analizar patrones de rutas."""
    
    @staticmethod
    def analizar_patrones_rutas(rutas_utilizadas: Dict[str, int]) -> Dict[str, Any]:
        """
        Analiza patrones en las rutas utilizadas.
        
        Args:
            rutas_utilizadas: Diccionario de rutas y sus frecuencias
            
        Returns:
            Dict[str, Any]: Análisis de patrones de rutas
        """
        if not rutas_utilizadas:
            return {
                'ruta_mas_usada': 'N/A',
                'ruta_menos_usada': 'N/A',
                'diversidad_rutas': 0.0,
                'concentracion_trafico': 0.0,
                'rutas_top_5': []
            }
        
        # Ruta más y menos usada
        ruta_mas_usada = max(rutas_utilizadas.items(), key=lambda x: x[1])
        ruta_menos_usada = min(rutas_utilizadas.items(), key=lambda x: x[1])
        
        # Calcular diversidad (índice de Shannon)
        total_viajes = sum(rutas_utilizadas.values())
        probabilidades = [freq / total_viajes for freq in rutas_utilizadas.values()]
        diversidad = -sum(p * np.log2(p) for p in probabilidades if p > 0)
        
        # Calcular concentración de tráfico (porcentaje en la ruta más usada)
        concentracion = (ruta_mas_usada[1] / total_viajes) * 100
        
        # Top 5 rutas
        rutas_ordenadas = sorted(rutas_utilizadas.items(), key=lambda x: x[1], reverse=True)
        rutas_top_5 = rutas_ordenadas[:5]
        
        return {
            'ruta_mas_usada': f"{ruta_mas_usada[0]} ({ruta_mas_usada[1]} viajes)",
            'ruta_menos_usada': f"{ruta_menos_usada[0]} ({ruta_menos_usada[1]} viajes)",
            'diversidad_rutas': float(diversidad),
            'concentracion_trafico': float(concentracion),
            'rutas_top_5': rutas_top_5
        }
    
    @staticmethod
    def analizar_nodos_activos(ciclistas_por_nodo: Dict[str, int]) -> Dict[str, Any]:
        """
        Analiza la actividad de los nodos.
        
        Args:
            ciclistas_por_nodo: Diccionario de nodos y número de ciclistas
            
        Returns:
            Dict[str, Any]: Análisis de actividad de nodos
        """
        if not ciclistas_por_nodo:
            return {
                'nodo_mas_activo': 'N/A',
                'nodo_menos_activo': 'N/A',
                'distribucion_actividad': {},
                'concentracion_nodos': 0.0
            }
        
        # Nodo más y menos activo
        nodo_mas_activo = max(ciclistas_por_nodo.items(), key=lambda x: x[1])
        nodo_menos_activo = min(ciclistas_por_nodo.items(), key=lambda x: x[1])
        
        # Calcular concentración de actividad
        total_ciclistas = sum(ciclistas_por_nodo.values())
        concentracion = (nodo_mas_activo[1] / total_ciclistas) * 100
        
        # Distribución de actividad
        distribucion = dict(sorted(ciclistas_por_nodo.items(), key=lambda x: x[1], reverse=True))
        
        return {
            'nodo_mas_activo': f"Nodo {nodo_mas_activo[0]} ({nodo_mas_activo[1]} ciclistas)",
            'nodo_menos_activo': f"Nodo {nodo_menos_activo[0]} ({nodo_menos_activo[1]} ciclistas)",
            'distribucion_actividad': distribucion,
            'concentracion_nodos': float(concentracion)
        }


class AnalizadorRendimiento:
    """Clase para analizar el rendimiento de la simulación."""
    
    @staticmethod
    def calcular_metricas_rendimiento(estadisticas: EstadisticasSimulacion) -> Dict[str, Any]:
        """
        Calcula métricas de rendimiento de la simulación.
        
        Args:
            estadisticas: Estadísticas de la simulación
            
        Returns:
            Dict[str, Any]: Métricas de rendimiento
        """
        # Tasa de finalización
        if estadisticas.total_ciclistas > 0:
            tasa_finalizacion = (estadisticas.ciclistas_completados / estadisticas.total_ciclistas) * 100
        else:
            tasa_finalizacion = 0.0
        
        # Eficiencia de la red
        if estadisticas.grafo_arcos > 0 and estadisticas.total_viajes > 0:
            eficiencia_red = estadisticas.total_viajes / estadisticas.grafo_arcos
        else:
            eficiencia_red = 0.0
        
        # Densidad de tráfico
        if estadisticas.grafo_nodos > 0:
            densidad_trafico = estadisticas.ciclistas_activos / estadisticas.grafo_nodos
        else:
            densidad_trafico = 0.0
        
        # Velocidad promedio de procesamiento
        if estadisticas.tiempo_actual > 0:
            velocidad_procesamiento = estadisticas.total_ciclistas / estadisticas.tiempo_actual
        else:
            velocidad_procesamiento = 0.0
        
        return {
            'tasa_finalizacion': float(tasa_finalizacion),
            'eficiencia_red': float(eficiencia_red),
            'densidad_trafico': float(densidad_trafico),
            'velocidad_procesamiento': float(velocidad_procesamiento)
        }


class GeneradorReportes:
    """Clase para generar reportes de estadísticas."""
    
    @staticmethod
    def generar_reporte_resumen(estadisticas: EstadisticasSimulacion) -> str:
        """
        Genera un reporte resumen de las estadísticas.
        
        Args:
            estadisticas: Estadísticas de la simulación
            
        Returns:
            str: Reporte resumen en formato texto
        """
        reporte = []
        reporte.append("=" * 60)
        reporte.append("📊 REPORTE DE ESTADÍSTICAS DE SIMULACIÓN")
        reporte.append("=" * 60)
        
        # Información general
        reporte.append(f"\n🕐 INFORMACIÓN GENERAL:")
        reporte.append(f"   Tiempo actual: {estadisticas.tiempo_actual:.1f}s")
        reporte.append(f"   Duración total: {estadisticas.duracion_simulacion:.1f}s")
        
        # Estadísticas de ciclistas
        reporte.append(f"\n🚴 CICLISTAS:")
        reporte.append(f"   Total: {estadisticas.total_ciclistas}")
        reporte.append(f"   Activos: {estadisticas.ciclistas_activos}")
        reporte.append(f"   Completados: {estadisticas.ciclistas_completados}")
        reporte.append(f"   Pausados: {estadisticas.ciclistas_pausados}")
        
        # Estadísticas de velocidad
        reporte.append(f"\n⚡ VELOCIDADES:")
        reporte.append(f"   Promedio: {estadisticas.velocidad_promedio:.1f} m/s")
        reporte.append(f"   Mínima: {estadisticas.velocidad_minima:.1f} m/s")
        reporte.append(f"   Máxima: {estadisticas.velocidad_maxima:.1f} m/s")
        reporte.append(f"   Desviación: {estadisticas.velocidad_desviacion:.1f} m/s")
        
        # Estadísticas de grafo
        reporte.append(f"\n🕸️ GRAFO:")
        reporte.append(f"   Nodos: {estadisticas.grafo_nodos}")
        reporte.append(f"   Arcos: {estadisticas.grafo_arcos}")
        reporte.append(f"   Conectado: {'Sí' if estadisticas.grafo_conectado else 'No'}")
        reporte.append(f"   Distancia promedio arcos: {estadisticas.distancia_promedio_arcos:.1f}m")
        
        # Estadísticas de rutas
        reporte.append(f"\n🛣️ RUTAS:")
        reporte.append(f"   Rutas utilizadas: {estadisticas.rutas_utilizadas}")
        reporte.append(f"   Total viajes: {estadisticas.total_viajes}")
        reporte.append(f"   Ruta más usada: {estadisticas.ruta_mas_usada}")
        
        # Estadísticas de nodos
        reporte.append(f"\n📍 NODOS:")
        reporte.append(f"   Nodo más activo: {estadisticas.nodo_mas_activo}")
        
        reporte.append("\n" + "=" * 60)
        
        return "\n".join(reporte)
    
    @staticmethod
    def generar_reporte_detallado(estadisticas: EstadisticasSimulacion, 
                                 analisis_rutas: Dict[str, Any],
                                 analisis_nodos: Dict[str, Any],
                                 metricas_rendimiento: Dict[str, Any]) -> str:
        """
        Genera un reporte detallado de las estadísticas.
        
        Args:
            estadisticas: Estadísticas de la simulación
            analisis_rutas: Análisis de patrones de rutas
            analisis_nodos: Análisis de actividad de nodos
            metricas_rendimiento: Métricas de rendimiento
            
        Returns:
            str: Reporte detallado en formato texto
        """
        reporte = []
        reporte.append("=" * 80)
        reporte.append("📊 REPORTE DETALLADO DE ESTADÍSTICAS DE SIMULACIÓN")
        reporte.append("=" * 80)
        
        # Incluir reporte resumen
        reporte.append(GeneradorReportes.generar_reporte_resumen(estadisticas))
        
        # Análisis de rutas
        reporte.append(f"\n🔍 ANÁLISIS DE RUTAS:")
        reporte.append(f"   Diversidad de rutas: {analisis_rutas.get('diversidad_rutas', 0):.2f}")
        reporte.append(f"   Concentración de tráfico: {analisis_rutas.get('concentracion_trafico', 0):.1f}%")
        reporte.append(f"   Ruta menos usada: {analisis_rutas.get('ruta_menos_usada', 'N/A')}")
        
        # Top 5 rutas
        rutas_top_5 = analisis_rutas.get('rutas_top_5', [])
        if rutas_top_5:
            reporte.append(f"\n   🏆 TOP 5 RUTAS MÁS USADAS:")
            for i, (ruta, frecuencia) in enumerate(rutas_top_5, 1):
                reporte.append(f"      {i}. {ruta}: {frecuencia} viajes")
        
        # Análisis de nodos
        reporte.append(f"\n🔍 ANÁLISIS DE NODOS:")
        reporte.append(f"   Concentración de actividad: {analisis_nodos.get('concentracion_nodos', 0):.1f}%")
        reporte.append(f"   Nodo menos activo: {analisis_nodos.get('nodo_menos_activo', 'N/A')}")
        
        # Distribución de actividad
        distribucion = analisis_nodos.get('distribucion_actividad', {})
        if distribucion:
            reporte.append(f"\n   📊 DISTRIBUCIÓN DE ACTIVIDAD POR NODO:")
            for nodo, ciclistas in distribucion.items():
                reporte.append(f"      Nodo {nodo}: {ciclistas} ciclistas")
        
        # Métricas de rendimiento
        reporte.append(f"\n⚡ MÉTRICAS DE RENDIMIENTO:")
        reporte.append(f"   Tasa de finalización: {metricas_rendimiento.get('tasa_finalizacion', 0):.1f}%")
        reporte.append(f"   Eficiencia de red: {metricas_rendimiento.get('eficiencia_red', 0):.2f}")
        reporte.append(f"   Densidad de tráfico: {metricas_rendimiento.get('densidad_trafico', 0):.2f}")
        reporte.append(f"   Velocidad de procesamiento: {metricas_rendimiento.get('velocidad_procesamiento', 0):.2f} ciclistas/s")
        
        reporte.append("\n" + "=" * 80)
        
        return "\n".join(reporte)


class GestorEstadisticas:
    """
    Gestor principal para manejar todas las estadísticas de la simulación.
    
    Esta clase orquesta el cálculo y análisis de estadísticas de todos
    los componentes del sistema.
    """
    
    def __init__(self):
        """Inicializa el gestor de estadísticas."""
        self.calculador = CalculadorEstadisticas()
        self.analizador_rutas = AnalizadorRutas()
        self.analizador_rendimiento = AnalizadorRendimiento()
        self.generador_reportes = GeneradorReportes()
    
    def calcular_estadisticas_completas(self, gestor_ciclistas: Any, 
                                      gestor_grafo: Any, 
                                      gestor_distribuciones: Any,
                                      generador: Any,
                                      tiempo_actual: float,
                                      duracion_simulacion: float) -> EstadisticasSimulacion:
        """
        Calcula estadísticas completas de la simulación.
        
        Args:
            gestor_ciclistas: Gestor de ciclistas
            gestor_grafo: Gestor de grafo
            gestor_distribuciones: Gestor de distribuciones
            generador: Generador de ciclistas
            tiempo_actual: Tiempo actual de la simulación
            duracion_simulacion: Duración total de la simulación
            
        Returns:
            EstadisticasSimulacion: Estadísticas completas
        """
        # Calcular estadísticas de cada componente
        stats_ciclistas = self.calculador.calcular_estadisticas_ciclistas(gestor_ciclistas)
        stats_grafo = self.calculador.calcular_estadisticas_grafo(gestor_grafo)
        stats_distribuciones = self.calculador.calcular_estadisticas_distribuciones(gestor_distribuciones)
        stats_generacion = self.calculador.calcular_estadisticas_generacion(generador)
        
        # Crear objeto de estadísticas
        estadisticas = EstadisticasSimulacion(
            tiempo_actual=tiempo_actual,
            duracion_simulacion=duracion_simulacion
        )
        
        # Actualizar con estadísticas de cada componente
        for key, value in stats_ciclistas.items():
            if hasattr(estadisticas, key):
                setattr(estadisticas, key, value)
        
        for key, value in stats_grafo.items():
            if hasattr(estadisticas, key):
                setattr(estadisticas, key, value)
        
        for key, value in stats_distribuciones.items():
            if hasattr(estadisticas, key):
                setattr(estadisticas, key, value)
        
        for key, value in stats_generacion.items():
            if hasattr(estadisticas, key):
                setattr(estadisticas, key, value)
        
        return estadisticas
    
    def generar_analisis_completo(self, estadisticas: EstadisticasSimulacion) -> Dict[str, Any]:
        """
        Genera un análisis completo de las estadísticas.
        
        Args:
            estadisticas: Estadísticas de la simulación
            
        Returns:
            Dict[str, Any]: Análisis completo
        """
        # Análisis de rutas
        analisis_rutas = self.analizador_rutas.analizar_patrones_rutas(
            {estadisticas.ruta_mas_usada: estadisticas.total_viajes}  # Simplificado
        )
        
        # Análisis de nodos
        analisis_nodos = self.analizador_rutas.analizar_nodos_activos(
            estadisticas.ciclistas_por_nodo
        )
        
        # Métricas de rendimiento
        metricas_rendimiento = self.analizador_rendimiento.calcular_metricas_rendimiento(estadisticas)
        
        return {
            'estadisticas': estadisticas,
            'analisis_rutas': analisis_rutas,
            'analisis_nodos': analisis_nodos,
            'metricas_rendimiento': metricas_rendimiento
        }
    
    def generar_reporte_completo(self, analisis_completo: Dict[str, Any]) -> str:
        """
        Genera un reporte completo de la simulación.
        
        Args:
            analisis_completo: Análisis completo de estadísticas
            
        Returns:
            str: Reporte completo
        """
        estadisticas = analisis_completo['estadisticas']
        analisis_rutas = analisis_completo['analisis_rutas']
        analisis_nodos = analisis_completo['analisis_nodos']
        metricas_rendimiento = analisis_completo['metricas_rendimiento']
        
        return self.generador_reportes.generar_reporte_detallado(
            estadisticas, analisis_rutas, analisis_nodos, metricas_rendimiento
        )
    
    def __str__(self) -> str:
        """Representación string del gestor."""
        return "GestorEstadisticas(calculador, analizadores, generador_reportes)"
