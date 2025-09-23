"""
Aplicación principal de la interfaz de simulación.

Este módulo contiene la clase principal que orquesta todos los componentes
de la interfaz gráfica del simulador.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from typing import Dict, Any, Callable, Optional, List
import pandas as pd
import networkx as nx

from ..panels.panel_control import PanelControl
from ..panels.panel_visualizacion import PanelVisualizacion
from ..panels.panel_estadisticas import PanelEstadisticas
from ..panels.panel_distribuciones import PanelDistribuciones
from ..utils.estilo_utils import EstiloUtils
from ..utils.archivo_utils import ArchivoUtils

# Importar el simulador desde el paquete Simulador
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from Simulador.core.simulador import SimuladorCiclorutas
from Simulador.core.configuracion import ConfiguracionSimulacion


class InterfazSimulacion:
    """Interfaz gráfica principal para controlar la simulación de ciclorutas"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🚴 Simulador de Ciclorutas - Control Avanzado")
        self.root.geometry("1400x900")
        self.root.configure(bg=EstiloUtils.COLORES['gris_claro'])
        
        # Configuración por defecto
        self.config = ConfiguracionSimulacion()
        self.simulador = SimuladorCiclorutas(self.config)
        
        # Variables para el grafo
        self.grafo_actual = None
        self.pos_grafo_actual = None
        self.perfiles_df = None
        self.rutas_df = None
        self.nombre_archivo_excel = None
        
        # Variables de control
        self.simulacion_activa = False
        self.hilo_simulacion = None
        self.ventana_cerrada = False
        
        # Cache de datos de interfaz
        self._cache_interfaz = None
        self._ultima_actualizacion_cache = 0
        self._intervalo_cache = 0.1  # Actualizar cache cada 100ms
        
        # Configurar manejo de cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        
        # Configurar estilo
        EstiloUtils.configurar_estilo_ttk()
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Inicializar simulación
        self.simulador.inicializar_simulacion()
        self.actualizar_visualizacion()
    
    def crear_interfaz(self):
        """Crea todos los elementos de la interfaz"""
        # Frame principal
        main_frame = EstiloUtils.crear_frame_con_estilo(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=0)  # Estadísticas no expanden verticalmente
        
        # Crear PanedWindow para paneles redimensionables
        self.paned_main = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        self.paned_main.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Crear callbacks para los paneles
        callbacks = self._crear_callbacks()
        
        # Panel de control izquierdo
        self.panel_control = PanelControl(self.paned_main, callbacks)
        self.paned_main.add(self.panel_control.frame_principal, weight=1)
        
        # Panel de distribuciones (centro)
        self.panel_distribuciones = PanelDistribuciones(self.paned_main, callbacks)
        self.paned_main.add(self.panel_distribuciones.frame_principal, weight=1)
        
        # Panel de visualización (derecha)
        self.panel_visualizacion = PanelVisualizacion(self.paned_main, callbacks)
        self.paned_main.add(self.panel_visualizacion.frame_principal, weight=2)
        
        # Panel de estadísticas (abajo) - fuera del PanedWindow para ancho completo
        self.panel_estadisticas = PanelEstadisticas(main_frame, callbacks)
        self.panel_estadisticas.frame_principal.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def _crear_callbacks(self) -> Dict[str, Callable]:
        """Crea los callbacks para comunicación entre paneles"""
        return {
            # Callbacks de control
            'aplicar_velocidades': self.aplicar_velocidades,
            'cargar_grafo': self.cargar_grafo,
            'nueva_simulacion': self.nueva_simulacion,
            'iniciar_simulacion': self.iniciar_simulacion,
            'pausar_simulacion': self.pausar_simulacion,
            'terminar_simulacion': self.terminar_simulacion,
            'adelantar_simulacion': self.adelantar_simulacion,
            'reiniciar_simulacion': self.reiniciar_simulacion,
            
            # Callbacks de visualización
            'actualizar_visualizacion': self.actualizar_visualizacion_grafo,
            'click_grafico': self.click_grafico,
            
            # Callbacks de distribuciones
            'aplicar_distribucion': self.aplicar_distribucion_nodo,
            'actualizar_perfil': self.actualizar_perfil_ciclista,
            
            # Callbacks de estadísticas
            'exportar_estadisticas': self.exportar_estadisticas,
            
            # Callbacks para acceso a datos
            'obtener_grafo_actual': lambda: self.grafo_actual,
            'obtener_perfiles_df': lambda: self.perfiles_df,
            'obtener_rutas_df': lambda: self.rutas_df
        }
    
    def aplicar_velocidades(self, vel_min: float, vel_max: float):
        """Aplica los cambios de velocidad configurados"""
        try:
            # Actualizar configuración
            self.config.actualizar_velocidades(vel_min, vel_max)
            
            # Actualizar simulador si existe
            if hasattr(self, 'simulador') and self.simulador:
                self.simulador.config.actualizar_velocidades(vel_min, vel_max)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar velocidades: {str(e)}")
    
    def cargar_grafo(self):
        """Carga un grafo desde archivo Excel"""
        archivo = ArchivoUtils.seleccionar_archivo_excel()
        if not archivo:
            return
        
        try:
            # Cargar datos desde Excel
            grafo, pos_grafo, perfiles_df, rutas_df, mensaje = ArchivoUtils.cargar_datos_desde_excel(archivo)
            
            if grafo is None:
                ArchivoUtils.mostrar_dialogo_error_carga(mensaje)
                return
            
            # Guardar datos
            self.grafo_actual = grafo
            self.pos_grafo_actual = pos_grafo
            self.perfiles_df = perfiles_df
            self.rutas_df = rutas_df
            self.nombre_archivo_excel = os.path.basename(archivo)
            
            # Configurar el simulador con el nuevo grafo
            self.simulador.configurar_grafo(grafo, pos_grafo, perfiles_df, rutas_df)
            
            # Reinicializar la simulación para que esté lista para ejecutar
            self.simulador.inicializar_simulacion()
            
            # Actualizar paneles
            self.actualizar_paneles_con_grafo()
            
            # Actualizar visualización para mostrar el estado inicial
            self.actualizar_visualizacion()
            
            # Mostrar mensaje de éxito
            ArchivoUtils.mostrar_dialogo_carga_exitosa(archivo, grafo, perfiles_df, rutas_df)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {str(e)}")
    
    def actualizar_paneles_con_grafo(self):
        """Actualiza todos los paneles cuando se carga un grafo"""
        # Actualizar panel de control
        info_grafo = f"Red Ciclorutas: {len(self.grafo_actual.nodes())} nodos, {len(self.grafo_actual.edges())} arcos"
        if self.nombre_archivo_excel:
            info_grafo += f"\n📁 Archivo: {self.nombre_archivo_excel}"
        self.panel_control.actualizar_info_grafo(info_grafo)
        
        # Actualizar estado del panel de control para indicar que está listo
        self.panel_control.actualizar_estado("LISTO", 0.0)
        
        # Actualizar panel de visualización
        self.panel_visualizacion.configurar_grafico_con_grafo(
            self.grafo_actual, self.pos_grafo_actual, self.nombre_archivo_excel
        )
        
        # Limpiar mensaje inicial para mostrar el grafo
        self.panel_visualizacion.limpiar_mensaje_inicial()
        
        # Actualizar controles de visualización
        atributos_disponibles = self._obtener_atributos_disponibles()
        self.panel_visualizacion.actualizar_controles_visualizacion(atributos_disponibles)
        
        # Actualizar panel de distribuciones
        distribuciones_actuales = self.simulador.obtener_distribuciones_nodos()
        self.panel_distribuciones.actualizar_panel_distribuciones(self.grafo_actual, distribuciones_actuales)
        
        # Obtener atributos disponibles para perfiles
        atributos_perfiles_disponibles = self._obtener_atributos_perfiles_disponibles()
        self.panel_distribuciones.actualizar_panel_perfiles(self.perfiles_df, atributos_perfiles_disponibles)
        
        # Actualizar panel de estadísticas
        self.actualizar_estadisticas()
    
    def _obtener_atributos_disponibles(self) -> List[str]:
        """Obtiene la lista de atributos disponibles en el grafo"""
        if not self.grafo_actual:
            return []
        
        atributos_disponibles = set()
        for edge in self.grafo_actual.edges(data=True):
            for key in edge[2].keys():
                if key not in ['weight']:
                    atributos_disponibles.add(key)
        
        return list(atributos_disponibles)
    
    def _obtener_atributos_perfiles_disponibles(self) -> List[str]:
        """Obtiene la lista de atributos disponibles tanto en el grafo como en los perfiles"""
        if not self.grafo_actual:
            return []
        
        # Obtener atributos del grafo
        atributos_grafo = set()
        for edge in self.grafo_actual.edges(data=True):
            for key in edge[2].keys():
                if key not in ['weight']:
                    atributos_grafo.add(key)
        
        # Obtener atributos de perfiles si existen
        atributos_perfiles = set()
        if self.perfiles_df is not None:
            # Mapeo de columnas Excel a claves internas
            mapeo_columnas = {
                'DISTANCIA': 'distancia',
                'SEGURIDAD': 'seguridad',
                'LUMINOSIDAD': 'luminosidad', 
                'INCLINACION': 'inclinacion'
            }
            
            for col_excel, clave_interna in mapeo_columnas.items():
                if col_excel in self.perfiles_df.columns:
                    atributos_perfiles.add(clave_interna)
        
        # Retornar solo los atributos que están tanto en el grafo como en los perfiles
        atributos_comunes = atributos_grafo.intersection(atributos_perfiles)
        
        # Si no hay perfiles, usar todos los atributos del grafo
        if not atributos_perfiles:
            atributos_comunes = atributos_grafo
        
        return list(atributos_comunes)
    
    def nueva_simulacion(self):
        """Crea una nueva simulación con los parámetros actuales"""
        try:
            # Detener simulación actual si está corriendo
            if self.simulacion_activa:
                self.simulacion_activa = False
                time.sleep(0.1)
            
            # Obtener velocidades del panel de control
            vel_min, vel_max = self.panel_control.obtener_velocidades()
            self.config.actualizar_velocidades(vel_min, vel_max)
            
            # Crear nuevo simulador
            self.simulador = SimuladorCiclorutas(self.config)
            
            # Si hay un grafo cargado, configurarlo en el nuevo simulador
            if self.grafo_actual and self.pos_grafo_actual:
                self.simulador.configurar_grafo(self.grafo_actual, self.pos_grafo_actual, self.perfiles_df, self.rutas_df)
            
            self.simulador.inicializar_simulacion()
            
            # Actualizar interfaz
            self.actualizar_paneles_con_grafo()
            self.actualizar_visualizacion()
            self.panel_control.actualizar_estado("LISTO", 0.0)
            
            # Limpiar mensaje inicial si no hay grafo
            if not self.grafo_actual:
                self.panel_visualizacion.limpiar_mensaje_inicial()
            
            # Resetear botón de pausa
            self.panel_control.resetear_boton_pausa()
            
            messagebox.showinfo("Nueva Simulación", "Simulación creada exitosamente con los nuevos parámetros!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear la simulación: {str(e)}")
    
    def iniciar_simulacion(self):
        """Inicia la simulación"""
        if not self.simulacion_activa:
            self.simulador.estado = "ejecutando"
            self.simulacion_activa = True
            self.panel_control.actualizar_estado("EJECUTANDO", self.simulador.tiempo_actual)
            
            # Iniciar hilo de simulación
            self.hilo_simulacion = threading.Thread(target=self.ejecutar_simulacion)
            self.hilo_simulacion.daemon = True
            self.hilo_simulacion.start()
    
    def ejecutar_simulacion(self):
        """Ejecuta la simulación en un hilo separado"""
        while self.simulacion_activa and self.simulador.estado == "ejecutando" and not self.ventana_cerrada:
            if self.simulador.ejecutar_paso():
                # Actualizar interfaz en el hilo principal
                if not self.ventana_cerrada and self.root.winfo_exists():
                    self.root.after(0, self.actualizar_interfaz)
                time.sleep(0.05)  # Control de velocidad
            else:
                # La simulación ha terminado
                if not self.ventana_cerrada and self.root.winfo_exists():
                    self.root.after(0, self.simulacion_terminada)
                break
    
    def actualizar_interfaz(self):
        """Actualiza la interfaz con los datos actuales"""
        if self.ventana_cerrada or not self.root.winfo_exists():
            return
        
        try:
            # Cache de datos para evitar recálculos costosos
            tiempo_actual = time.time()
            if (self._cache_interfaz is None or 
                tiempo_actual - self._ultima_actualizacion_cache > self._intervalo_cache):
                
                # Actualizar cache con datos del simulador
                estado = self.simulador.obtener_estado_actual()
                ciclistas_activos = self.simulador.obtener_ciclistas_activos()
                estadisticas = self.simulador.obtener_estadisticas()
                
                self._cache_interfaz = {
                    'estado': estado,
                    'ciclistas_activos': ciclistas_activos,
                    'estadisticas': estadisticas,
                    'timestamp': tiempo_actual
                }
                self._ultima_actualizacion_cache = tiempo_actual
            else:
                # Usar datos del cache
                estado = self._cache_interfaz['estado']
                ciclistas_activos = self._cache_interfaz['ciclistas_activos']
                estadisticas = self._cache_interfaz['estadisticas']
            
            # Actualizar interfaz con datos
            self.panel_control.actualizar_estado(estado['estado'], estado['tiempo_actual'])
            self.panel_visualizacion.actualizar_visualizacion(ciclistas_activos)
            self.panel_estadisticas.actualizar_estadisticas(estadisticas)
            
        except tk.TclError:
            # Widget ya fue destruido
            pass
    
    def pausar_simulacion(self):
        """Pausa o reanuda la simulación"""
        if self.ventana_cerrada or not self.root.winfo_exists():
            return
        
        try:
            if self.simulador.estado == "ejecutando":
                # Pausar
                self.simulador.pausar_simulacion()
                self.panel_control.actualizar_estado("PAUSADO", self.simulador.tiempo_actual)
            else:
                # Reanudar
                self.simulador.estado = "ejecutando"
                self.simulacion_activa = True
                self.panel_control.actualizar_estado("EJECUTANDO", self.simulador.tiempo_actual)
                
                # Reiniciar hilo de simulación
                self.hilo_simulacion = threading.Thread(target=self.ejecutar_simulacion)
                self.hilo_simulacion.daemon = True
                self.hilo_simulacion.start()
                
        except tk.TclError:
            pass
    
    def terminar_simulacion(self):
        """Termina la simulación llevándola a su estado final"""
        # Ejecutar la simulación hasta el final
        while self.simulador.ejecutar_paso():
            pass
        
        # Marcar como terminada
        self.simulacion_activa = False
        self.simulador.estado = "completada"
        
        # Actualizar interfaz
        if not self.ventana_cerrada and self.root.winfo_exists():
            try:
                self.panel_control.actualizar_estado("TERMINADA", self.simulador.tiempo_actual)
                self.actualizar_interfaz()
                
                messagebox.showinfo("Simulación Terminada", 
                                  "¡La simulación ha sido terminada exitosamente!\n\n"
                                  "Todos los ciclistas han completado sus rutas.")
            except tk.TclError:
                pass
    
    def simulacion_terminada(self):
        """Maneja cuando la simulación termina naturalmente"""
        self.simulacion_activa = False
        
        if self.ventana_cerrada or not self.root.winfo_exists():
            return
        
        try:
            self.panel_control.actualizar_estado("COMPLETADA", self.simulador.tiempo_actual)
            self.actualizar_estadisticas()
            
            messagebox.showinfo("Simulación Completada", 
                              "¡La simulación ha terminado! Puedes:\n\n"
                              "• Hacer clic en 'NUEVA' para crear una nueva simulación\n"
                              "• Hacer clic en 'REINICIAR' para repetir la misma simulación\n"
                              "• Modificar parámetros y crear una nueva simulación")
        except tk.TclError:
            pass
    
    def adelantar_simulacion(self):
        """Adelanta la simulación varios pasos"""
        for _ in range(10):  # Adelantar 10 pasos
            if not self.simulador.ejecutar_paso():
                break
        self.actualizar_interfaz()
    
    def reiniciar_simulacion(self):
        """Reinicia la simulación actual con los mismos parámetros"""
        try:
            # Reinicializar el simulador actual
            self.simulador.inicializar_simulacion()
            
            # Resetear estado
            self.simulacion_activa = False
            self.panel_control.actualizar_estado("LISTO", 0.0)
            
            # Actualizar visualización
            self.actualizar_visualizacion()
            self.actualizar_estadisticas()
            
            # Resetear botón de pausa
            self.panel_control.resetear_boton_pausa()
            
            messagebox.showinfo("Simulación Reiniciada", "La simulación ha sido reiniciada exitosamente!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al reiniciar la simulación: {str(e)}")
    
    def actualizar_visualizacion(self):
        """Actualiza la visualización con los datos actuales"""
        ciclistas_activos = self.simulador.obtener_ciclistas_activos()
        self.panel_visualizacion.actualizar_visualizacion(ciclistas_activos)
    
    def actualizar_visualizacion_grafo(self):
        """Actualiza la visualización del grafo según la selección del usuario"""
        if self.grafo_actual and self.pos_grafo_actual:
            self.panel_visualizacion.configurar_grafico_con_grafo(
                self.grafo_actual, self.pos_grafo_actual, self.nombre_archivo_excel
            )
        else:
            self.panel_visualizacion.configurar_grafico_inicial()
    
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas mostradas"""
        stats = self.simulador.obtener_estadisticas()
        self.panel_estadisticas.actualizar_estadisticas(stats)
    
    def click_grafico(self, x: float, y: float):
        """Maneja clics en el gráfico"""
        print(f"Click en coordenadas: ({x:.2f}, {y:.2f})")
    
    def aplicar_distribucion_nodo(self, nodo_id: str, tipo: str, parametros: Dict):
        """Aplica una distribución a un nodo específico"""
        self.simulador.actualizar_distribucion_nodo(nodo_id, tipo, parametros)
    
    def actualizar_perfil_ciclista(self, perfil_id: int, pesos_vars: Dict):
        """Actualiza un perfil de ciclista"""
        # Esta funcionalidad se implementaría aquí
        print(f"Actualizando perfil {perfil_id} con pesos: {pesos_vars}")
    
    def exportar_estadisticas(self):
        """Exporta las estadísticas actuales"""
        stats = self.simulador.obtener_estadisticas()
        # Implementar exportación de estadísticas
        print("Exportando estadísticas...")
    
    def cerrar_aplicacion(self):
        """Maneja el cierre seguro de la aplicación"""
        # Marcar que la ventana está siendo cerrada
        self.ventana_cerrada = True
        
        # Detener la simulación si está activa
        if self.simulacion_activa:
            self.simulacion_activa = False
            if self.simulador:
                self.simulador.detener_simulacion()
        
        # Esperar a que el hilo termine
        if self.hilo_simulacion and self.hilo_simulacion.is_alive():
            self.hilo_simulacion.join(timeout=1.0)
        
        # Destruir la ventana
        self.root.destroy()


def main():
    """Función principal para ejecutar la interfaz"""
    root = tk.Tk()
    app = InterfazSimulacion(root)
    root.mainloop()


if __name__ == "__main__":
    main()
