"""
Ventana para mostrar el gráfico de ocupación de arcos.

Este módulo contiene una ventana separada que muestra el gráfico
del Top 5 de rutas más concurridas al finalizar la simulación.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

from ..utils.estilo_utils import EstiloUtils


class VentanaGraficoOcupacion:
    """Ventana separada para mostrar el gráfico de ocupación de arcos"""
    
    def __init__(self, parent, simulador):
        """
        Inicializa la ventana del gráfico
        
        Args:
            parent: Ventana padre (tk.Tk o tk.Toplevel)
            simulador: Referencia al simulador para obtener datos
        """
        self.parent = parent
        self.simulador = simulador
        
        # Crear ventana Toplevel
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("📊 Gráfico de Ocupación - Top 5 Rutas Más Concurridas")
        self.ventana.geometry("1000x700")
        self.ventana.minsize(800, 600)
        self.ventana.configure(bg=EstiloUtils.COLORES.get('gris_claro', '#f8f9fa'))
        
        # Variables para el gráfico
        self.fig_grafico = None
        self.ax_grafico = None
        self.canvas_grafico = None
        
        # Configurar cierre de ventana
        self.ventana.protocol("WM_DELETE_WINDOW", self._cerrar_ventana)
        
        # Crear la interfaz
        self._crear_interfaz()
        
        # Generar el gráfico automáticamente
        self._generar_grafico()
    
    def _crear_interfaz(self):
        """Crea la interfaz de la ventana"""
        # Frame principal
        main_frame = EstiloUtils.crear_frame_con_estilo(self.ventana)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame para el título y botones
        frame_header = EstiloUtils.crear_frame_con_estilo(main_frame)
        frame_header.pack(fill=tk.X, pady=(0, 10))
        
        # Título
        titulo = ttk.Label(
            frame_header,
            text="📊 Ocupación de Arcos a lo Largo del Tiempo - Top 5 Rutas Más Concurridas",
            font=EstiloUtils.FUENTES.get('subtitulo', ('Arial', 12, 'bold'))
        )
        titulo.pack(side=tk.LEFT, anchor=tk.W)
        
        # Frame para botones
        frame_botones = EstiloUtils.crear_frame_con_estilo(frame_header)
        frame_botones.pack(side=tk.RIGHT, padx=5)
        
        # Botón para exportar
        btn_exportar = ttk.Button(
            frame_botones,
            text="📥 Exportar Gráfico",
            command=self._exportar_grafico
        )
        btn_exportar.pack(side=tk.LEFT, padx=5)
        
        # Botón para cerrar
        btn_cerrar = ttk.Button(
            frame_botones,
            text="✖ Cerrar",
            command=self._cerrar_ventana
        )
        btn_cerrar.pack(side=tk.LEFT, padx=5)
        
        # Frame para el gráfico
        self.frame_grafico = EstiloUtils.crear_frame_con_estilo(main_frame)
        self.frame_grafico.pack(fill=tk.BOTH, expand=True)
    
    def _generar_grafico(self):
        """Genera el gráfico de líneas con la ocupación del Top 5 de arcos"""
        if not self.simulador:
            messagebox.showwarning("Advertencia", "No hay datos de simulación disponibles.")
            self.ventana.destroy()
            return
        
        try:
            # Obtener Top 5 arcos más concurridos
            top_5_arcos = self.simulador.obtener_top_5_arcos_concurridos()
            
            if not top_5_arcos:
                messagebox.showinfo("Información", "No hay suficientes datos de arcos para generar el gráfico.")
                self.ventana.destroy()
                return
            
            # Crear figura de matplotlib
            self.fig_grafico, self.ax_grafico = plt.subplots(figsize=(12, 7))
            self.fig_grafico.patch.set_facecolor('#f8f9fa')
            self.ax_grafico.set_facecolor('#ffffff')
            
            # Colores para las líneas
            colores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
            
            # Dibujar líneas para cada arco
            for idx, arco_data in enumerate(top_5_arcos):
                arco_str = arco_data['arco']
                ocupacion_tiempo = arco_data['ocupacion_tiempo']
                
                if not ocupacion_tiempo:
                    continue
                
                # Extraer tiempos y ocupaciones
                tiempos = [t for t, _ in ocupacion_tiempo]
                ocupaciones = [oc for _, oc in ocupacion_tiempo]
                
                # Truncar nombre del arco si es muy largo
                nombre_arco = arco_str
                if len(nombre_arco) > 30:
                    nombre_arco = nombre_arco[:27] + "..."
                
                # Dibujar línea
                color = colores[idx % len(colores)]
                self.ax_grafico.plot(
                    tiempos, 
                    ocupaciones, 
                    label=f"{nombre_arco} (Uso: {arco_data['total_uso']})",
                    color=color, 
                    linewidth=2.5, 
                    alpha=0.8,
                    marker='o',
                    markersize=3
                )
            
            # Configurar el gráfico
            self.ax_grafico.set_xlabel('Tiempo (segundos)', fontsize=12, fontweight='bold')
            self.ax_grafico.set_ylabel('Número de Ciclistas', fontsize=12, fontweight='bold')
            self.ax_grafico.set_title(
                'Ocupación de Arcos a lo Largo del Tiempo - Top 5 Rutas Más Concurridas', 
                fontsize=14, 
                fontweight='bold', 
                pad=20
            )
            self.ax_grafico.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
            self.ax_grafico.legend(loc='best', fontsize=10, framealpha=0.95, shadow=True)
            
            # Mejorar el estilo
            self.ax_grafico.spines['top'].set_visible(False)
            self.ax_grafico.spines['right'].set_visible(False)
            self.ax_grafico.spines['left'].set_color('#cccccc')
            self.ax_grafico.spines['bottom'].set_color('#cccccc')
            
            # Ajustar layout
            self.fig_grafico.tight_layout()
            
            # Crear canvas para tkinter
            self.canvas_grafico = FigureCanvasTkAgg(self.fig_grafico, self.frame_grafico)
            self.canvas_grafico.draw()
            self.canvas_grafico.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar el gráfico: {str(e)}")
            print(f"❌ Error generando gráfico: {e}")
            self.ventana.destroy()
    
    def _exportar_grafico(self):
        """Exporta el gráfico a un archivo"""
        if not self.fig_grafico:
            messagebox.showwarning("Advertencia", "No hay gráfico para exportar.")
            return
        
        try:
            # Solicitar ubicación para guardar
            archivo = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[
                    ("PNG", "*.png"),
                    ("PDF", "*.pdf"),
                    ("SVG", "*.svg"),
                    ("JPEG", "*.jpg")
                ],
                title="Exportar Gráfico de Ocupación"
            )
            
            if archivo:
                self.fig_grafico.savefig(archivo, dpi=300, bbox_inches='tight', facecolor='white')
                messagebox.showinfo("Éxito", f"Gráfico exportado exitosamente a:\n{os.path.basename(archivo)}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar el gráfico: {str(e)}")
            print(f"❌ Error exportando gráfico: {e}")
    
    def _cerrar_ventana(self):
        """Cierra la ventana y limpia recursos"""
        if self.fig_grafico:
            plt.close(self.fig_grafico)
        self.ventana.destroy()

