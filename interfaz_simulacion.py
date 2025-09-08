import tkinter as tk
from tkinter import filedialog
import pandas as pd
import networkx as nx
from tkinter import ttk, messagebox
import threading
import time
from simulacion_ciclorutas import SimuladorCiclorutas, ConfiguracionSimulacion
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle
import numpy as np
from typing import Dict

class InterfazSimulacion:
    """Interfaz gráfica para controlar la simulación de ciclorutas"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🚴 Simulador de Ciclorutas - Control Avanzado")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f8f9fa')
        
        # Configuración por defecto
        self.config = ConfiguracionSimulacion()
        self.simulador = SimuladorCiclorutas(self.config)
        
        # Variables para el grafo
        self.grafo_actual = None
        self.pos_grafo_actual = None
        
        # Variables de control
        self.simulacion_activa = False
        self.hilo_simulacion = None
        
        # Configurar estilo
        self.configurar_estilo()
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Inicializar simulación
        self.simulador.inicializar_simulacion()
        self.actualizar_visualizacion()

        # Posiciones del grafo
        self.pos_grafo = None
        
    def configurar_estilo(self):
        """Configura el estilo visual de la interfaz"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores personalizados
        style.configure('TFrame', background='#f8f9fa')
        style.configure('TLabel', background='#f8f9fa', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#2E86AB')
        
    def crear_interfaz(self):
        """Crea todos los elementos de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=0)  # Estadísticas no expanden verticalmente
        
        # Crear PanedWindow para paneles redimensionables
        self.paned_main = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        self.paned_main.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Panel de control izquierdo
        self.crear_panel_control(self.paned_main)
        
        # Panel de distribuciones (centro)
        self.crear_panel_distribuciones(self.paned_main)
        
        # Panel de visualización (derecha)
        self.crear_panel_visualizacion(self.paned_main)
        
        # Panel de estadísticas (abajo) - fuera del PanedWindow para ancho completo
        self.crear_panel_estadisticas(main_frame)
        
    def crear_panel_control(self, parent):
        """Crea el panel de control de parámetros"""
        control_frame = ttk.LabelFrame(parent, text="⚙️ CONFIGURACIÓN DE SIMULACIÓN", padding="10")
        parent.add(control_frame, weight=1)
        
        # Configuración de velocidades
        ttk.Label(control_frame, text="⚡ CONFIGURACIÓN DE VELOCIDADES", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Velocidad mínima
        ttk.Label(control_frame, text="Velocidad Mínima (m/s):", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.vel_min_var = tk.DoubleVar(value=self.config.velocidad_min)
        vel_min_spin = ttk.Spinbox(control_frame, from_=1.0, to=20.0, increment=0.5, textvariable=self.vel_min_var, width=10)
        vel_min_spin.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Velocidad máxima
        ttk.Label(control_frame, text="Velocidad Máxima (m/s):", font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.vel_max_var = tk.DoubleVar(value=self.config.velocidad_max)
        vel_max_spin = ttk.Spinbox(control_frame, from_=1.0, to=30.0, increment=0.5, textvariable=self.vel_max_var, width=10)
        vel_max_spin.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Información sobre el grafo
        ttk.Label(control_frame, text="📊 Configuración de Red:", font=('Segoe UI', 10, 'bold')).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(15, 5))
        self.info_grafo_label = ttk.Label(control_frame, text="Sin grafo cargado", font=('Segoe UI', 9), foreground='#6c757d')
        self.info_grafo_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Separador
        ttk.Separator(control_frame, orient='horizontal').grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=15)
        
        # Sección de carga de grafo
        ttk.Label(control_frame, text="📂 GESTIÓN DE GRAFO", font=('Segoe UI', 10, 'bold')).grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        ttk.Button(control_frame, text='📂 CARGAR GRAFO', command=self.cargar_grafo).grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Separador
        ttk.Separator(control_frame, orient='horizontal').grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=15)
        
        # Sección de control de simulación
        ttk.Label(control_frame, text="🎮 CONTROL DE SIMULACIÓN", font=('Segoe UI', 10, 'bold')).grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        # Botones principales en dos columnas
        ttk.Button(control_frame, text="🔄 NUEVA", command=self.nueva_simulacion, 
                  style='Accent.TButton').grid(row=10, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Button(control_frame, text="▶️ INICIAR", command=self.iniciar_simulacion, 
                  style='Accent.TButton').grid(row=11, column=0, sticky=(tk.W, tk.E), pady=2, padx=(0, 2))
        
        ttk.Button(control_frame, text="⏸️ PAUSAR", command=self.pausar_simulacion, 
                  style='Accent.TButton').grid(row=11, column=1, sticky=(tk.W, tk.E), pady=2, padx=(2, 0))
        
        ttk.Button(control_frame, text="⏹️ DETENER", command=self.detener_simulacion, 
                  style='Accent.TButton').grid(row=12, column=0, sticky=(tk.W, tk.E), pady=2, padx=(0, 2))
        
        ttk.Button(control_frame, text="⏭️ ADELANTAR", command=self.adelantar_simulacion, 
                  style='Accent.TButton').grid(row=12, column=1, sticky=(tk.W, tk.E), pady=2, padx=(2, 0))
        
        ttk.Button(control_frame, text="🔄 REPRODUCIR", command=self.reiniciar_simulacion, 
                  style='Accent.TButton').grid(row=13, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # Separador
        ttk.Separator(control_frame, orient='horizontal').grid(row=14, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=15)
        
        # Sección de estado
        ttk.Label(control_frame, text="📊 ESTADO DE SIMULACIÓN", font=('Segoe UI', 10, 'bold')).grid(row=15, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        # Estado de la simulación
        ttk.Label(control_frame, text="Estado:", font=('Segoe UI', 9, 'bold')).grid(row=16, column=0, sticky=tk.W, pady=2)
        self.estado_label = ttk.Label(control_frame, text="DETENIDO", font=('Segoe UI', 9), foreground='#dc3545')
        self.estado_label.grid(row=16, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Tiempo actual
        ttk.Label(control_frame, text="Tiempo:", font=('Segoe UI', 9, 'bold')).grid(row=17, column=0, sticky=tk.W, pady=2)
        self.tiempo_label = ttk.Label(control_frame, text="0.0s", font=('Segoe UI', 9))
        self.tiempo_label.grid(row=17, column=1, sticky=tk.W, pady=2, padx=(5, 0))
    
    def crear_panel_distribuciones(self, parent):
        """Crea el panel de configuración de distribuciones por nodo"""
        dist_frame = ttk.LabelFrame(parent, text="📊 DISTRIBUCIONES DE ARRIBO", padding="10")
        parent.add(dist_frame, weight=1)
        
        # Frame para scroll - se ajusta al contenido
        canvas = tk.Canvas(dist_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(dist_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Función para actualizar el scroll y ajustar el tamaño
        def actualizar_scroll(event=None):
            # Actualizar región de scroll
            canvas.configure(scrollregion=canvas.bbox("all"))
            
            # Ajustar el tamaño del canvas al contenido si es necesario
            scrollable_frame.update_idletasks()
            frame_height = scrollable_frame.winfo_reqheight()
            canvas_height = canvas.winfo_height()
            
            # Si el contenido es menor que el canvas, ajustar el canvas
            if frame_height < canvas_height and frame_height > 0:
                canvas.configure(height=frame_height)
        
        scrollable_frame.bind("<Configure>", actualizar_scroll)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Variables para almacenar controles de distribuciones
        self.controles_distribuciones = {}
        
        # Mensaje inicial
        self.mensaje_distribuciones = ttk.Label(scrollable_frame, 
                                              text="📂 Carga un grafo para configurar distribuciones",
                                              font=('Segoe UI', 10), foreground='#6c757d')
        self.mensaje_distribuciones.pack(pady=20)
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Guardar referencias
        self.canvas_distribuciones = canvas
        self.frame_distribuciones = scrollable_frame
        
        # Función para ajustar el tamaño del panel
        def ajustar_tamano_panel():
            """Ajusta el tamaño del panel al contenido"""
            self.frame_distribuciones.update_idletasks()
            contenido_height = self.frame_distribuciones.winfo_reqheight()
            
            # Calcular altura basada en el número de nodos
            num_nodos = len(self.grafo_actual.nodes()) if self.grafo_actual else 0
            
            if num_nodos == 0:
                # Solo mensaje - altura mínima
                altura_optima = 150
            elif num_nodos <= 2:
                # Pocos nodos - altura pequeña
                altura_optima = 250
            elif num_nodos <= 4:
                # Nodos moderados - altura media
                altura_optima = 400
            else:
                # Muchos nodos - altura máxima con scroll
                altura_optima = 600
            
            # Aplicar la altura
            self.canvas_distribuciones.configure(height=altura_optima)
        
        # Guardar referencia a la función
        self.ajustar_tamano_panel = ajustar_tamano_panel
    
    def actualizar_panel_distribuciones(self):
        """Actualiza el panel de distribuciones con los nodos del grafo"""
        # Limpiar controles existentes
        for widget in self.frame_distribuciones.winfo_children():
            widget.destroy()
        
        self.controles_distribuciones = {}
        
        if not self.grafo_actual:
            # Mostrar mensaje si no hay grafo
            self.mensaje_distribuciones = ttk.Label(self.frame_distribuciones, 
                                                  text="📂 Carga un grafo para configurar distribuciones",
                                                  font=('Segoe UI', 10), foreground='#6c757d')
            self.mensaje_distribuciones.pack(pady=20)
            
            # Ajustar el tamaño del panel para el mensaje
            self.ajustar_tamano_panel()
            return
        
        # Obtener distribuciones actuales
        distribuciones = self.simulador.obtener_distribuciones_nodos()
        
        # Crear controles para cada nodo
        for i, nodo_id in enumerate(self.grafo_actual.nodes()):
            self._crear_controles_nodo(self.frame_distribuciones, nodo_id, i, distribuciones.get(nodo_id, {}))
        
        # Actualizar el scroll y ajustar el tamaño después de crear todos los controles
        self.frame_distribuciones.update_idletasks()
        self.canvas_distribuciones.configure(scrollregion=self.canvas_distribuciones.bbox("all"))
        
        # Ajustar el tamaño del panel al contenido
        self.ajustar_tamano_panel()
    
    def _crear_controles_nodo(self, parent, nodo_id: str, index: int, config_actual: Dict[str, any]):
        """Crea los controles para configurar la distribución de un nodo"""
        # Frame para el nodo
        nodo_frame = ttk.LabelFrame(parent, text=f"📍 Nodo: {nodo_id}", padding="8")
        nodo_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Variables para este nodo
        tipo_var = tk.StringVar(value=config_actual.get('tipo', 'exponencial'))
        unidades_var = tk.StringVar(value=config_actual.get('unidades', 'segundos'))
        lambda_var = tk.DoubleVar(value=config_actual.get('parametros', {}).get('lambda', 0.5))
        min_var = tk.DoubleVar(value=config_actual.get('parametros', {}).get('min', 1.0))
        max_var = tk.DoubleVar(value=config_actual.get('parametros', {}).get('max', 5.0))
        
        # Guardar referencias
        self.controles_distribuciones[nodo_id] = {
            'tipo': tipo_var,
            'unidades': unidades_var,
            'lambda': lambda_var,
            'min': min_var,
            'max': max_var
        }
        
        # Selector de tipo de distribución
        ttk.Label(nodo_frame, text="Tipo:", font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=2)
        tipo_combo = ttk.Combobox(nodo_frame, textvariable=tipo_var, 
                                 values=['exponencial', 'poisson', 'uniforme'],
                                 state='readonly', width=12)
        tipo_combo.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Selector de unidades de tiempo
        ttk.Label(nodo_frame, text="Unidades:", font=('Segoe UI', 9, 'bold')).grid(row=0, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        unidades_combo = ttk.Combobox(nodo_frame, textvariable=unidades_var,
                                     values=['segundos', 'minutos', 'horas'],
                                     state='readonly', width=10)
        unidades_combo.grid(row=0, column=3, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Función para obtener factor de conversión a segundos
        def obtener_factor_conversion(unidades):
            if unidades == 'segundos':
                return 1.0
            elif unidades == 'minutos':
                return 60.0
            elif unidades == 'horas':
                return 3600.0
            return 1.0
        
        # Función para actualizar parámetros según el tipo y unidades
        def actualizar_parametros(*args):
            tipo = tipo_var.get()
            unidades = unidades_var.get()
            factor = obtener_factor_conversion(unidades)
            
            # Actualizar etiquetas con unidades
            if tipo == 'exponencial':
                lambda_label.config(text=f"λ (1/{unidades}):")
                # Mostrar solo Lambda
                lambda_label.grid(row=1, column=0, sticky=tk.W, pady=2)
                lambda_spin.grid(row=1, column=1, sticky=tk.W, pady=2, padx=(5, 0))
                min_label.grid_remove()
                min_spin.grid_remove()
                max_label.grid_remove()
                max_spin.grid_remove()
                # Ajustar valores por defecto según unidades
                if unidades == 'segundos':
                    lambda_var.set(0.5)
                elif unidades == 'minutos':
                    lambda_var.set(0.008)  # ~0.5/60
                elif unidades == 'horas':
                    lambda_var.set(0.00014)  # ~0.5/3600
            elif tipo == 'poisson':
                lambda_label.config(text=f"λ (eventos/{unidades}):")
                # Mostrar solo Lambda (tasa de eventos)
                lambda_label.grid(row=1, column=0, sticky=tk.W, pady=2)
                lambda_spin.grid(row=1, column=1, sticky=tk.W, pady=2, padx=(5, 0))
                min_label.grid_remove()
                min_spin.grid_remove()
                max_label.grid_remove()
                max_spin.grid_remove()
                # Ajustar valores por defecto según unidades
                if unidades == 'segundos':
                    lambda_var.set(2.0)
                elif unidades == 'minutos':
                    lambda_var.set(0.033)  # ~2/60
                elif unidades == 'horas':
                    lambda_var.set(0.00056)  # ~2/3600
            elif tipo == 'uniforme':
                min_label.config(text=f"Min ({unidades}):")
                max_label.config(text=f"Max ({unidades}):")
                # Mostrar Min y Max
                lambda_label.grid_remove()
                lambda_spin.grid_remove()
                min_label.grid(row=1, column=0, sticky=tk.W, pady=2)
                min_spin.grid(row=1, column=1, sticky=tk.W, pady=2, padx=(5, 0))
                max_label.grid(row=2, column=0, sticky=tk.W, pady=2)
                max_spin.grid(row=2, column=1, sticky=tk.W, pady=2, padx=(5, 0))
                # Ajustar valores por defecto según unidades
                if unidades == 'segundos':
                    min_var.set(1.0)
                    max_var.set(5.0)
                elif unidades == 'minutos':
                    min_var.set(0.017)  # ~1/60
                    max_var.set(0.083)  # ~5/60
                elif unidades == 'horas':
                    min_var.set(0.00028)  # ~1/3600
                    max_var.set(0.00139)  # ~5/3600
        
        # Vincular cambio de tipo y unidades con actualización de parámetros
        tipo_var.trace('w', actualizar_parametros)
        unidades_var.trace('w', actualizar_parametros)
        
        # Función para obtener rangos según unidades
        def obtener_rangos_spinbox(unidades):
            if unidades == 'segundos':
                return {'from_': 0.1, 'to': 10.0, 'increment': 0.1}
            elif unidades == 'minutos':
                return {'from_': 0.001, 'to': 1.0, 'increment': 0.001}
            elif unidades == 'horas':
                return {'from_': 0.0001, 'to': 0.1, 'increment': 0.0001}
            return {'from_': 0.1, 'to': 10.0, 'increment': 0.1}
        
        # Crear controles de parámetros con rangos dinámicos
        lambda_label = ttk.Label(nodo_frame, text="λ (Lambda):", font=('Segoe UI', 9, 'bold'))
        lambda_spin = ttk.Spinbox(nodo_frame, textvariable=lambda_var, width=10)
        
        min_label = ttk.Label(nodo_frame, text="Min (s):", font=('Segoe UI', 9, 'bold'))
        min_spin = ttk.Spinbox(nodo_frame, textvariable=min_var, width=10)
        
        max_label = ttk.Label(nodo_frame, text="Max (s):", font=('Segoe UI', 9, 'bold'))
        max_spin = ttk.Spinbox(nodo_frame, textvariable=max_var, width=10)
        
        # Función para actualizar rangos de spinboxes
        def actualizar_rangos_spinbox():
            rangos = obtener_rangos_spinbox(unidades_var.get())
            lambda_spin.config(from_=rangos['from_'], to=rangos['to'], increment=rangos['increment'])
            min_spin.config(from_=rangos['from_'], to=rangos['to'], increment=rangos['increment'])
            max_spin.config(from_=rangos['from_'], to=rangos['to'], increment=rangos['increment'])
        
        # Vincular cambio de unidades con actualización de rangos
        unidades_var.trace('w', lambda *args: actualizar_rangos_spinbox())
        
        # Inicializar con parámetros por defecto
        actualizar_parametros()
        
        # Botón para aplicar cambios
        aplicar_btn = ttk.Button(nodo_frame, text="✅ Aplicar", 
                               command=lambda: self._aplicar_distribucion_nodo(nodo_id))
        aplicar_btn.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Descripción actual
        descripcion = config_actual.get('descripcion', 'Exponencial (λ=0.50)')
        desc_label = ttk.Label(nodo_frame, text=f"Actual: {descripcion}", 
                              font=('Segoe UI', 8), foreground='#6c757d')
        desc_label.grid(row=5, column=0, columnspan=2, pady=2)
        
        # Guardar referencia a la descripción para actualizarla
        self.controles_distribuciones[nodo_id]['descripcion'] = desc_label
    
    def _aplicar_distribucion_nodo(self, nodo_id: str):
        """Aplica la distribución configurada para un nodo específico"""
        try:
            controles = self.controles_distribuciones[nodo_id]
            tipo = controles['tipo'].get()
            unidades = controles['unidades'].get()
            
            # Función para convertir a segundos
            def convertir_a_segundos(valor, unidades):
                if unidades == 'segundos':
                    return valor
                elif unidades == 'minutos':
                    return valor * 60.0
                elif unidades == 'horas':
                    return valor * 3600.0
                return valor
            
            # Validar y preparar parámetros según el tipo
            if tipo in ['exponencial', 'poisson']:
                lambda_val = controles['lambda'].get()
                if lambda_val <= 0:
                    messagebox.showerror("Error", f"❌ El parámetro λ debe ser mayor que 0 para {tipo}")
                    return
                # Convertir lambda a segundos
                lambda_segundos = convertir_a_segundos(lambda_val, unidades)
                parametros = {'lambda': lambda_segundos}
            elif tipo == 'uniforme':
                min_val = controles['min'].get()
                max_val = controles['max'].get()
                if min_val >= max_val:
                    messagebox.showerror("Error", "❌ El valor mínimo debe ser menor que el máximo")
                    return
                if min_val < 0:
                    messagebox.showerror("Error", "❌ Los valores no pueden ser negativos")
                    return
                # Convertir a segundos
                min_segundos = convertir_a_segundos(min_val, unidades)
                max_segundos = convertir_a_segundos(max_val, unidades)
                parametros = {
                    'min': min_segundos,
                    'max': max_segundos
                }
            else:
                messagebox.showerror("Error", f"❌ Tipo de distribución no válido: {tipo}")
                return
            
            # Aplicar al simulador
            self.simulador.actualizar_distribucion_nodo(nodo_id, tipo, parametros)
            
            # Actualizar descripción con formato específico por tipo y unidades
            if tipo == 'exponencial':
                lambda_val = controles['lambda'].get()
                nueva_descripcion = f"Exponencial (λ={lambda_val:.3f}/{unidades})"
            elif tipo == 'poisson':
                lambda_val = controles['lambda'].get()
                nueva_descripcion = f"Poisson (λ={lambda_val:.3f} eventos/{unidades})"
            elif tipo == 'uniforme':
                min_val = controles['min'].get()
                max_val = controles['max'].get()
                nueva_descripcion = f"Uniforme ({min_val:.3f}-{max_val:.3f} {unidades})"
            else:
                nueva_descripcion = "Desconocida"
            
            controles['descripcion'].config(text=f"Actual: {nueva_descripcion}")
            
            # Mostrar mensaje de confirmación
            messagebox.showinfo("Distribución Aplicada", 
                              f"✅ Distribución {tipo} aplicada al nodo {nodo_id}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar distribución: {str(e)}")
    
    def actualizar_info_grafo(self):
        """Actualiza la información del grafo en el panel de control"""
        if self.grafo_actual:
            num_nodos = len(self.grafo_actual.nodes())
            num_arcos = len(self.grafo_actual.edges())
            self.info_grafo_label.config(
                text=f"Grafo: {num_nodos} nodos, {num_arcos} arcos",
                foreground='#28a745'
            )
        else:
            self.info_grafo_label.config(
                text="Sin grafo cargado",
                foreground='#6c757d'
            )
        
    def crear_panel_visualizacion(self, parent):
        """Crea el panel de visualización de la simulación"""
        viz_frame = ttk.LabelFrame(parent, text="📊 VISUALIZACIÓN EN TIEMPO REAL", padding="10")
        parent.add(viz_frame, weight=2)  # Panel visual más grande
        
        # Crear figura de matplotlib
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Configurar el gráfico inicial
        self.configurar_grafico_inicial()
        
    def crear_panel_estadisticas(self, parent):
        """Crea el panel de estadísticas"""
        stats_frame = ttk.LabelFrame(parent, text="📈 ESTADÍSTICAS DE SIMULACIÓN", padding="10")
        stats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Frame para estadísticas con grid para mejor distribución
        stats_inner = ttk.Frame(stats_frame)
        stats_inner.pack(fill=tk.BOTH, expand=True)
        
        # Configurar grid para distribución uniforme
        for i in range(10):  # 10 columnas para distribuir uniformemente
            stats_inner.columnconfigure(i, weight=1)
        
        # Estadísticas principales
        self.stats_labels = {}
        
        # Primera fila - Estadísticas básicas
        ttk.Label(stats_inner, text="Ciclistas Activos:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.stats_labels['total_ciclistas'] = ttk.Label(stats_inner, text="0", font=('Segoe UI', 10))
        self.stats_labels['total_ciclistas'].grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(stats_inner, text="Velocidad Promedio:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=5)
        self.stats_labels['velocidad_promedio'] = ttk.Label(stats_inner, text="0.0 m/s", font=('Segoe UI', 10))
        self.stats_labels['velocidad_promedio'].grid(row=0, column=3, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(stats_inner, text="Velocidad Mín:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=4, sticky=tk.W, padx=5)
        self.stats_labels['velocidad_min'] = ttk.Label(stats_inner, text="0.0 m/s", font=('Segoe UI', 10))
        self.stats_labels['velocidad_min'].grid(row=0, column=5, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(stats_inner, text="Velocidad Máx:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=6, sticky=tk.W, padx=5)
        self.stats_labels['velocidad_max'] = ttk.Label(stats_inner, text="0.0 m/s", font=('Segoe UI', 10))
        self.stats_labels['velocidad_max'].grid(row=0, column=7, sticky=tk.W, padx=(0, 20))
        
        # Segunda fila - Estadísticas del grafo
        ttk.Label(stats_inner, text="Nodos del Grafo:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.stats_labels['grafo_nodos'] = ttk.Label(stats_inner, text="0", font=('Segoe UI', 10))
        self.stats_labels['grafo_nodos'].grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=5)
        
        ttk.Label(stats_inner, text="Arcos del Grafo:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.stats_labels['grafo_arcos'] = ttk.Label(stats_inner, text="0", font=('Segoe UI', 10))
        self.stats_labels['grafo_arcos'].grid(row=1, column=3, sticky=tk.W, padx=(0, 20), pady=5)
        
        ttk.Label(stats_inner, text="Modo:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=4, sticky=tk.W, padx=5, pady=5)
        self.stats_labels['modo_simulacion'] = ttk.Label(stats_inner, text="Original", font=('Segoe UI', 10))
        self.stats_labels['modo_simulacion'].grid(row=1, column=5, sticky=tk.W, padx=(0, 20), pady=5)
        
        # Tercera fila - Estadísticas de distribuciones
        ttk.Label(stats_inner, text="Distribuciones:", font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, padx=5)
        self.stats_labels['distribuciones_configuradas'] = ttk.Label(stats_inner, text="0", font=('Segoe UI', 10))
        self.stats_labels['distribuciones_configuradas'].grid(row=2, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(stats_inner, text="Tasa Promedio:", font=('Segoe UI', 10, 'bold')).grid(row=2, column=2, sticky=tk.W, padx=5)
        self.stats_labels['tasa_arribo_promedio'] = ttk.Label(stats_inner, text="0.0", font=('Segoe UI', 10))
        self.stats_labels['tasa_arribo_promedio'].grid(row=2, column=3, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(stats_inner, text="Duración:", font=('Segoe UI', 10, 'bold')).grid(row=2, column=4, sticky=tk.W, padx=5)
        self.stats_labels['duracion_simulacion'] = ttk.Label(stats_inner, text="300s", font=('Segoe UI', 10))
        self.stats_labels['duracion_simulacion'].grid(row=2, column=5, sticky=tk.W, padx=(0, 20))
        
    def configurar_grafico_inicial(self):
        """Configura el gráfico inicial sin grafo cargado"""
        self.ax.clear()
        self.ax.set_title("🚴 SIMULADOR DE CICLORUTAS", 
                         fontsize=14, fontweight='bold', color='#212529', pad=15)
        self.ax.set_xlabel("Distancia (metros)", fontsize=12, fontweight='bold', color='#495057')
        self.ax.set_ylabel("Desviación (metros)", fontsize=12, fontweight='bold', color='#495057')
        self.ax.grid(True, alpha=0.3, color='#adb5bd', linestyle='-', linewidth=0.5)
        
        # Configurar ejes elegantes
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#6c757d')
        self.ax.spines['bottom'].set_color('#6c757d')
        
        # Scatter plot para ciclistas
        self.scatter = self.ax.scatter([], [], s=100, alpha=0.9, edgecolors='none', linewidth=0, zorder=5)
        
        # Mensaje inicial
        self.ax.text(0.5, 0.5, '📂 Carga un grafo Excel para comenzar la simulación\n\n' +
                    'El grafo debe tener:\n' +
                    '• Hoja "NODOS" con lista de nodos\n' +
                    '• Hoja "ARCOS" con origen, destino y peso', 
                    transform=self.ax.transAxes, fontsize=11, ha='center', va='center',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))
        
        self.canvas.draw()
        
    def configurar_grafico_con_grafo(self):
        """Configura el gráfico cuando hay un grafo cargado"""
        if not self.grafo_actual or not self.pos_grafo_actual:
            return
            
        self.ax.clear()
        
        # Dibujar el grafo NetworkX
        nx.draw(self.grafo_actual, self.pos_grafo_actual, ax=self.ax, 
                with_labels=True, node_color="#2E86AB", edge_color="#AAB7B8",
                node_size=800, font_size=10, font_color="white", font_weight='bold')
        
        # Agregar etiquetas de peso en los arcos
        etiquetas = nx.get_edge_attributes(self.grafo_actual, 'weight')
        nx.draw_networkx_edge_labels(self.grafo_actual, self.pos_grafo_actual, 
                                   edge_labels=etiquetas, ax=self.ax, font_size=8)
        
        # Configurar el gráfico
        self.ax.set_title("🚴 SIMULACIÓN SOBRE GRAFO REAL", 
                         fontsize=14, fontweight='bold', color='#212529', pad=15)
        self.ax.set_xlabel("Coordenada X", fontsize=12, fontweight='bold', color='#495057')
        self.ax.set_ylabel("Coordenada Y", fontsize=12, fontweight='bold', color='#495057')
        
        # Configurar ejes elegantes
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#6c757d')
        self.ax.spines['bottom'].set_color('#6c757d')
        
        # Scatter plot para ciclistas con zorder alto para estar por encima del grafo
        self.scatter = self.ax.scatter([], [], s=120, alpha=0.95, edgecolors='white', 
                                     linewidth=2, zorder=10)
        
        self.canvas.draw()
        
    # def configurar_grafico(self):
    #     """Configura el gráfico de matplotlib"""
    #     self.ax.clear()
        
    #     # Dibujar carreteras en forma de Y con mejor diseño
    #     # Tramo principal A->X
    #     solid_capstyle='round', label='Tramo Principal A→X', zorder=1)

    #     # Tramo X->B con sombra y mejor color
    #     solid_capstyle='round', label='Tramo X→B', zorder=1)

    #     # Tramo X->C con sombra y mejor color
    #     solid_capstyle='round', label='Tramo X→C', zorder=1)
        
    #     # Marcadores de puntos
    #     self.ax.plot(0, 0, 'ko', markersize=8, label='Punto A', zorder=3)
    #     color='#FF6B35', marker='o', markersize=8, label='Punto B', zorder=3)
    #     color='#FF1744', marker='o', markersize=8, label='Punto C', zorder=3)
        
    #     # Configuración del gráfico
    #     self.ax.set_title("CICLORRUTA EN FORMA DE Y - SIMULACION EN TIEMPO REAL", 
    #                      fontsize=14, fontweight='bold', color='#212529', pad=15)
    #     self.ax.set_xlabel("Distancia (metros)", fontsize=12, fontweight='bold', color='#495057')
    #     self.ax.set_ylabel("Desviación (metros)", fontsize=12, fontweight='bold', color='#495057')
        
    #     # Crear leyenda sin zorder para compatibilidad
    #     legend = self.ax.legend(fontsize=10, frameon=True, fancybox=True, shadow=True)
    #     legend.set_zorder(4)  # Establecer zorder después de crear la leyenda
        
    #     self.ax.grid(True, alpha=0.3, color='#adb5bd', linestyle='-', linewidth=0.5, zorder=1)
        
    #     # Ejes elegantes
    #     self.ax.spines['top'].set_visible(False)
    #     self.ax.spines['right'].set_visible(False)
    #     self.ax.spines['left'].set_color('#6c757d')
    #     self.ax.spines['bottom'].set_color('#6c757d')
        
    #     # Scatter plot para ciclistas - CON ZORDER ALTO para estar por encima
    #     self.scatter = self.ax.scatter([], [], s=100, alpha=0.9, edgecolors='none', linewidth=0, zorder=5)
        
    #     self.canvas.draw()
        
    def actualizar_visualizacion(self):
        """Actualiza la visualización con los datos actuales"""
        if not hasattr(self, 'scatter'):
            return
            
        try:
            estado = self.simulador.obtener_estado_actual()
            
            if not estado['coordenadas']:
                # No hay ciclistas para mostrar
                self.scatter.set_offsets([])
                self.canvas.draw()
                return
            
            # Extraer coordenadas
            x, y = zip(*estado['coordenadas'])
            
            # Actualizar posiciones de los ciclistas
            self.scatter.set_offsets(list(zip(x, y)))
            self.scatter.set_color(estado['colores'])
            
            # Configurar apariencia de los ciclistas
            num_ciclistas = len(estado['coordenadas'])
            self.scatter.set_sizes([120] * num_ciclistas)
            self.scatter.set_alpha(0.95)
            
            # Configurar bordes según si hay grafo o no
            if self.grafo_actual:
                # Con grafo: bordes blancos para contraste
                self.scatter.set_edgecolors('white')
                self.scatter.set_linewidth(2)
            else:
                # Sin grafo: sin bordes
                self.scatter.set_edgecolors('none')
                self.scatter.set_linewidth(0)
            
            # Actualizar canvas
            self.canvas.draw()
            
        except Exception as e:
            print(f"⚠️ Error actualizando visualización: {e}")
            # En caso de error, intentar redibujar el gráfico
            if self.grafo_actual:
                self.configurar_grafico_con_grafo()
            else:
                self.configurar_grafico_inicial()
            
    def nueva_simulacion(self):
        """Crea una nueva simulación con los parámetros actuales"""
        try:
            # Detener simulación actual si está corriendo
            if self.simulacion_activa:
                self.simulacion_activa = False
                time.sleep(0.1)  # Pequeña pausa para asegurar que el hilo termine
            
            # Actualizar configuración
            self.config.velocidad_min = self.vel_min_var.get()
            self.config.velocidad_max = self.vel_max_var.get()
            
            # Validar velocidades
            if self.config.velocidad_min >= self.config.velocidad_max:
                messagebox.showerror("Error", "La velocidad mínima debe ser menor que la máxima")
                return
            
            # Crear nuevo simulador
            self.simulador = SimuladorCiclorutas(self.config)
            
            # Si hay un grafo cargado, configurarlo en el nuevo simulador
            if self.grafo_actual and self.pos_grafo_actual:
                self.simulador.configurar_grafo(self.grafo_actual, self.pos_grafo_actual)
            
            self.simulador.inicializar_simulacion()
            
            # Actualizar interfaz
            if self.grafo_actual:
                self.configurar_grafico_con_grafo()
                self.actualizar_panel_distribuciones()
            else:
                self.configurar_grafico_inicial()
            self.actualizar_visualizacion()
            self.actualizar_estadisticas()
            self.actualizar_info_grafo()
            self.estado_label.config(text="LISTO", foreground='#28a745')
            self.tiempo_label.config(text="0.0s")
            
            # Resetear botón de pausa
            self.resetear_boton_pausa()
            
            messagebox.showinfo("Nueva Simulación", "Simulación creada exitosamente con los nuevos parámetros!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear la simulación: {str(e)}")
    
    def iniciar_simulacion(self):
        """Inicia la simulación"""
        if not self.simulacion_activa:
            self.simulador.estado = "ejecutando"
            self.simulacion_activa = True
            self.estado_label.config(text="EJECUTANDO", foreground='#007bff')
            
            # Iniciar hilo de simulación
            self.hilo_simulacion = threading.Thread(target=self.ejecutar_simulacion)
            self.hilo_simulacion.daemon = True
            self.hilo_simulacion.start()
    
    def ejecutar_simulacion(self):
        """Ejecuta la simulación en un hilo separado"""
        while self.simulacion_activa and self.simulador.estado == "ejecutando":
            if self.simulador.ejecutar_paso():
                # Actualizar interfaz en el hilo principal
                self.root.after(0, self.actualizar_interfaz)
                time.sleep(0.05)  # Control de velocidad
            else:
                # La simulación ha terminado
                self.root.after(0, self.simulacion_terminada)
                break
    
    def actualizar_interfaz(self):
        """Actualiza la interfaz con los datos actuales"""
        estado = self.simulador.obtener_estado_actual()
        self.tiempo_label.config(text=f"{estado['tiempo_actual']:.1f}s")
        self.actualizar_visualizacion()
        self.actualizar_estadisticas()
    
    def pausar_simulacion(self):
        """Pausa o reanuda la simulación"""
        if self.simulador.estado == "ejecutando":
            # Pausar
            self.simulador.pausar_simulacion()
            self.estado_label.config(text="PAUSADO", foreground='#ffc107')
            # Cambiar texto del botón
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.LabelFrame):
                            for button in child.winfo_children():
                                if isinstance(button, ttk.Button) and "PAUSAR" in button.cget("text"):
                                    button.configure(text="▶️ REANUDAR")
        else:
            # Reanudar
            self.simulador.estado = "ejecutando"
            self.estado_label.config(text="EJECUTANDO", foreground='#007bff')
            # Cambiar texto del botón de vuelta
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.LabelFrame):
                            for button in child.winfo_children():
                                if isinstance(button, ttk.Button) and "REANUDAR" in button.cget("text"):
                                    button.configure(text="⏸️ PAUSAR")
    
    def detener_simulacion(self):
        """Detiene la simulación"""
        self.simulacion_activa = False
        self.simulador.detener_simulacion()
        self.estado_label.config(text="DETENIDO", foreground='#dc3545')
        self.tiempo_label.config(text="0.0s")
        
    def simulacion_terminada(self):
        """Maneja cuando la simulación termina naturalmente"""
        self.simulacion_activa = False
        self.estado_label.config(text="COMPLETADA", foreground='#28a745')
        self.actualizar_estadisticas()
        
        # Mostrar mensaje de finalización
        messagebox.showinfo("Simulación Completada", 
                          "¡La simulación ha terminado! Puedes:\n\n"
                          "• Hacer clic en 'NUEVA SIMULACIÓN' para reiniciar\n"
                          "• Hacer clic en 'REPRODUCIR' para repetir la misma simulación\n"
                          "• Modificar parámetros y crear una nueva simulación")
        
    def reiniciar_simulacion(self):
        """Reinicia la simulación actual con los mismos parámetros"""
        try:
            # Reinicializar el simulador actual
            self.simulador.inicializar_simulacion()
            
            # Resetear estado
            self.simulacion_activa = False
            self.estado_label.config(text="LISTO", foreground='#28a745')
            self.tiempo_label.config(text="0.0s")
            
            # Actualizar visualización
            if self.grafo_actual:
                self.configurar_grafico_con_grafo()
                self.actualizar_panel_distribuciones()
            else:
                self.configurar_grafico_inicial()
            self.actualizar_visualizacion()
            self.actualizar_estadisticas()
            self.actualizar_info_grafo()
            
            # Resetear botón de pausa
            self.resetear_boton_pausa()
            
            messagebox.showinfo("Simulación Reiniciada", "La simulación ha sido reiniciada exitosamente!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al reiniciar la simulación: {str(e)}")
    
    def resetear_boton_pausa(self):
        """Resetea el botón de pausa al estado original"""
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.LabelFrame):
                        for button in child.winfo_children():
                            if isinstance(button, ttk.Button) and "REANUDAR" in button.cget("text"):
                                button.configure(text="⏸️ PAUSAR")
    
    def adelantar_simulacion(self):
        """Adelanta la simulación varios pasos"""
        if self.simulador.estado == "ejecutando":
            for _ in range(10):  # Adelantar 10 pasos
                if not self.simulador.ejecutar_paso():
                    break
            self.actualizar_interfaz()
    
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas mostradas"""
        stats = self.simulador.obtener_estadisticas()
        
        # Estadísticas básicas
        self.stats_labels['total_ciclistas'].config(text=str(stats['total_ciclistas']))
        self.stats_labels['velocidad_promedio'].config(text=f"{stats['velocidad_promedio']:.1f} m/s")
        self.stats_labels['velocidad_min'].config(text=f"{stats['velocidad_minima']:.1f} m/s")
        self.stats_labels['velocidad_max'].config(text=f"{stats['velocidad_maxima']:.1f} m/s")
        self.stats_labels['duracion_simulacion'].config(text=f"{stats.get('duracion_simulacion', 300):.0f}s")
        
        # Estadísticas del grafo
        if stats.get('usando_grafo_real', False):
            self.stats_labels['grafo_nodos'].config(text=str(stats.get('grafo_nodos', 0)))
            self.stats_labels['grafo_arcos'].config(text=str(stats.get('grafo_arcos', 0)))
            self.stats_labels['modo_simulacion'].config(text="Grafo Real", foreground='#28a745')
            
            # Estadísticas de distribuciones
            self.stats_labels['distribuciones_configuradas'].config(text=str(stats.get('distribuciones_configuradas', 0)))
            tasa_promedio = stats.get('tasa_arribo_promedio', 0)
            self.stats_labels['tasa_arribo_promedio'].config(text=f"{tasa_promedio:.2f}")
        else:
            self.stats_labels['grafo_nodos'].config(text="0")
            self.stats_labels['grafo_arcos'].config(text="0")
            self.stats_labels['modo_simulacion'].config(text="Sistema Original", foreground='#6c757d')
            self.stats_labels['distribuciones_configuradas'].config(text="0")
            self.stats_labels['tasa_arribo_promedio'].config(text="0.0")


    def cargar_grafo(self):
        """Carga un grafo desde archivo Excel y lo integra con la simulación"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de grafo",
            filetypes=[("Excel files", "*.xlsx"), ("Excel files", "*.xls")]
        )
        
        if not archivo:
            return
            
        try:
            # Leer datos del Excel
            nodos_df = pd.read_excel(archivo, sheet_name="NODOS", engine="openpyxl")
            arcos_df = pd.read_excel(archivo, sheet_name="ARCOS", engine="openpyxl")
            
            # Crear grafo NetworkX
            G = nx.Graph()
            
            # Agregar nodos
            for nodo in nodos_df.iloc[:, 0]:
                G.add_node(nodo)
                print(f"✅ Nodo agregado: {nodo}")
            
            # Agregar arcos con pesos
            for _, fila in arcos_df.iterrows():
                origen, destino, longitud = fila[0], fila[1], fila[2]
                G.add_edge(origen, destino, weight=longitud)
                print(f"✅ Arco agregado: {origen} -> {destino} (distancia: {longitud})")
            
            # Verificar que el grafo tenga al menos 3 nodos
            if len(G.nodes()) < 3:
                messagebox.showerror("Error", "El grafo debe tener al menos 3 nodos para la simulación")
                return
            
            # Calcular posiciones del grafo
            pos = nx.spring_layout(G, seed=42, k=2, iterations=50)
            
            # Guardar grafo y posiciones
            self.grafo_actual = G
            self.pos_grafo_actual = pos
            
            # Configurar el simulador con el nuevo grafo
            self.simulador.configurar_grafo(G, pos)
            
            # Actualizar visualización
            self.configurar_grafico_con_grafo()
            
            # Reinicializar simulación con el nuevo grafo
            self.simulador.inicializar_simulacion()
            self.actualizar_visualizacion()
            self.actualizar_estadisticas()
            
            # Actualizar panel de distribuciones
            self.actualizar_panel_distribuciones()
            
            # Actualizar información del grafo en el panel de control
            self.actualizar_info_grafo()
            
            # Mostrar mensaje de éxito
            num_nodos = len(G.nodes())
            num_arcos = len(G.edges())
            messagebox.showinfo("Grafo Cargado", 
                              f"✅ Grafo cargado exitosamente!\n\n"
                              f"📊 Estadísticas:\n"
                              f"• Nodos: {num_nodos}\n"
                              f"• Arcos: {num_arcos}\n\n"
                              f"🚴 La simulación ahora usará las coordenadas reales del grafo")
            
        except FileNotFoundError:
            messagebox.showerror("Error", "No se encontró el archivo especificado")
        except KeyError as e:
            messagebox.showerror("Error", f"Error en la estructura del archivo Excel: {str(e)}\n\n"
                                        "Asegúrate de que el archivo tenga las hojas 'NODOS' y 'ARCOS'")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {str(e)}")
def main():
    """Función principal para ejecutar la interfaz"""
    root = tk.Tk()
    app = InterfazSimulacion(root)
    root.mainloop()

if __name__ == "__main__":
    main()

