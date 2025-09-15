#!/usr/bin/env python3
"""
🎯 SIMULADOR PRINCIPAL - SIMULADOR DE CICLORUTAS 🎯

Este módulo contiene la clase principal SimuladorCiclorutas que orquesta
todos los componentes del sistema de simulación.

Autor: Sistema de Simulación de Ciclorutas
Versión: 2.0 (Refactorizado)
"""

import simpy
from typing import Dict, List, Tuple, Optional, Any
import networkx as nx

# Importar módulos refactorizados
from ..config import ConfiguracionSimulacion, ConfiguracionesPredefinidas
from ..data import GestorDistribuciones, DistribucionNodo, GestorGrafo, ValidadorGrafo, CargadorGrafo, GestorEstadisticas, EstadisticasSimulacion
from .ciclista import GestorCiclistas, EstadoCiclista
from .generador import GeneradorCiclistas, GeneradorSimple, ConfiguracionGeneracion, AsignadorRutas


class SimuladorCiclorutas:
    """
    Clase principal para manejar la simulación de ciclorutas.
    
    Esta clase actúa como orquestador principal que coordina todos los
    componentes del sistema de simulación.
    """
    
    def __init__(self, config: Optional[ConfiguracionSimulacion] = None):
        """
        Inicializa el simulador.
        
        Args:
            config: Configuración de la simulación (opcional)
        """
        # Configuración
        self.config = config or ConfiguracionSimulacion()
        
        # Entorno de SimPy
        self.env: Optional[simpy.Environment] = None
        
        # Estado de la simulación
        self.estado = "detenido"  # detenido, ejecutando, pausado, completada
        self.tiempo_actual = 0.0
        self.tiempo_total = self.config.duracion_simulacion
        
        # Gestores de componentes
        self.gestor_distribuciones = GestorDistribuciones()
        self.gestor_grafo = GestorGrafo()
        self.gestor_ciclistas = GestorCiclistas(self.config)
        self.gestor_estadisticas = GestorEstadisticas()
        
        # Generador de ciclistas
        self.generador: Optional[Any] = None
        self.asignador_rutas: Optional[AsignadorRutas] = None
        
        # Procesos de SimPy
        self.procesos: List[simpy.Process] = []
    
    def configurar_grafo(self, grafo: nx.Graph, posiciones: Dict[str, Tuple[float, float]]) -> bool:
        """
        Configura el grafo NetworkX y sus posiciones para la simulación.
        
        Args:
            grafo: Grafo de NetworkX
            posiciones: Posiciones de los nodos
            
        Returns:
            bool: True si la configuración fue exitosa
        """
        # Validar grafo
        es_valido, errores = ValidadorGrafo.validar_grafo(grafo)
        if not es_valido:
            print(f"⚠️ Error validando grafo: {errores}")
            return False
        
        # Validar posiciones
        es_valido_pos, errores_pos = ValidadorGrafo.validar_posiciones(posiciones, grafo)
        if not es_valido_pos:
            print(f"⚠️ Error validando posiciones: {errores_pos}")
            return False
        
        # Configurar en el gestor de grafo
        self.gestor_grafo.grafo_actual = grafo
        self.gestor_grafo.posiciones_actuales = posiciones
        self.gestor_grafo._inicializar_grafo()
        
        # Crear asignador de rutas
        rutas_dinamicas = self.gestor_grafo.obtener_rutas_dinamicas()
        self.asignador_rutas = AsignadorRutas(grafo, rutas_dinamicas)
        
        # Inicializar distribuciones por defecto para todos los nodos
        self._inicializar_distribuciones_por_defecto(list(grafo.nodes()))
        
        print(f"✅ Grafo configurado exitosamente: {len(grafo.nodes())} nodos, {len(grafo.edges())} arcos")
        return True
    
    def _inicializar_distribuciones_por_defecto(self, nodos: List[str]):
        """
        Inicializa distribuciones por defecto para todos los nodos.
        
        Args:
            nodos: Lista de nodos del grafo
        """
        for i, nodo in enumerate(nodos):
            if nodo not in self.gestor_distribuciones.distribuciones:
                # Distribución exponencial por defecto con tasas variadas
                lambda_val = 0.3 + (i * 0.2)  # Tasas de 0.3 a 0.9
                distribucion = DistribucionNodo('exponencial', {'lambda': lambda_val})
                self.gestor_distribuciones.agregar_distribucion(nodo, distribucion)
        
        print(f"✅ Distribuciones por defecto inicializadas para {len(nodos)} nodos")
    
    def configurar_distribuciones_nodos(self, distribuciones: Dict[str, Dict]):
        """
        Configura las distribuciones de probabilidad para cada nodo.
        
        Args:
            distribuciones: Diccionario de configuraciones de distribuciones
        """
        for nodo_id, config_dist in distribuciones.items():
            tipo = config_dist.get('tipo', 'exponencial')
            parametros = config_dist.get('parametros', {})
            distribucion = DistribucionNodo(tipo, parametros)
            self.gestor_distribuciones.agregar_distribucion(nodo_id, distribucion)
        
        print(f"✅ Distribuciones configuradas para {len(distribuciones)} nodos")
    
    def actualizar_distribucion_nodo(self, nodo_id: str, tipo: str, parametros: Dict):
        """
        Actualiza la distribución de un nodo específico.
        
        Args:
            nodo_id: Identificador del nodo
            tipo: Tipo de distribución
            parametros: Parámetros de la distribución
        """
        self.gestor_distribuciones.actualizar_distribucion_nodo(nodo_id, tipo, parametros)
        print(f"✅ Distribución actualizada para nodo {nodo_id}: {tipo}")
    
    def inicializar_simulacion(self):
        """Inicializa una nueva simulación con los parámetros configurados."""
        # Limpiar datos anteriores
        self.gestor_ciclistas.limpiar_ciclistas()
        self.procesos.clear()
        
        # Crear entorno SimPy
        self.env = simpy.Environment()
        
        # Verificar que hay un grafo cargado
        if not self.gestor_grafo.tiene_grafo_cargado():
            print("⚠️ No hay grafo cargado. Carga un grafo para iniciar la simulación.")
            return
        
        # Verificar que el asignador de rutas está inicializado
        if not hasattr(self, 'asignador_rutas') or self.asignador_rutas is None:
            print("⚠️ Asignador de rutas no inicializado. Configurando grafo...")
            grafo = self.gestor_grafo.obtener_grafo()
            posiciones = self.gestor_grafo.obtener_posiciones()
            if grafo and posiciones:
                self.configurar_grafo(grafo, posiciones)
            else:
                print("❌ No se puede configurar el grafo. Saliendo...")
                return
        
        # Crear configuración de generación
        config_generacion = ConfiguracionGeneracion(
            duracion_simulacion=self.config.duracion_simulacion,
            max_ciclistas_simultaneos=self.config.max_ciclistas_simultaneos,
            usar_distribuciones=len(self.gestor_distribuciones) > 0
        )
        
        # Crear generador apropiado
        if config_generacion.usar_distribuciones:
            self.generador = GeneradorCiclistas(
                config_generacion,
                self.gestor_distribuciones,
                self.gestor_ciclistas,
                self.asignador_rutas
            )
        else:
            self.generador = GeneradorSimple(
                config_generacion,
                self.gestor_ciclistas,
                self.asignador_rutas
            )
        
        # Crear proceso de generación de ciclistas
        if isinstance(self.generador, GeneradorCiclistas):
            proceso_generacion = self.env.process(
                self.generador.generar_ciclistas_realista(
                    self.env,
                    self.gestor_grafo.obtener_grafo(),
                    self.gestor_grafo.obtener_posiciones(),
                    self.gestor_grafo.obtener_colores_nodos()
                )
            )
        else:
            proceso_generacion = self.env.process(
                self.generador.generar_ciclistas_uniforme(
                    self.env,
                    self.gestor_grafo.obtener_grafo(),
                    self.gestor_grafo.obtener_posiciones(),
                    self.gestor_grafo.obtener_colores_nodos()
                )
            )
        self.procesos.append(proceso_generacion)
        
        # Proceso para detener la simulación después de la duración
        proceso_detener = self.env.process(self._detener_por_tiempo())
        self.procesos.append(proceso_detener)
        
        self.estado = "detenido"
        self.tiempo_actual = 0.0
        self.tiempo_total = self.config.duracion_simulacion
        
        print("✅ Simulación inicializada correctamente")
    
    def _detener_por_tiempo(self):
        """Detiene la simulación después del tiempo configurado."""
        yield self.env.timeout(self.config.duracion_simulacion)
        # No cambiar el estado automáticamente - solo mostrar mensaje
        print(f"⏰ Simulación ha alcanzado {self.config.duracion_simulacion} segundos - Continúa ejecutándose")
    
    def ejecutar_paso(self) -> bool:
        """
        Ejecuta un paso de la simulación.
        
        Returns:
            bool: True si la simulación continúa, False si ha terminado
        """
        if self.env and self.estado == "ejecutando":
            try:
                self.env.step()
                self.tiempo_actual = self.env.now
                return True
            except Exception as e:
                print(f"⚠️ Error ejecutando paso de simulación: {e}")
                return False
        return False
    
    def pausar_simulacion(self):
        """Pausa la simulación."""
        if self.estado == "ejecutando":
            self.estado = "pausado"
            self.gestor_ciclistas.pausar_todos()
            print("⏸️ Simulación pausada")
    
    def reanudar_simulacion(self):
        """Reanuda la simulación pausada."""
        if self.estado == "pausado":
            self.estado = "ejecutando"
            self.gestor_ciclistas.reanudar_todos()
            print("▶️ Simulación reanudada")
    
    def detener_simulacion(self):
        """Detiene la simulación."""
        self.estado = "detenido"
        self.tiempo_actual = 0.0
        print("⏹️ Simulación detenida")
    
    def marcar_completada(self):
        """Marca la simulación como completada manualmente."""
        self.estado = "completada"
        print("✅ Simulación marcada como completada")
    
    def reiniciar_simulacion(self):
        """Reinicia la simulación desde el principio."""
        self.inicializar_simulacion()
        print("🔄 Simulación reiniciada")
    
    def reiniciar_sin_limpiar(self):
        """Reinicia la simulación sin limpiar las entidades existentes."""
        # Solo limpiar procesos, no ciclistas
        self.procesos.clear()
        
        # Crear entorno SimPy
        self.env = simpy.Environment()
        
        # Verificar que hay un grafo cargado
        if not self.gestor_grafo.tiene_grafo_cargado():
            print("⚠️ No hay grafo cargado. Carga un grafo para iniciar la simulación.")
            return
        
        # Verificar que el asignador de rutas está inicializado
        if not hasattr(self, 'asignador_rutas') or self.asignador_rutas is None:
            print("⚠️ Asignador de rutas no inicializado. Configurando grafo...")
            grafo = self.gestor_grafo.obtener_grafo()
            posiciones = self.gestor_grafo.obtener_posiciones()
            if grafo and posiciones:
                self.configurar_grafo(grafo, posiciones)
            else:
                print("❌ No se puede configurar el grafo. Saliendo...")
                return
        
        # Crear configuración de generación
        config_generacion = ConfiguracionGeneracion(
            duracion_simulacion=self.config.duracion_simulacion,
            max_ciclistas_simultaneos=self.config.max_ciclistas_simultaneos,
            usar_distribuciones=len(self.gestor_distribuciones) > 0
        )
        
        # Crear generador apropiado
        if config_generacion.usar_distribuciones:
            self.generador = GeneradorCiclistas(
                config_generacion,
                self.gestor_distribuciones,
                self.gestor_ciclistas,
                self.asignador_rutas
            )
        else:
            self.generador = GeneradorSimple(
                config_generacion,
                self.gestor_ciclistas,
                self.asignador_rutas
            )
        
        # Crear proceso de generación de ciclistas
        if isinstance(self.generador, GeneradorCiclistas):
            proceso_generacion = self.env.process(
                self.generador.generar_ciclistas(self.env)
            )
            self.procesos.append(proceso_generacion)
        else:
            proceso_generacion = self.env.process(
                self.generador.generar_ciclistas(self.env)
            )
            self.procesos.append(proceso_generacion)
        
        # Crear proceso de detención por tiempo
        proceso_detencion = self.env.process(self._detener_por_tiempo())
        self.procesos.append(proceso_detencion)
        
        # Configurar estado
        self.estado = "detenido"
        self.tiempo_actual = 0.0
        
        print("🔄 Simulación reiniciada sin limpiar entidades")
    
    def obtener_estado_actual(self) -> Dict[str, Any]:
        """
        Retorna el estado actual de la simulación.
        
        Returns:
            Dict[str, Any]: Estado actual de la simulación
        """
        return {
            'estado': self.estado,
            'tiempo_actual': self.tiempo_actual,
            'tiempo_total': self.tiempo_total,
            'progreso': (self.tiempo_actual / self.tiempo_total) * 100 if self.tiempo_total > 0 else 0,
            'grafo_cargado': self.gestor_grafo.tiene_grafo_cargado(),
            'distribuciones_configuradas': len(self.gestor_distribuciones)
        }
    
    def obtener_ciclistas_activos(self) -> Dict[str, Any]:
        """
        Retorna información de los ciclistas activos.
        
        Returns:
            Dict[str, Any]: Información de ciclistas activos
        """
        return self.gestor_ciclistas.obtener_ciclistas_activos()
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Retorna estadísticas de la simulación.
        
        Returns:
            Dict[str, Any]: Estadísticas de la simulación
        """
        # Calcular estadísticas completas
        estadisticas = self.gestor_estadisticas.calcular_estadisticas_completas(
            self.gestor_ciclistas,
            self.gestor_grafo,
            self.gestor_distribuciones,
            self.generador,
            self.tiempo_actual,
            self.tiempo_total
        )
        
        # Convertir a diccionario para compatibilidad
        return {
            'total_ciclistas': estadisticas.total_ciclistas,
            'ciclistas_activos': estadisticas.ciclistas_activos,
            'ciclistas_completados': estadisticas.ciclistas_completados,
            'velocidad_promedio': estadisticas.velocidad_promedio,
            'velocidad_minima': estadisticas.velocidad_minima,
            'velocidad_maxima': estadisticas.velocidad_maxima,
            'usando_grafo_real': self.gestor_grafo.tiene_grafo_cargado(),
            'duracion_simulacion': estadisticas.duracion_simulacion,
            'grafo_nodos': estadisticas.grafo_nodos,
            'grafo_arcos': estadisticas.grafo_arcos,
            'distribuciones_configuradas': estadisticas.distribuciones_configuradas,
            'tasa_arribo_promedio': estadisticas.tasa_arribo_promedio,
            'rutas_utilizadas': estadisticas.rutas_utilizadas,
            'total_viajes': estadisticas.total_viajes,
            'ruta_mas_usada': estadisticas.ruta_mas_usada,
            'nodo_mas_activo': estadisticas.nodo_mas_activo
        }
    
    def obtener_distribuciones_nodos(self) -> Dict[str, Dict]:
        """
        Retorna la configuración actual de distribuciones.
        
        Returns:
            Dict[str, Dict]: Configuración de distribuciones
        """
        return self.gestor_distribuciones.obtener_todas_distribuciones()
    
    def obtener_colores_nodos(self) -> Dict[str, str]:
        """
        Retorna el mapeo de colores por nodo.
        
        Returns:
            Dict[str, str]: Mapeo de colores
        """
        return self.gestor_grafo.obtener_colores_nodos()
    
    def cargar_grafo_desde_excel(self, archivo: str) -> Tuple[bool, List[str]]:
        """
        Carga un grafo desde un archivo Excel.
        
        Args:
            archivo: Ruta del archivo Excel
            
        Returns:
            Tuple[bool, List[str]]: (exitoso, lista_de_errores)
        """
        return self.gestor_grafo.cargar_grafo_desde_excel(archivo)
    
    def crear_grafo_ejemplo(self):
        """Crea un grafo de ejemplo para testing."""
        self.gestor_grafo.crear_grafo_ejemplo()
        grafo = self.gestor_grafo.obtener_grafo()
        posiciones = self.gestor_grafo.obtener_posiciones()
        
        if grafo and posiciones:
            self.configurar_grafo(grafo, posiciones)
    
    def generar_reporte_completo(self) -> str:
        """
        Genera un reporte completo de la simulación.
        
        Returns:
            str: Reporte completo
        """
        # Calcular estadísticas completas
        estadisticas = self.gestor_estadisticas.calcular_estadisticas_completas(
            self.gestor_ciclistas,
            self.gestor_grafo,
            self.gestor_distribuciones,
            self.generador,
            self.tiempo_actual,
            self.tiempo_total
        )
        
        # Generar análisis completo
        analisis_completo = self.gestor_estadisticas.generar_analisis_completo(estadisticas)
        
        # Generar reporte
        return self.gestor_estadisticas.generar_reporte_completo(analisis_completo)
    
    def __str__(self) -> str:
        """Representación string del simulador."""
        return (f"SimuladorCiclorutas(estado={self.estado}, "
                f"tiempo={self.tiempo_actual:.1f}s, "
                f"ciclistas={len(self.gestor_ciclistas)})")
    
    def __repr__(self) -> str:
        """Representación detallada del simulador."""
        return self.__str__()


# Funciones de utilidad para crear simuladores
def crear_simulador_rapido() -> SimuladorCiclorutas:
    """Crea un simulador con configuración rápida para testing."""
    config = ConfiguracionesPredefinidas.simulacion_rapida()
    simulador = SimuladorCiclorutas(config)
    simulador.crear_grafo_ejemplo()
    return simulador


def crear_simulador_realista() -> SimuladorCiclorutas:
    """Crea un simulador con configuración realista."""
    config = ConfiguracionesPredefinidas.simulacion_realista()
    return SimuladorCiclorutas(config)


def crear_simulador_intensivo() -> SimuladorCiclorutas:
    """Crea un simulador con configuración intensiva."""
    config = ConfiguracionesPredefinidas.simulacion_intensiva()
    return SimuladorCiclorutas(config)
