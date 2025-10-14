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
        
        # Crear el panel
        self.crear_panel()
    
    def crear_panel(self):
        """Crea el panel de control principal"""
        # Frame principal
        self.frame_principal = EstiloUtils.crear_label_frame_con_estilo(
            self.parent, 
            "⚙️ CONFIGURACIÓN DE SIMULACIÓN"
        )
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Crear secciones del panel
        self._crear_seccion_velocidades()
        self._crear_separador()
        self._crear_seccion_grafo()
        self._crear_separador()
        self._crear_seccion_control_simulacion()
        self._crear_separador()
        self._crear_seccion_estado()
    
    def _crear_seccion_velocidades(self):
        """Crea la sección de configuración de velocidades"""
        # Título
        EstiloUtils.crear_label_con_estilo(
            self.frame_principal,
            "⚡ CONFIGURACIÓN DE VELOCIDADES",
            'Subheader.TLabel'
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Frame para controles de velocidad
        vel_frame = EstiloUtils.crear_frame_con_estilo(self.frame_principal)
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
    
    def _crear_seccion_grafo(self):
        """Crea la sección de información del grafo"""
        # Título
        EstiloUtils.crear_label_con_estilo(
            self.frame_principal,
            "📊 Configuración de Red:",
            'Subheader.TLabel'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Información del grafo
        self.info_grafo_label = EstiloUtils.crear_label_con_estilo(
            self.frame_principal,
            "Sin grafo cargado",
            'Info.TLabel'
        )
        self.info_grafo_label.pack(anchor=tk.W, pady=2)
        
        # Botón para cargar grafo
        EstiloUtils.crear_button_con_estilo(
            self.frame_principal,
            "📂 CARGAR GRAFO",
            'TButton',
            command=self._cargar_grafo
        ).pack(fill=tk.X, pady=5)
    
    def _crear_seccion_control_simulacion(self):
        """Crea la sección de control de simulación"""
        # Título
        EstiloUtils.crear_label_con_estilo(
            self.frame_principal,
            "🎮 CONTROL DE SIMULACIÓN",
            'Subheader.TLabel'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Frame para botones en grid
        control_frame = EstiloUtils.crear_frame_con_estilo(self.frame_principal)
        control_frame.pack(fill=tk.X, pady=5)
        
        # Configurar grid
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)
        
        # Botones principales
        botones_config = [
            ("🔄 NUEVA", 'Accent.TButton', self._nueva_simulacion, 0, 0, 2),
            ("▶️ INICIAR", 'Success.TButton', self._iniciar_simulacion, 1, 0, 1),
            ("⏸️ PAUSAR", 'Warning.TButton', self._pausar_simulacion, 1, 1, 1),
            ("🏁 TERMINAR", 'Danger.TButton', self._terminar_simulacion, 2, 0, 1),
            ("⏭️ ADELANTAR", 'TButton', self._adelantar_simulacion, 2, 1, 1),
            ("🔄 REINICIAR", 'Accent.TButton', self._reiniciar_simulacion, 3, 0, 2)
        ]
        
        for texto, estilo, comando, fila, col, colspan in botones_config:
            btn = EstiloUtils.crear_button_con_estilo(
                control_frame, texto, estilo, command=comando
            )
            btn.grid(row=fila, column=col, columnspan=colspan, 
                    sticky=(tk.W, tk.E), pady=2, padx=2)
    
    def _crear_seccion_estado(self):
        """Crea la sección de estado de la simulación"""
        # Título
        EstiloUtils.crear_label_con_estilo(
            self.frame_principal,
            "📊 ESTADO DE SIMULACIÓN",
            'Subheader.TLabel'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Frame para información de estado
        estado_frame = EstiloUtils.crear_frame_con_estilo(self.frame_principal)
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
        EstiloUtils.crear_separador(self.frame_principal).pack(fill=tk.X, pady=10)
    
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
    
    def habilitar_controles(self, habilitado: bool = True):
        """Habilita o deshabilita los controles del panel"""
        estado = 'normal' if habilitado else 'disabled'
        
        # Habilitar/deshabilitar spinboxes de velocidad
        for widget in self.frame_principal.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Spinbox):
                        child.config(state=estado)
    
    def resetear_boton_pausa(self):
        """Resetea el botón de pausa al estado original"""
        # Buscar y resetear el botón de pausa
        for widget in self.frame_principal.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button) and "REANUDAR" in child.cget("text"):
                        child.configure(text="⏸️ PAUSAR", style='Warning.TButton')
    
    def obtener_estado_panel(self) -> Dict[str, Any]:
        """Retorna el estado actual del panel"""
        return {
            'velocidad_min': self.vel_min_var.get(),
            'velocidad_max': self.vel_max_var.get(),
            'info_grafo': self.info_grafo_label.cget('text'),
            'estado_simulacion': self.estado_label.cget('text'),
            'tiempo_actual': self.tiempo_label.cget('text')
        }
