"""
Panel de control principal de la simulación.

Este módulo contiene el panel de control con parámetros configurables
y botones de control de la simulación.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Any

from ..utils.estilo_utils import EstiloUtils


class PanelControl:
    """Panel de control con parámetros y botones de simulación"""
    
    def __init__(self, parent, callbacks: Dict[str, Callable]):
        self.parent = parent
        self.callbacks = callbacks
        
        # Variables de control
        self.vel_min_var = tk.DoubleVar(value=10.0)
        self.vel_max_var = tk.DoubleVar(value=15.0)
        self.duracion_var = tk.DoubleVar(value=300.0)  # Duración por defecto: 300 segundos
        
        # Variables para scroll
        self.canvas = None
        self.scrollbar = None
        self.scrollable_frame = None
        
        # Crear el panel
        self.crear_panel()
    
    def crear_panel(self):
        """Crea el panel de control principal con scroll"""
        # Frame principal
        self.frame_principal = EstiloUtils.crear_label_frame_con_estilo(
            self.parent, 
            "⚙️ CONFIGURACIÓN DE SIMULACIÓN"
        )
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Crear sistema de scroll
        self._crear_sistema_scroll()
        
        # Crear secciones del panel dentro del frame scrollable
        self._crear_seccion_velocidades()
        self._crear_separador()
        self._crear_seccion_duracion()
        self._crear_separador()
        self._crear_seccion_grafo()
        self._crear_separador()
        self._crear_seccion_control_simulacion()
        self._crear_separador()
        self._crear_seccion_estado()
    
    def _crear_sistema_scroll(self):
        """Crea el sistema de scroll para el panel de control"""
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
    
    def _crear_seccion_velocidades(self):
        """Crea la sección de configuración de velocidades"""
        # Título
        EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame,
            "⚡ CONFIGURACIÓN DE VELOCIDADES",
            'Subheader.TLabel'
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Frame para controles de velocidad
        vel_frame = EstiloUtils.crear_frame_con_estilo(self.scrollable_frame)
        vel_frame.pack(fill=tk.X, pady=5)
        
        # Velocidad mínima
        ttk.Label(vel_frame, text="Velocidad Mínima (m/s):", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=0, column=0, sticky=tk.W, pady=5)
        vel_min_spin = ttk.Spinbox(vel_frame, from_=1.0, to=20.0, increment=0.5, 
                                  textvariable=self.vel_min_var, width=10)
        vel_min_spin.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Velocidad máxima
        ttk.Label(vel_frame, text="Velocidad Máxima (m/s):", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=1, column=0, sticky=tk.W, pady=5)
        vel_max_spin = ttk.Spinbox(vel_frame, from_=1.0, to=30.0, increment=0.5, 
                                  textvariable=self.vel_max_var, width=10)
        vel_max_spin.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Botón para aplicar cambios
        EstiloUtils.crear_button_con_estilo(
            vel_frame, 
            "✅ Aplicar Velocidades",
            'Accent.TButton',
            command=self._aplicar_velocidades
        ).grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
    
    def _crear_seccion_duracion(self):
        """Crea la sección de configuración de duración de simulación"""
        # Título
        EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame,
            "⏱️ DURACIÓN DE SIMULACIÓN",
            'Subheader.TLabel'
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Frame para controles de duración
        duracion_frame = EstiloUtils.crear_frame_con_estilo(self.scrollable_frame)
        duracion_frame.pack(fill=tk.X, pady=5)
        
        # Duración de simulación
        ttk.Label(duracion_frame, text="Duración (segundos):", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=0, column=0, sticky=tk.W, pady=5)
        duracion_spin = ttk.Spinbox(duracion_frame, from_=60.0, to=1800.0, increment=30.0, 
                                   textvariable=self.duracion_var, width=10)
        duracion_spin.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Etiqueta informativa con límite máximo
        info_label = ttk.Label(duracion_frame, 
                              text="(Mín: 60s, Máx: 1800s / 30 min)", 
                              font=EstiloUtils.FUENTES['pequeno'],
                              foreground='gray')
        info_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        # Botón para aplicar cambios
        EstiloUtils.crear_button_con_estilo(
            duracion_frame, 
            "✅ Aplicar Duración",
            'Accent.TButton',
            command=self._aplicar_duracion
        ).grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
    
    def _crear_seccion_grafo(self):
        """Crea la sección de información del grafo"""
        # Título
        EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame,
            "📊 Configuración de Red:",
            'Subheader.TLabel'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Información del grafo
        self.info_grafo_label = EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame,
            "Sin grafo cargado",
            'Info.TLabel'
        )
        self.info_grafo_label.pack(anchor=tk.W, pady=2)
        
        # Botón para cargar grafo
        EstiloUtils.crear_button_con_estilo(
            self.scrollable_frame,
            "📂 CARGAR GRAFO",
            'TButton',
            command=self._cargar_grafo
        ).pack(fill=tk.X, pady=5)
    
    def _crear_seccion_control_simulacion(self):
        """Crea la sección de control de simulación"""
        # Título
        EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame,
            "🎮 CONTROL DE SIMULACIÓN",
            'Subheader.TLabel'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Frame para botones en grid
        control_frame = EstiloUtils.crear_frame_con_estilo(self.scrollable_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        # Configurar grid
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)
        
        # Botones principales - guardar referencias para control de estado
        botones_config = [
            ("🔄 NUEVA", 'Accent.TButton', self._nueva_simulacion, 0, 0, 2, 'nueva'),
            ("▶️ INICIAR", 'Success.TButton', self._iniciar_simulacion, 1, 0, 1, 'iniciar'),
            ("⏸️ PAUSAR", 'Warning.TButton', self._pausar_simulacion, 1, 1, 1, 'pausar'),
            ("🏁 TERMINAR", 'Danger.TButton', self._terminar_simulacion, 2, 0, 1, 'terminar'),
            ("⏭️ ADELANTAR", 'TButton', self._adelantar_simulacion, 2, 1, 1, 'adelantar'),
            ("🔄 REINICIAR", 'Accent.TButton', self._reiniciar_simulacion, 3, 0, 2, 'reiniciar')
        ]
        
        # Diccionario para almacenar referencias a los botones
        self.botones_control = {}
        
        for texto, estilo, comando, fila, col, colspan, nombre in botones_config:
            btn = EstiloUtils.crear_button_con_estilo(
                control_frame, texto, estilo, command=comando
            )
            btn.grid(row=fila, column=col, columnspan=colspan, 
                    sticky=(tk.W, tk.E), pady=2, padx=2)
            # Guardar referencia al botón
            self.botones_control[nombre] = btn
    
    def _crear_seccion_estado(self):
        """Crea la sección de estado de la simulación"""
        # Título
        EstiloUtils.crear_label_con_estilo(
            self.scrollable_frame,
            "📊 ESTADO DE SIMULACIÓN",
            'Subheader.TLabel'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Frame para información de estado
        estado_frame = EstiloUtils.crear_frame_con_estilo(self.scrollable_frame)
        estado_frame.pack(fill=tk.X, pady=5)
        
        # Estado de la simulación
        ttk.Label(estado_frame, text="Estado:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.estado_label = EstiloUtils.crear_label_con_estilo(
            estado_frame, "DETENIDO", 'Danger.TLabel'
        )
        self.estado_label.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Tiempo actual
        ttk.Label(estado_frame, text="Tiempo:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.tiempo_label = EstiloUtils.crear_label_con_estilo(
            estado_frame, "0.0s", 'Info.TLabel'
        )
        self.tiempo_label.grid(row=1, column=1, sticky=tk.W, pady=2, padx=(5, 0))
    
    def _crear_separador(self):
        """Crea un separador visual"""
        EstiloUtils.crear_separador(self.scrollable_frame).pack(fill=tk.X, pady=10)
    
    def _aplicar_velocidades(self):
        """Aplica los cambios de velocidad configurados"""
        try:
            vel_min = self.vel_min_var.get()
            vel_max = self.vel_max_var.get()
            
            # Validar velocidades
            if vel_min >= vel_max:
                messagebox.showerror("Error", "La velocidad mínima debe ser menor que la máxima")
                return
            
            if vel_min < 0 or vel_max < 0:
                messagebox.showerror("Error", "Las velocidades no pueden ser negativas")
                return
            
            # Llamar callback para aplicar velocidades
            if 'aplicar_velocidades' in self.callbacks:
                self.callbacks['aplicar_velocidades'](vel_min, vel_max)
            
            # Mostrar mensaje de confirmación
            messagebox.showinfo("Velocidades Aplicadas", 
                              f"✅ Velocidades actualizadas:\n"
                              f"   Mínima: {vel_min:.1f} m/s\n"
                              f"   Máxima: {vel_max:.1f} m/s\n\n"
                              f"Los cambios se aplicarán en la próxima simulación.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar velocidades: {str(e)}")
    
    def _aplicar_duracion(self):
        """Aplica los cambios de duración configurados"""
        try:
            duracion = self.duracion_var.get()
            
            # Validar duración
            if duracion < 60.0:
                messagebox.showerror("Error", 
                                   "La duración mínima es de 60 segundos (1 minuto)")
                return
            
            # Límite máximo para evitar colapsar el código en máquinas locales
            DURACION_MAXIMA = 1800.0  # 30 minutos
            if duracion > DURACION_MAXIMA:
                messagebox.showerror("Error", 
                                   f"La duración máxima permitida es de {DURACION_MAXIMA:.0f} segundos "
                                   f"({DURACION_MAXIMA/60:.0f} minutos) para evitar problemas de rendimiento "
                                   f"en máquinas locales.")
                # Restablecer al valor máximo
                self.duracion_var.set(DURACION_MAXIMA)
                return
            
            if duracion <= 0:
                messagebox.showerror("Error", "La duración debe ser positiva")
                return
            
            # Llamar callback para aplicar duración
            if 'aplicar_duracion' in self.callbacks:
                self.callbacks['aplicar_duracion'](duracion)
            
            # Mostrar mensaje de confirmación
            minutos = duracion / 60.0
            messagebox.showinfo("Duración Aplicada", 
                              f"✅ Duración actualizada:\n"
                              f"   {duracion:.0f} segundos ({minutos:.1f} minutos)\n\n"
                              f"Los cambios se aplicarán en la próxima simulación.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar duración: {str(e)}")
    
    def _cargar_grafo(self):
        """Maneja la carga de grafo"""
        if 'cargar_grafo' in self.callbacks:
            self.callbacks['cargar_grafo']()
    
    def _nueva_simulacion(self):
        """Maneja la creación de nueva simulación"""
        if 'nueva_simulacion' in self.callbacks:
            self.callbacks['nueva_simulacion']()
    
    def _iniciar_simulacion(self):
        """Maneja el inicio de simulación"""
        if 'iniciar_simulacion' in self.callbacks:
            self.callbacks['iniciar_simulacion']()
    
    def _pausar_simulacion(self):
        """Maneja la pausa/reanudación de simulación"""
        if 'pausar_simulacion' in self.callbacks:
            self.callbacks['pausar_simulacion']()
    
    def _terminar_simulacion(self):
        """Maneja la terminación de simulación"""
        if 'terminar_simulacion' in self.callbacks:
            self.callbacks['terminar_simulacion']()
    
    def _adelantar_simulacion(self):
        """Maneja el adelanto de simulación"""
        if 'adelantar_simulacion' in self.callbacks:
            self.callbacks['adelantar_simulacion']()
    
    def _reiniciar_simulacion(self):
        """Maneja el reinicio de simulación"""
        if 'reiniciar_simulacion' in self.callbacks:
            self.callbacks['reiniciar_simulacion']()
    
    def actualizar_info_grafo(self, info_grafo: str):
        """Actualiza la información del grafo mostrada"""
        self.info_grafo_label.config(text=info_grafo)
    
    def actualizar_estado(self, estado: str, tiempo: float):
        """Actualiza el estado y tiempo de la simulación"""
        # Actualizar estado con color correspondiente
        color = EstiloUtils.obtener_color_estado(estado)
        icono = EstiloUtils.obtener_icono_estado(estado)
        
        self.estado_label.config(text=f"{icono} {estado.upper()}", foreground=color)
        self.tiempo_label.config(text=f"{tiempo:.1f}s")
    
    def obtener_velocidades(self) -> tuple:
        """Retorna las velocidades configuradas"""
        return self.vel_min_var.get(), self.vel_max_var.get()
    
    def establecer_velocidades(self, vel_min: float, vel_max: float):
        """Establece las velocidades en los controles"""
        self.vel_min_var.set(vel_min)
        self.vel_max_var.set(vel_max)
    
    def obtener_duracion(self) -> float:
        """Retorna la duración configurada"""
        return self.duracion_var.get()
    
    def establecer_duracion(self, duracion: float):
        """Establece la duración en los controles"""
        # Validar que esté dentro del rango permitido
        if duracion < 60.0:
            duracion = 60.0
        elif duracion > 1800.0:
            duracion = 1800.0
        self.duracion_var.set(duracion)
    
    def habilitar_controles(self, habilitado: bool = True):
        """Habilita o deshabilita los controles del panel"""
        estado = 'normal' if habilitado else 'disabled'
        
        # Habilitar/deshabilitar spinboxes y botones en el frame scrollable
        def _habilitar_widgets(widget):
            if isinstance(widget, ttk.Spinbox):
                widget.config(state=estado)
            elif isinstance(widget, ttk.Button):
                widget.config(state=estado)
            elif isinstance(widget, tk.Widget):
                for child in widget.winfo_children():
                    _habilitar_widgets(child)
        
        if self.scrollable_frame:
            _habilitar_widgets(self.scrollable_frame)
    
    def resetear_boton_pausa(self):
        """Resetea el botón de pausa al estado original"""
        def _buscar_boton_pausa(widget):
            if isinstance(widget, ttk.Button) and "REANUDAR" in widget.cget("text"):
                widget.configure(text="⏸️ PAUSAR", style='Warning.TButton')
            elif isinstance(widget, tk.Widget):
                for child in widget.winfo_children():
                    _buscar_boton_pausa(child)
        
        if self.scrollable_frame:
            _buscar_boton_pausa(self.scrollable_frame)
    
    def obtener_estado_panel(self) -> Dict[str, Any]:
        """Retorna el estado actual del panel"""
        return {
            'velocidad_min': self.vel_min_var.get(),
            'velocidad_max': self.vel_max_var.get(),
            'duracion_simulacion': self.duracion_var.get(),
            'info_grafo': self.info_grafo_label.cget('text'),
            'estado_simulacion': self.estado_label.cget('text'),
            'tiempo_actual': self.tiempo_label.cget('text')
        }
    
    def bloquear_botones_simulacion_terminada(self):
        """Bloquea los botones de iniciar, pausar y adelantar cuando la simulación termina.
        Solo deja habilitados los botones de nueva y reiniciar."""
        if hasattr(self, 'botones_control'):
            # Bloquear: iniciar, pausar, terminar, adelantar
            botones_bloqueados = ['iniciar', 'pausar', 'terminar', 'adelantar']
            for nombre in botones_bloqueados:
                if nombre in self.botones_control:
                    self.botones_control[nombre].config(state='disabled')
            
            # Mantener habilitados: nueva y reiniciar
            botones_habilitados = ['nueva', 'reiniciar']
            for nombre in botones_habilitados:
                if nombre in self.botones_control:
                    self.botones_control[nombre].config(state='normal')
    
    def desbloquear_botones_simulacion(self):
        """Desbloquea todos los botones cuando se inicia una nueva simulación"""
        if hasattr(self, 'botones_control'):
            for nombre, boton in self.botones_control.items():
                boton.config(state='normal')
