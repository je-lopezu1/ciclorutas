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
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Panel de control izquierdo
        self.crear_panel_control(main_frame)
        
        # Panel de visualización derecha
        self.crear_panel_visualizacion(main_frame)
        
        # Panel de estadísticas inferior
        self.crear_panel_estadisticas(main_frame)
        
    def crear_panel_control(self, parent):
        """Crea el panel de control de parámetros"""
        control_frame = ttk.LabelFrame(parent, text="⚙️ CONFIGURACIÓN DE SIMULACIÓN", padding="10")
        control_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Número de ciclistas
        ttk.Label(control_frame, text="Número de Ciclistas:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.num_ciclistas_var = tk.IntVar(value=self.config.num_ciclistas)
        num_ciclistas_spin = ttk.Spinbox(control_frame, from_=5, to=100, textvariable=self.num_ciclistas_var, width=10)
        num_ciclistas_spin.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
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
        
        # # Distancia A
        # ttk.Label(control_frame, text="Distancia A (m):", font=('Segoe UI', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        # dist_a_spin = ttk.Spinbox(control_frame, from_=20.0, to=100.0, increment=5.0, textvariable=self.dist_a_var, width=10)
        # dist_a_spin.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # # Distancia B
        # ttk.Label(control_frame, text="Distancia B (m):", font=('Segoe UI', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=5)
        # dist_b_spin = ttk.Spinbox(control_frame, from_=15.0, to=80.0, increment=5.0, textvariable=self.dist_b_var, width=10)
        # dist_b_spin.grid(row=4, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # # Distancia C
        # ttk.Label(control_frame, text="Distancia C (m):", font=('Segoe UI', 10, 'bold')).grid(row=5, column=0, sticky=tk.W, pady=5)
        # dist_c_spin = ttk.Spinbox(control_frame, from_=15.0, to=80.0, increment=5.0, textvariable=self.dist_c_var, width=10)
        # dist_c_spin.grid(row=5, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Separador
        ttk.Separator(control_frame, orient='horizontal').grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=15)
        
        ttk.Button(control_frame, text='📂 CARGAR GRAFO', command=self.cargar_grafo).grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        # Botones de control
        ttk.Button(control_frame, text="🔄 NUEVA SIMULACIÓN", command=self.nueva_simulacion, 
                  style='Accent.TButton').grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(control_frame, text="▶️ INICIAR", command=self.iniciar_simulacion, 
                  style='Accent.TButton').grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(control_frame, text="⏸️ PAUSAR", command=self.pausar_simulacion, 
                  style='Accent.TButton').grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(control_frame, text="⏹️ DETENER", command=self.detener_simulacion, 
                  style='Accent.TButton').grid(row=10, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(control_frame, text="⏭️ ADELANTAR", command=self.adelantar_simulacion, 
                  style='Accent.TButton').grid(row=11, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Botón para reiniciar simulación
        ttk.Button(control_frame, text="🔄 REPRODUCIR", command=self.reiniciar_simulacion, 
                  style='Accent.TButton').grid(row=12, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Estado de la simulación
        ttk.Label(control_frame, text="Estado:", font=('Segoe UI', 10, 'bold')).grid(row=13, column=0, sticky=tk.W, pady=(15, 5))
        self.estado_label = ttk.Label(control_frame, text="DETENIDO", font=('Segoe UI', 10), foreground='#dc3545')
        self.estado_label.grid(row=13, column=1, sticky=tk.W, pady=(15, 5), padx=(10, 0))
        
        # Tiempo actual
        ttk.Label(control_frame, text="Tiempo:", font=('Segoe UI', 10, 'bold')).grid(row=14, column=0, sticky=tk.W, pady=5)
        self.tiempo_label = ttk.Label(control_frame, text="0.0s", font=('Segoe UI', 10))
        self.tiempo_label.grid(row=14, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
    def crear_panel_visualizacion(self, parent):
        """Crea el panel de visualización de la simulación"""
        viz_frame = ttk.LabelFrame(parent, text="📊 VISUALIZACIÓN EN TIEMPO REAL", padding="10")
        viz_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Crear figura de matplotlib
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Configurar el gráfico inicial
        self.configurar_grafico_inicial()
        
    def crear_panel_estadisticas(self, parent):
        """Crea el panel de estadísticas"""
        stats_frame = ttk.LabelFrame(parent, text="📈 ESTADÍSTICAS DE SIMULACIÓN", padding="10")
        stats_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Frame para estadísticas
        stats_inner = ttk.Frame(stats_frame)
        stats_inner.pack(fill=tk.BOTH, expand=True)
        
        # Estadísticas principales
        self.stats_labels = {}
        
        # Primera fila
        row1 = ttk.Frame(stats_inner)
        row1.pack(fill=tk.X, pady=5)
        
        ttk.Label(row1, text="Total Ciclistas:", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
        self.stats_labels['total_ciclistas'] = ttk.Label(row1, text="0", font=('Segoe UI', 10))
        self.stats_labels['total_ciclistas'].pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(row1, text="Velocidad Promedio:", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
        self.stats_labels['velocidad_promedio'] = ttk.Label(row1, text="0.0 m/s", font=('Segoe UI', 10))
        self.stats_labels['velocidad_promedio'].pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(row1, text="Velocidad Mín:", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
        self.stats_labels['velocidad_min'] = ttk.Label(row1, text="0.0 m/s", font=('Segoe UI', 10))
        self.stats_labels['velocidad_min'].pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(row1, text="Velocidad Máx:", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
        self.stats_labels['velocidad_max'] = ttk.Label(row1, text="0.0 m/s", font=('Segoe UI', 10))
        self.stats_labels['velocidad_max'].pack(side=tk.LEFT)
        
        # Segunda fila - Estadísticas del grafo
        row2 = ttk.Frame(stats_inner)
        row2.pack(fill=tk.X, pady=5)
        
        ttk.Label(row2, text="Nodos del Grafo:", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
        self.stats_labels['grafo_nodos'] = ttk.Label(row2, text="0", font=('Segoe UI', 10))
        self.stats_labels['grafo_nodos'].pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(row2, text="Arcos del Grafo:", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
        self.stats_labels['grafo_arcos'] = ttk.Label(row2, text="0", font=('Segoe UI', 10))
        self.stats_labels['grafo_arcos'].pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(row2, text="Modo:", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
        self.stats_labels['modo_simulacion'] = ttk.Label(row2, text="Original", font=('Segoe UI', 10))
        self.stats_labels['modo_simulacion'].pack(side=tk.LEFT)
        
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
        self.ax.text(0.5, 0.5, '📂 Carga un grafo para comenzar la simulación', 
                    transform=self.ax.transAxes, fontsize=12, ha='center', va='center',
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
            self.config.num_ciclistas = self.num_ciclistas_var.get()
            self.config.velocidad_min = self.vel_min_var.get()
            self.config.velocidad_max = self.vel_max_var.get()
            
            # Crear nuevo simulador
            self.simulador = SimuladorCiclorutas(self.config)
            
            # Si hay un grafo cargado, configurarlo en el nuevo simulador
            if self.grafo_actual and self.pos_grafo_actual:
                self.simulador.configurar_grafo(self.grafo_actual, self.pos_grafo_actual)
            
            self.simulador.inicializar_simulacion()
            
            # Actualizar interfaz
            if self.grafo_actual:
                self.configurar_grafico_con_grafo()
            else:
                self.configurar_grafico_inicial()
            self.actualizar_visualizacion()
            self.actualizar_estadisticas()
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
            else:
                self.configurar_grafico_inicial()
            self.actualizar_visualizacion()
            self.actualizar_estadisticas()
            
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
        
        # Estadísticas del grafo
        if stats.get('usando_grafo_real', False):
            self.stats_labels['grafo_nodos'].config(text=str(stats.get('grafo_nodos', 0)))
            self.stats_labels['grafo_arcos'].config(text=str(stats.get('grafo_arcos', 0)))
            self.stats_labels['modo_simulacion'].config(text="Grafo Real", foreground='#28a745')
        else:
            self.stats_labels['grafo_nodos'].config(text="0")
            self.stats_labels['grafo_arcos'].config(text="0")
            self.stats_labels['modo_simulacion'].config(text="Sistema Original", foreground='#6c757d')


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
