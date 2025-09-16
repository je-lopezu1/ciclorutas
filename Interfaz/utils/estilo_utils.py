"""
Utilidades de estilo para la interfaz gráfica.

Este módulo contiene funciones y configuraciones para el estilo visual
de la interfaz del simulador.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any


class EstiloUtils:
    """Utilidades para configuración de estilos de la interfaz"""
    
    # Paleta de colores del sistema
    COLORES = {
        'primario': '#2E86AB',
        'secundario': '#A23B72', 
        'exito': '#28a745',
        'advertencia': '#ffc107',
        'peligro': '#dc3545',
        'info': '#17a2b8',
        'gris_claro': '#f8f9fa',
        'gris_medio': '#6c757d',
        'gris_oscuro': '#343a40',
        'blanco': '#ffffff',
        'negro': '#000000'
    }
    
    # Configuraciones de fuente
    FUENTES = {
        'titulo': ('Segoe UI', 14, 'bold'),
        'subtitulo': ('Segoe UI', 12, 'bold'),
        'normal': ('Segoe UI', 10),
        'pequeno': ('Segoe UI', 9),
        'muy_pequeno': ('Segoe UI', 8)
    }
    
    # Configuraciones de padding
    PADDING = {
        'pequeno': 5,
        'medio': 10,
        'grande': 15,
        'muy_grande': 20
    }
    
    @staticmethod
    def configurar_estilo_ttk():
        """Configura el estilo de los widgets ttk"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar estilos personalizados
        EstiloUtils._configurar_estilos_frame(style)
        EstiloUtils._configurar_estilos_label(style)
        EstiloUtils._configurar_estilos_button(style)
        EstiloUtils._configurar_estilos_combobox(style)
        EstiloUtils._configurar_estilos_progressbar(style)
        
        return style
    
    @staticmethod
    def _configurar_estilos_frame(style):
        """Configura estilos para frames"""
        style.configure('TFrame', background=EstiloUtils.COLORES['gris_claro'])
        style.configure('Header.TFrame', background=EstiloUtils.COLORES['primario'])
        style.configure('Control.TFrame', background=EstiloUtils.COLORES['blanco'])
    
    @staticmethod
    def _configurar_estilos_label(style):
        """Configura estilos para labels"""
        style.configure('TLabel', 
                       background=EstiloUtils.COLORES['gris_claro'], 
                       font=EstiloUtils.FUENTES['normal'])
        style.configure('Header.TLabel', 
                       font=EstiloUtils.FUENTES['titulo'], 
                       foreground=EstiloUtils.COLORES['primario'])
        style.configure('Subheader.TLabel', 
                       font=EstiloUtils.FUENTES['subtitulo'], 
                       foreground=EstiloUtils.COLORES['gris_oscuro'])
        style.configure('Info.TLabel', 
                       font=EstiloUtils.FUENTES['pequeno'], 
                       foreground=EstiloUtils.COLORES['gris_medio'])
        style.configure('Success.TLabel', 
                       font=EstiloUtils.FUENTES['normal'], 
                       foreground=EstiloUtils.COLORES['exito'])
        style.configure('Warning.TLabel', 
                       font=EstiloUtils.FUENTES['normal'], 
                       foreground=EstiloUtils.COLORES['advertencia'])
        style.configure('Danger.TLabel', 
                       font=EstiloUtils.FUENTES['normal'], 
                       foreground=EstiloUtils.COLORES['peligro'])
    
    @staticmethod
    def _configurar_estilos_button(style):
        """Configura estilos para botones"""
        style.configure('TButton', font=EstiloUtils.FUENTES['normal'])
        style.configure('Accent.TButton', 
                       font=EstiloUtils.FUENTES['normal'], 
                       foreground=EstiloUtils.COLORES['blanco'],
                       background=EstiloUtils.COLORES['primario'])
        style.configure('Success.TButton', 
                       font=EstiloUtils.FUENTES['normal'], 
                       foreground=EstiloUtils.COLORES['blanco'],
                       background=EstiloUtils.COLORES['exito'])
        style.configure('Warning.TButton', 
                       font=EstiloUtils.FUENTES['normal'], 
                       foreground=EstiloUtils.COLORES['blanco'],
                       background=EstiloUtils.COLORES['advertencia'])
        style.configure('Danger.TButton', 
                       font=EstiloUtils.FUENTES['normal'], 
                       foreground=EstiloUtils.COLORES['blanco'],
                       background=EstiloUtils.COLORES['peligro'])
    
    @staticmethod
    def _configurar_estilos_combobox(style):
        """Configura estilos para comboboxes"""
        style.configure('TCombobox', font=EstiloUtils.FUENTES['normal'])
    
    @staticmethod
    def _configurar_estilos_progressbar(style):
        """Configura estilos para barras de progreso"""
        style.configure('TProgressbar', 
                       background=EstiloUtils.COLORES['primario'],
                       troughcolor=EstiloUtils.COLORES['gris_claro'])
    
    @staticmethod
    def crear_label_con_estilo(parent, texto: str, estilo: str = 'TLabel', **kwargs) -> ttk.Label:
        """Crea un label con estilo predefinido"""
        return ttk.Label(parent, text=texto, style=estilo, **kwargs)
    
    @staticmethod
    def crear_button_con_estilo(parent, texto: str, estilo: str = 'TButton', **kwargs) -> ttk.Button:
        """Crea un botón con estilo predefinido"""
        return ttk.Button(parent, text=texto, style=estilo, **kwargs)
    
    @staticmethod
    def crear_frame_con_estilo(parent, estilo: str = 'TFrame', **kwargs) -> ttk.Frame:
        """Crea un frame con estilo predefinido"""
        return ttk.Frame(parent, style=estilo, **kwargs)
    
    @staticmethod
    def crear_label_frame_con_estilo(parent, texto: str, **kwargs) -> ttk.LabelFrame:
        """Crea un LabelFrame con estilo predefinido"""
        return ttk.LabelFrame(parent, text=texto, **kwargs)
    
    @staticmethod
    def aplicar_padding(widget, padding: str = 'medio'):
        """Aplica padding a un widget"""
        pad_value = EstiloUtils.PADDING.get(padding, 10)
        return {'padx': pad_value, 'pady': pad_value}
    
    @staticmethod
    def obtener_color_estado(estado: str) -> str:
        """Obtiene el color correspondiente a un estado"""
        colores_estado = {
            'detenido': EstiloUtils.COLORES['gris_medio'],
            'ejecutando': EstiloUtils.COLORES['info'],
            'pausado': EstiloUtils.COLORES['advertencia'],
            'completado': EstiloUtils.COLORES['exito'],
            'error': EstiloUtils.COLORES['peligro']
        }
        return colores_estado.get(estado, EstiloUtils.COLORES['gris_medio'])
    
    @staticmethod
    def obtener_icono_estado(estado: str) -> str:
        """Obtiene el icono correspondiente a un estado"""
        iconos_estado = {
            'detenido': '⏹️',
            'ejecutando': '▶️',
            'pausado': '⏸️',
            'completado': '✅',
            'error': '❌'
        }
        return iconos_estado.get(estado, '❓')
    
    @staticmethod
    def crear_tooltip(widget, texto: str):
        """Crea un tooltip para un widget"""
        def mostrar_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=texto, 
                           background=EstiloUtils.COLORES['gris_oscuro'],
                           foreground=EstiloUtils.COLORES['blanco'],
                           font=EstiloUtils.FUENTES['pequeno'],
                           padx=5, pady=3)
            label.pack()
            
            def ocultar_tooltip(event):
                tooltip.destroy()
            
            widget.bind("<Leave>", ocultar_tooltip)
        
        widget.bind("<Enter>", mostrar_tooltip)
    
    @staticmethod
    def centrar_ventana(ventana, ancho: int = 400, alto: int = 300):
        """Centra una ventana en la pantalla"""
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (ventana.winfo_screenheight() // 2) - (alto // 2)
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
    
    @staticmethod
    def configurar_grid_responsivo(parent, num_columnas: int = 10):
        """Configura un grid responsivo para distribución uniforme"""
        for i in range(num_columnas):
            parent.columnconfigure(i, weight=1)
    
    @staticmethod
    def crear_separador(parent, orientacion: str = 'horizontal'):
        """Crea un separador con estilo"""
        return ttk.Separator(parent, orient=orientacion)
    
    @staticmethod
    def aplicar_estilo_estadistica(label, valor: Any, tipo: str = 'normal'):
        """Aplica estilo específico a una estadística"""
        if tipo == 'exito':
            label.config(foreground=EstiloUtils.COLORES['exito'])
        elif tipo == 'advertencia':
            label.config(foreground=EstiloUtils.COLORES['advertencia'])
        elif tipo == 'peligro':
            label.config(foreground=EstiloUtils.COLORES['peligro'])
        elif tipo == 'info':
            label.config(foreground=EstiloUtils.COLORES['info'])
        else:
            label.config(foreground=EstiloUtils.COLORES['gris_oscuro'])
        
        # Formatear valor según el tipo
        if isinstance(valor, float):
            if valor >= 1000:
                label.config(text=f"{valor:.0f}")
            elif valor >= 1:
                label.config(text=f"{valor:.1f}")
            else:
                label.config(text=f"{valor:.3f}")
        else:
            label.config(text=str(valor))
