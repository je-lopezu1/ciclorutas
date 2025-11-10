"""
Panel de estadísticas de la simulación.

Este módulo contiene el panel de estadísticas que muestra métricas
en tiempo real de la simulación con scroll y mejor organización.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Dict, List, Any, Callable

from ..utils.estilo_utils import EstiloUtils


class PanelEstadisticas:
    """Panel de estadísticas con métricas en tiempo real y scroll"""
    
    def __init__(self, parent, callbacks: Dict[str, Callable]):
        self.parent = parent
        self.callbacks = callbacks
        
        # Diccionario para almacenar referencias a los labels
        self.stats_labels = {}
        
        # Variables para control de scroll
        self.canvas = None
        self.scrollbar = None
        self.scrollable_frame = None
        
        # Crear el panel
        self.crear_panel()
    
    def crear_panel(self):
        """Crea el panel de estadísticas principal con scroll"""
        # Frame principal
        self.frame_principal = EstiloUtils.crear_label_frame_con_estilo(
            self.parent, 
            "📈 ESTADÍSTICAS DE SIMULACIÓN"
        )
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Crear sistema de scroll
        self._crear_sistema_scroll()
        
        # Crear el contenido del panel
        self._crear_contenido_estadisticas()
    
    def _crear_sistema_scroll(self):
        """Crea el sistema de scroll para el panel de estadísticas"""
        # Crear canvas para scroll primero
        self.canvas = tk.Canvas(
            self.frame_principal, 
            bg=EstiloUtils.COLORES.get('gris_claro', '#f8f9fa'),
            highlightthickness=0
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        
        # Crear scrollbar vertical (siempre visible en el lado derecho)
        self.scrollbar = ttk.Scrollbar(
            self.frame_principal, 
            orient=tk.VERTICAL, 
            command=self.canvas.yview
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=5)
        
        # Configurar canvas con scrollbar
        self.canvas.configure(yscrollcommand=self._on_scrollbar_update)
        
        # Crear frame scrollable dentro del canvas
        self.scrollable_frame = EstiloUtils.crear_frame_con_estilo(self.canvas)
        self.canvas_window = self.canvas.create_window(
            (0, 0), 
            window=self.scrollable_frame, 
            anchor="nw"
        )
        
        # Configurar eventos de scroll
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Habilitar scroll con rueda del mouse
        self._bind_mousewheel()
    
    def _on_scrollbar_update(self, *args):
        """Callback para actualizar el scrollbar - siempre lo mantiene visible"""
        # Actualizar el scrollbar
        self.scrollbar.set(*args)
    
    def _on_frame_configure(self, event):
        """Actualiza la región de scroll cuando el frame cambia de tamaño"""
        # Actualizar scrollregion
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Ajusta el ancho del frame scrollable al canvas"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def _bind_mousewheel(self):
        """Vincula el scroll del mouse al canvas"""
        def _on_mousewheel(event):
            # Solo procesar si el mouse está sobre el canvas o el frame scrollable
            widget = event.widget
            if widget == self.canvas or widget == self.scrollable_frame or widget.master == self.canvas:
                # Windows y MacOS
                if event.delta:
                    self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                # Linux
                elif event.num == 4:
                    self.canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    self.canvas.yview_scroll(1, "units")
        
        def _on_enter(event):
            # Cuando el mouse entra al canvas, vincular eventos
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
            self.canvas.bind_all("<Button-4>", _on_mousewheel)
            self.canvas.bind_all("<Button-5>", _on_mousewheel)
        
        def _on_leave(event):
            # Cuando el mouse sale del canvas, desvincular eventos
            self.canvas.unbind_all("<MouseWheel>")
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        
        # Vincular eventos de entrada y salida del canvas
        self.canvas.bind("<Enter>", _on_enter)
        self.canvas.bind("<Leave>", _on_leave)
        self.scrollable_frame.bind("<Enter>", _on_enter)
        self.scrollable_frame.bind("<Leave>", _on_leave)
    
    def _crear_seccion_estado_simulacion(self):
        """Crea la sección de estado de la simulación"""
        # Título de sección
        titulo_frame = EstiloUtils.crear_frame_con_estilo(self.scrollable_frame)
        titulo_frame.grid(row=0, column=0, columnspan=4, sticky=tk.W+tk.E, padx=5, pady=(5, 10))
        
        ttk.Label(titulo_frame, text="⚡ ESTADO DE SIMULACIÓN", 
                 font=EstiloUtils.FUENTES['subtitulo']).pack(anchor=tk.W)
        
        # Fila 1: Estado y tiempo
        ttk.Label(self.scrollable_frame, text="Estado:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.stats_labels['estado_simulacion'] = EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame, "DETENIDO", 'Info.TLabel'
        )
        self.stats_labels['estado_simulacion'].grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=2)
        
        ttk.Label(self.scrollable_frame, text="Tiempo Actual:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.stats_labels['tiempo_actual'] = EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame, "0.0s", 'Info.TLabel'
        )
        self.stats_labels['tiempo_actual'].grid(row=1, column=3, sticky=tk.W, padx=(0, 20), pady=2)
    
    def _crear_contenido_estadisticas(self):
        """Crea el contenido principal del panel de estadísticas con mejor organización"""
        if not self.scrollable_frame:
            return
        
        # Configurar grid responsivo en el frame scrollable
        EstiloUtils.configurar_grid_responsivo(self.scrollable_frame, 4)
        
        # Crear secciones de estadísticas organizadas (solo tiempo y ciclistas)
        self._crear_seccion_estado_simulacion()
        self._crear_seccion_estadisticas_basicas()
        self._crear_seccion_estadisticas_rutas()
        self._crear_seccion_estadisticas_adicionales()
        
        # Actualizar scroll después de crear contenido
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _crear_seccion_estadisticas_basicas(self):
        """Crea la sección de estadísticas básicas"""
        # Título de sección
        titulo_frame = EstiloUtils.crear_frame_con_estilo(self.scrollable_frame)
        titulo_frame.grid(row=2, column=0, columnspan=4, sticky=tk.W+tk.E, padx=5, pady=(15, 5))
        
        ttk.Label(titulo_frame, text="🚴 ESTADÍSTICAS BÁSICAS", 
                 font=EstiloUtils.FUENTES['subtitulo']).pack(anchor=tk.W)
        
        # Fila 1: Ciclistas y velocidades
        ttk.Label(self.scrollable_frame, text="Ciclistas Activos:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.stats_labels['total_ciclistas'] = EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame, "0", 'Info.TLabel'
        )
        self.stats_labels['total_ciclistas'].grid(row=3, column=1, sticky=tk.W, padx=(0, 20), pady=2)
        
        ttk.Label(self.scrollable_frame, text="Velocidad Promedio:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=3, column=2, sticky=tk.W, padx=5, pady=2)
        self.stats_labels['velocidad_promedio'] = EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame, "0.0 m/s", 'Info.TLabel'
        )
        self.stats_labels['velocidad_promedio'].grid(row=3, column=3, sticky=tk.W, padx=(0, 20), pady=2)
        
        # Fila 2: Velocidades min/max
        ttk.Label(self.scrollable_frame, text="Velocidad Mín:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.stats_labels['velocidad_min'] = EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame, "0.0 m/s", 'Info.TLabel'
        )
        self.stats_labels['velocidad_min'].grid(row=4, column=1, sticky=tk.W, padx=(0, 20), pady=2)
        
        ttk.Label(self.scrollable_frame, text="Velocidad Máx:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=4, column=2, sticky=tk.W, padx=5, pady=2)
        self.stats_labels['velocidad_max'] = EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame, "0.0 m/s", 'Info.TLabel'
        )
        self.stats_labels['velocidad_max'].grid(row=4, column=3, sticky=tk.W, padx=(0, 20), pady=2)
    
    def _crear_seccion_estadisticas_grafo(self):
        """Crea la sección de estadísticas del grafo"""
        # Título de sección
        titulo_frame = EstiloUtils.crear_frame_con_estilo(self.scrollable_frame)
        titulo_frame.grid(row=3, column=0, columnspan=4, sticky=tk.W+tk.E, padx=5, pady=(15, 5))
        
        ttk.Label(titulo_frame, text="🕸️ ESTADÍSTICAS DEL GRAFO", 
                 font=EstiloUtils.FUENTES['subtitulo']).pack(anchor=tk.W)
        
        # Fila 1: Nodos y arcos
        ttk.Label(self.scrollable_frame, text="Nodos del Grafo:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.stats_labels['grafo_nodos'] = EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame, "0", 'Info.TLabel'
        )
        self.stats_labels['grafo_nodos'].grid(row=4, column=1, sticky=tk.W, padx=(0, 20), pady=2)
        
        ttk.Label(self.scrollable_frame, text="Arcos del Grafo:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=4, column=2, sticky=tk.W, padx=5, pady=2)
        self.stats_labels['grafo_arcos'] = EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame, "0", 'Info.TLabel'
        )
        self.stats_labels['grafo_arcos'].grid(row=4, column=3, sticky=tk.W, padx=(0, 20), pady=2)
        
        # Fila 2: Modo de simulación
        ttk.Label(self.scrollable_frame, text="Modo de Simulación:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        self.stats_labels['modo_simulacion'] = EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame, "Original", 'Info.TLabel'
        )
        self.stats_labels['modo_simulacion'].grid(row=5, column=1, sticky=tk.W, padx=(0, 20), pady=2)
    
    def _crear_seccion_estadisticas_distribuciones(self):
        """Crea la sección de estadísticas de distribuciones"""
        # Título de sección
        titulo_frame = EstiloUtils.crear_frame_con_estilo(self.scrollable_frame)
        titulo_frame.grid(row=6, column=0, columnspan=4, sticky=tk.W+tk.E, padx=5, pady=(15, 5))
        
        ttk.Label(titulo_frame, text="📊 DISTRIBUCIONES DE PROBABILIDAD", 
                 font=EstiloUtils.FUENTES['subtitulo']).pack(anchor=tk.W)
        
        # Fila 1: Distribuciones y tasa
        ttk.Label(self.scrollable_frame, text="Distribuciones Configuradas:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=7, column=0, sticky=tk.W, padx=5, pady=2)
        self.stats_labels['distribuciones_configuradas'] = EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame, "0", 'Info.TLabel'
        )
        self.stats_labels['distribuciones_configuradas'].grid(row=7, column=1, sticky=tk.W, padx=(0, 20), pady=2)
        
        ttk.Label(self.scrollable_frame, text="Tasa de Arribo Promedio:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=7, column=2, sticky=tk.W, padx=5, pady=2)
        self.stats_labels['tasa_arribo_promedio'] = EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame, "0.0", 'Info.TLabel'
        )
        self.stats_labels['tasa_arribo_promedio'].grid(row=7, column=3, sticky=tk.W, padx=(0, 20), pady=2)
        
        # Fila 2: Duración
        ttk.Label(self.scrollable_frame, text="Duración de Simulación:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=8, column=0, sticky=tk.W, padx=5, pady=2)
        self.stats_labels['duracion_simulacion'] = EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame, "300s", 'Info.TLabel'
        )
        self.stats_labels['duracion_simulacion'].grid(row=8, column=1, sticky=tk.W, padx=(0, 20), pady=2)
    
    def _crear_seccion_estadisticas_rutas(self):
        """Crea la sección de estadísticas de rutas"""
        # Título de sección
        titulo_frame = EstiloUtils.crear_frame_con_estilo(self.scrollable_frame)
        titulo_frame.grid(row=5, column=0, columnspan=4, sticky=tk.W+tk.E, padx=5, pady=(15, 5))
        
        ttk.Label(titulo_frame, text="🛣️ ESTADÍSTICAS DE RUTAS", 
                 font=EstiloUtils.FUENTES['subtitulo']).pack(anchor=tk.W)
        
        # Fila 1: Rutas utilizadas y total viajes
        ttk.Label(self.scrollable_frame, text="Rutas Utilizadas:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=6, column=0, sticky=tk.W, padx=5, pady=2)
        self.stats_labels['rutas_utilizadas'] = EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame, "0", 'Info.TLabel'
        )
        self.stats_labels['rutas_utilizadas'].grid(row=6, column=1, sticky=tk.W, padx=(0, 20), pady=2)
        
        ttk.Label(self.scrollable_frame, text="Total Viajes:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=6, column=2, sticky=tk.W, padx=5, pady=2)
        self.stats_labels['total_viajes'] = EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame, "0", 'Info.TLabel'
        )
        self.stats_labels['total_viajes'].grid(row=6, column=3, sticky=tk.W, padx=(0, 20), pady=2)
        
        # Fila 2: Ruta más usada
        ttk.Label(self.scrollable_frame, text="Ruta Más Usada:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=7, column=0, sticky=tk.W, padx=5, pady=2)
        self.stats_labels['ruta_mas_usada'] = EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame, "N/A", 'Info.TLabel'
        )
        self.stats_labels['ruta_mas_usada'].grid(row=7, column=1, columnspan=3, sticky=tk.W, padx=(0, 20), pady=2)
        
        # Fila 3: Tramo más concurrido (NUEVA ESTADÍSTICA)
        ttk.Label(self.scrollable_frame, text="Tramo Más Concurrido:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=8, column=0, sticky=tk.W, padx=5, pady=2)
        self.stats_labels['tramo_mas_concurrido'] = EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame, "N/A", 'Info.TLabel'
        )
        self.stats_labels['tramo_mas_concurrido'].grid(row=8, column=1, columnspan=3, sticky=tk.W, padx=(0, 20), pady=2)
    
    def _crear_seccion_estadisticas_adicionales(self):
        """Crea la sección de estadísticas adicionales"""
        # Título de sección
        titulo_frame = EstiloUtils.crear_frame_con_estilo(self.scrollable_frame)
        titulo_frame.grid(row=9, column=0, columnspan=4, sticky=tk.W+tk.E, padx=5, pady=(15, 5))
        
        ttk.Label(titulo_frame, text="📈 ESTADÍSTICAS ADICIONALES", 
                 font=EstiloUtils.FUENTES['subtitulo']).pack(anchor=tk.W)
        
        # Fila 1: Ciclistas completados y nodo más activo
        ttk.Label(self.scrollable_frame, text="Ciclistas Completados:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=10, column=0, sticky=tk.W, padx=5, pady=2)
        self.stats_labels['ciclistas_completados'] = EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame, "0", 'Success.TLabel'
        )
        self.stats_labels['ciclistas_completados'].grid(row=10, column=1, sticky=tk.W, padx=(0, 20), pady=2)
        
        ttk.Label(self.scrollable_frame, text="Nodo Más Activo:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=10, column=2, sticky=tk.W, padx=5, pady=2)
        self.stats_labels['nodo_mas_activo'] = EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame, "N/A", 'Info.TLabel'
        )
        self.stats_labels['nodo_mas_activo'].grid(row=10, column=3, sticky=tk.W, padx=(0, 20), pady=2)
    
    
    def actualizar_estadisticas(self, stats: Dict[str, Any]):
        """Actualiza las estadísticas mostradas con validación mejorada"""
        try:
            # Validar que stats no sea None
            if not stats:
                print("⚠️ Advertencia: No se recibieron estadísticas para actualizar")
                return
            
            # Estado de simulación
            estado = stats.get('estado_simulacion', 'detenido').upper()
            self._actualizar_estadistica('estado_simulacion', estado, 
                                       'exito' if estado == 'EJECUTANDO' else 'info')
            tiempo_actual = self._validar_numero(stats.get('tiempo_actual', 0))
            self._actualizar_estadistica('tiempo_actual', f"{tiempo_actual:.1f}s")
            
            # Estadísticas básicas con validación
            self._actualizar_estadistica('total_ciclistas', self._validar_numero(stats.get('ciclistas_activos', 0)))
            self._actualizar_estadistica('velocidad_promedio', f"{self._validar_velocidad(stats.get('velocidad_promedio', 0)):.1f} m/s")
            self._actualizar_estadistica('velocidad_min', f"{self._validar_velocidad(stats.get('velocidad_minima', 0)):.1f} m/s")
            self._actualizar_estadistica('velocidad_max', f"{self._validar_velocidad(stats.get('velocidad_maxima', 0)):.1f} m/s")
            self._actualizar_estadistica('duracion_simulacion', f"{self._validar_numero(stats.get('duracion_simulacion', 300)):.0f}s")
            
            # No mostrar estadísticas del grafo ni distribuciones (eliminadas)
            
            # Estadísticas de rutas
            self._actualizar_estadistica('rutas_utilizadas', self._validar_numero(stats.get('rutas_utilizadas', 0)))
            self._actualizar_estadistica('total_viajes', self._validar_numero(stats.get('total_viajes', 0)))
            
            # Ruta más usada (truncar si es muy larga)
            ruta_mas_usada = stats.get('ruta_mas_usada', 'N/A')
            if isinstance(ruta_mas_usada, str) and len(ruta_mas_usada) > 30:
                ruta_mas_usada = ruta_mas_usada[:27] + "..."
            self._actualizar_estadistica('ruta_mas_usada', str(ruta_mas_usada))
            
            # Tramo más concurrido (NUEVA ESTADÍSTICA)
            tramo_mas_concurrido = stats.get('tramo_mas_concurrido', 'N/A')
            if isinstance(tramo_mas_concurrido, str) and len(tramo_mas_concurrido) > 30:
                tramo_mas_concurrido = tramo_mas_concurrido[:27] + "..."
            self._actualizar_estadistica('tramo_mas_concurrido', str(tramo_mas_concurrido))
            
            # Ciclistas completados
            self._actualizar_estadistica('ciclistas_completados', self._validar_numero(stats.get('ciclistas_completados', 0)), 'exito')
            
            # Nodo más activo (truncar si es muy largo)
            nodo_mas_activo = stats.get('nodo_mas_activo', 'N/A')
            if isinstance(nodo_mas_activo, str) and len(nodo_mas_activo) > 25:
                nodo_mas_activo = nodo_mas_activo[:22] + "..."
            self._actualizar_estadistica('nodo_mas_activo', str(nodo_mas_activo))
            
            # No se actualizan atributos ni perfiles (eliminados)
            
        except Exception as e:
            print(f"⚠️ Error actualizando estadísticas: {e}")
            # Mostrar valores por defecto en caso de error
            self._mostrar_valores_por_defecto()
    
    def _validar_numero(self, valor: Any) -> float:
        """Valida y convierte un valor a número"""
        try:
            if valor is None:
                return 0.0
            return float(valor)
        except (ValueError, TypeError):
            return 0.0
    
    def _validar_velocidad(self, valor: Any) -> float:
        """Valida y convierte un valor de velocidad"""
        try:
            if valor is None:
                return 0.0
            vel = float(valor)
            # Asegurar que la velocidad esté en un rango razonable
            return max(0.0, min(vel, 50.0))  # Entre 0 y 50 m/s
        except (ValueError, TypeError):
            return 0.0
    
    def _mostrar_valores_por_defecto(self):
        """Muestra valores por defecto en caso de error"""
        valores_por_defecto = {
            'total_ciclistas': "0",
            'velocidad_promedio': "0.0 m/s",
            'velocidad_min': "0.0 m/s",
            'velocidad_max': "0.0 m/s",
            'grafo_nodos': "0",
            'grafo_arcos': "0",
            'modo_simulacion': "Error",
            'distribuciones_configuradas': "0",
            'tasa_arribo_promedio': "0.0",
            'duracion_simulacion': "300s",
            'rutas_utilizadas': "0",
            'total_viajes': "0",
            'ruta_mas_usada': "N/A",
            'ciclistas_completados': "0",
            'nodo_mas_activo': "N/A",
            'atributos_disponibles': "0",
            'peso_compuesto': "Error",
            'perfiles_disponibles': "0",
            'matriz_rutas': "No"
        }
        
        for key, valor in valores_por_defecto.items():
            if key in self.stats_labels:
                self.stats_labels[key].config(text=valor)
    
    def _actualizar_estadistica(self, key: str, valor: Any, tipo: str = 'normal'):
        """Actualiza una estadística específica"""
        if key in self.stats_labels:
            EstiloUtils.aplicar_estilo_estadistica(self.stats_labels[key], valor, tipo)
    
    
    def limpiar_estadisticas(self):
        """Limpia todas las estadísticas"""
        valores_por_defecto = {
            'estado_simulacion': "DETENIDO",
            'tiempo_actual': "0.0s",
            'total_ciclistas': "0",
            'velocidad_promedio': "0.0 m/s",
            'velocidad_min': "0.0 m/s",
            'velocidad_max': "0.0 m/s",
            'duracion_simulacion': "300s",
            'rutas_utilizadas': "0",
            'total_viajes': "0",
            'ruta_mas_usada': "N/A",
            'tramo_mas_concurrido': "N/A",
            'ciclistas_completados': "0",
            'nodo_mas_activo': "N/A"
        }
        
        for key, valor in valores_por_defecto.items():
            if key in self.stats_labels:
                self.stats_labels[key].config(text=valor)
        
        # Actualizar scroll después de limpiar
        if self.canvas:
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def obtener_estadisticas_actuales(self) -> Dict[str, str]:
        """Retorna las estadísticas actuales mostradas"""
        return {key: label.cget('text') for key, label in self.stats_labels.items()}
    
    def exportar_estadisticas(self):
        """Exporta las estadísticas actuales"""
        if 'exportar_estadisticas' in self.callbacks:
            self.callbacks['exportar_estadisticas']()
    
    def establecer_grafo_actual(self, grafo_actual, perfiles_df=None, rutas_df=None):
        """Establece referencias al grafo y datos para estadísticas"""
        self.grafo_actual = grafo_actual
        self.perfiles_df = perfiles_df
        self.rutas_df = rutas_df
    
    def obtener_estado_panel(self) -> Dict[str, Any]:
        """Retorna el estado actual del panel"""
        return {
            'estadisticas': self.obtener_estadisticas_actuales(),
            'num_labels': len(self.stats_labels)
        }
    
    def configurar_modo_compacto(self, compacto: bool = True):
        """Configura el panel en modo compacto o expandido"""
        if compacto:
            # Modo compacto: mostrar solo estadísticas esenciales
            self._mostrar_estadisticas_esenciales()
        else:
            # Modo expandido: mostrar todas las estadísticas
            self._mostrar_todas_estadisticas()
        
        # Actualizar scroll después de cambiar modo
        if self.canvas:
            self.scrollable_frame.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _mostrar_estadisticas_esenciales(self):
        """Muestra solo las estadísticas más importantes"""
        # Ocultar secciones menos importantes
        secciones_ocultar = [
            'atributos_disponibles', 'peso_compuesto',
            'perfiles_disponibles', 'matriz_rutas'
        ]
        
        for key in secciones_ocultar:
            if key in self.stats_labels:
                # Ocultar el label y su etiqueta
                self.stats_labels[key].pack_forget()
    
    def _mostrar_todas_estadisticas(self):
        """Muestra todas las estadísticas"""
        # Recrear el contenido completo
        self._crear_contenido_estadisticas()
    
    def ajustar_tamaño_responsivo(self, ancho_ventana: int, alto_ventana: int):
        """Ajusta el tamaño del panel según las dimensiones de la ventana"""
        # El panel ahora es redimensionable, no se configura altura fija
        # Solo actualizar scroll después de cambiar tamaño
        if self.canvas:
            self.scrollable_frame.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
