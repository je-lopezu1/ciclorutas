"""
Panel de configuración de distribuciones.

Este módulo contiene el panel para configurar distribuciones de probabilidad
para cada nodo de la red de ciclorutas.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Any, Callable, Optional
import pandas as pd

from ..utils.estilo_utils import EstiloUtils


class PanelDistribuciones:
    """Panel de configuración de distribuciones por nodo"""
    
    def __init__(self, parent, callbacks: Dict[str, Callable]):
        self.parent = parent
        self.callbacks = callbacks
        
        # Variables de control
        self.grafo_actual = None
        self.perfiles_df = None
        self.controles_distribuciones = {}
        self.controles_perfiles = {}
        
        # Crear el panel
        self.crear_panel()
    
    def crear_panel(self):
        """Crea el panel de distribuciones principal"""
        # Frame principal
        self.frame_principal = EstiloUtils.crear_label_frame_con_estilo(
            self.parent, 
            "📊 CONFIGURACIÓN DE SIMULACIÓN"
        )
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Crear widget de pestañas
        self._crear_pestanas()
    
    def _crear_pestanas(self):
        """Crea las pestañas del panel"""
        # Crear widget de pestañas (Notebook)
        self.notebook_distribuciones = ttk.Notebook(self.frame_principal)
        self.notebook_distribuciones.pack(fill="both", expand=True)
        
        # PESTAÑA 1: NODOS
        self._crear_tab_nodos()
        
        # PESTAÑA 2: PERFILES DE CICLISTAS
        self._crear_tab_perfiles()
    
    def _crear_tab_nodos(self):
        """Crea la pestaña de configuración de nodos"""
        # Frame para la pestaña de nodos
        tab_nodos = ttk.Frame(self.notebook_distribuciones)
        self.notebook_distribuciones.add(tab_nodos, text="📍 NODOS")
        
        # Frame para scroll
        canvas = tk.Canvas(tab_nodos, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_nodos, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configurar scroll
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Mensaje inicial
        self.mensaje_distribuciones = EstiloUtils.crear_label_con_estilo(
            scrollable_frame, 
            "📂 Carga un grafo para configurar distribuciones de nodos",
            'Info.TLabel'
        )
        self.mensaje_distribuciones.pack(pady=20)
        
        # Guardar referencias
        self.canvas_distribuciones = canvas
        self.frame_distribuciones = scrollable_frame
    
    def _crear_tab_perfiles(self):
        """Crea la pestaña de configuración de perfiles de ciclistas"""
        # Frame para la pestaña de perfiles
        tab_perfiles = ttk.Frame(self.notebook_distribuciones)
        self.notebook_distribuciones.add(tab_perfiles, text="🚴 PERFILES")
        
        # Frame para scroll
        canvas_perfiles = tk.Canvas(tab_perfiles, highlightthickness=0)
        scrollbar_perfiles = ttk.Scrollbar(tab_perfiles, orient="vertical", command=canvas_perfiles.yview)
        scrollable_frame_perfiles = ttk.Frame(canvas_perfiles)
        
        # Configurar scroll
        scrollable_frame_perfiles.bind("<Configure>", lambda e: canvas_perfiles.configure(scrollregion=canvas_perfiles.bbox("all")))
        canvas_perfiles.create_window((0, 0), window=scrollable_frame_perfiles, anchor="nw")
        canvas_perfiles.configure(yscrollcommand=scrollbar_perfiles.set)
        
        # Empaquetar canvas y scrollbar
        canvas_perfiles.pack(side="left", fill="both", expand=True)
        scrollbar_perfiles.pack(side="right", fill="y")
        
        # Configurar scroll con mouse wheel
        def _on_mousewheel_perfiles(event):
            canvas_perfiles.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas_perfiles.bind_all("<MouseWheel>", _on_mousewheel_perfiles)
        
        # Mensaje inicial
        self.mensaje_perfiles = EstiloUtils.crear_label_con_estilo(
            scrollable_frame_perfiles, 
            "📂 Carga un grafo con hoja 'PERFILES' para configurar ciclistas",
            'Info.TLabel'
        )
        self.mensaje_perfiles.pack(pady=20)
        
        # Guardar referencias
        self.canvas_perfiles = canvas_perfiles
        self.frame_perfiles = scrollable_frame_perfiles
    
    def actualizar_panel_distribuciones(self, grafo_actual, distribuciones_actuales: Dict[str, Dict]):
        """Actualiza el panel de distribuciones con los nodos del grafo"""
        self.grafo_actual = grafo_actual
        
        # Limpiar controles existentes
        for widget in self.frame_distribuciones.winfo_children():
            widget.destroy()
        
        self.controles_distribuciones = {}
        
        if not grafo_actual:
            # Mostrar mensaje si no hay grafo
            self.mensaje_distribuciones = EstiloUtils.crear_label_con_estilo(
                self.frame_distribuciones, 
                "📂 Carga un grafo para configurar distribuciones",
                'Info.TLabel'
            )
            self.mensaje_distribuciones.pack(pady=20)
            return
        
        # Crear controles para cada nodo
        for i, nodo_id in enumerate(grafo_actual.nodes()):
            self._crear_controles_nodo(self.frame_distribuciones, nodo_id, i, 
                                     distribuciones_actuales.get(nodo_id, {}))
        
        # Actualizar el scroll
        self.frame_distribuciones.update_idletasks()
        self.canvas_distribuciones.configure(scrollregion=self.canvas_distribuciones.bbox("all"))
    
    def actualizar_panel_perfiles(self, perfiles_df: Optional[pd.DataFrame], atributos_disponibles: List[str] = None):
        """Actualiza el panel de perfiles de ciclistas"""
        self.perfiles_df = perfiles_df
        self.atributos_disponibles = atributos_disponibles or []
        
        # Limpiar controles existentes
        for widget in self.frame_perfiles.winfo_children():
            widget.destroy()
        
        self.controles_perfiles = {}
        
        if perfiles_df is None:
            # Mostrar mensaje si no hay perfiles
            self.mensaje_perfiles = EstiloUtils.crear_label_con_estilo(
                self.frame_perfiles, 
                "📂 Carga un grafo con hoja 'PERFILES' para configurar ciclistas",
                'Info.TLabel'
            )
            self.mensaje_perfiles.pack(pady=20)
            return
        
        # Crear controles para cada perfil
        for i, (_, perfil_data) in enumerate(perfiles_df.iterrows()):
            self._crear_controles_perfil(self.frame_perfiles, perfil_data, i)
        
        # Actualizar el scroll
        self.frame_perfiles.update_idletasks()
        self.canvas_perfiles.configure(scrollregion=self.canvas_perfiles.bbox("all"))
    
    def _crear_controles_nodo(self, parent, nodo_id: str, index: int, config_actual: Dict[str, Any]):
        """Crea los controles para configurar la distribución de un nodo"""
        # Frame para el nodo
        nodo_frame = EstiloUtils.crear_label_frame_con_estilo(
            parent, 
            f"📍 Nodo: {nodo_id}"
        )
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
        ttk.Label(nodo_frame, text="Tipo:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=0, column=0, sticky=tk.W, pady=2)
        tipo_combo = ttk.Combobox(nodo_frame, textvariable=tipo_var, 
                                 values=['exponencial', 'poisson', 'uniforme'],
                                 state='readonly', width=12)
        tipo_combo.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Selector de unidades de tiempo
        ttk.Label(nodo_frame, text="Unidades:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=0, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        unidades_combo = ttk.Combobox(nodo_frame, textvariable=unidades_var,
                                     values=['segundos', 'minutos', 'horas'],
                                     state='readonly', width=10)
        unidades_combo.grid(row=0, column=3, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Función para actualizar parámetros según el tipo y unidades
        def actualizar_parametros(*args):
            tipo = tipo_var.get()
            unidades = unidades_var.get()
            
            # Mostrar/ocultar controles según el tipo
            if tipo in ['exponencial', 'poisson']:
                # Mostrar solo Lambda
                lambda_label.grid(row=1, column=0, sticky=tk.W, pady=2)
                lambda_spin.grid(row=1, column=1, sticky=tk.W, pady=2, padx=(5, 0))
                min_label.grid_remove()
                min_spin.grid_remove()
                max_label.grid_remove()
                max_spin.grid_remove()
            elif tipo == 'uniforme':
                # Mostrar Min y Max
                lambda_label.grid_remove()
                lambda_spin.grid_remove()
                min_label.grid(row=1, column=0, sticky=tk.W, pady=2)
                min_spin.grid(row=1, column=1, sticky=tk.W, pady=2, padx=(5, 0))
                max_label.grid(row=2, column=0, sticky=tk.W, pady=2)
                max_spin.grid(row=2, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Vincular cambio de tipo con actualización de parámetros
        tipo_var.trace('w', actualizar_parametros)
        unidades_var.trace('w', actualizar_parametros)
        
        # Crear controles de parámetros
        lambda_label = ttk.Label(nodo_frame, text="λ (Lambda):", 
                                font=EstiloUtils.FUENTES['normal'])
        lambda_spin = ttk.Spinbox(nodo_frame, textvariable=lambda_var, width=10)
        
        min_label = ttk.Label(nodo_frame, text="Min (s):", 
                             font=EstiloUtils.FUENTES['normal'])
        min_spin = ttk.Spinbox(nodo_frame, textvariable=min_var, width=10)
        
        max_label = ttk.Label(nodo_frame, text="Max (s):", 
                             font=EstiloUtils.FUENTES['normal'])
        max_spin = ttk.Spinbox(nodo_frame, textvariable=max_var, width=10)
        
        # Inicializar con parámetros por defecto
        actualizar_parametros()
        
        # Botón para aplicar cambios
        aplicar_btn = EstiloUtils.crear_button_con_estilo(
            nodo_frame, 
            "✅ Aplicar", 
            'Accent.TButton',
            command=lambda: self._aplicar_distribucion_nodo(nodo_id)
        )
        aplicar_btn.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Descripción actual
        descripcion = config_actual.get('descripcion', 'Exponencial (λ=0.50)')
        desc_label = EstiloUtils.crear_label_con_estilo(
            nodo_frame, 
            f"Actual: {descripcion}", 
            'Info.TLabel'
        )
        desc_label.grid(row=5, column=0, columnspan=2, pady=2)
        
        # Guardar referencia a la descripción para actualizarla
        self.controles_distribuciones[nodo_id]['descripcion'] = desc_label
    
    def _crear_controles_perfil(self, parent, perfil_data: pd.Series, index: int):
        """Crea los controles para un perfil de ciclista"""
        # Frame principal para el perfil
        perfil_frame = EstiloUtils.crear_label_frame_con_estilo(
            parent, 
            f"🚴 Perfil {perfil_data['PERFILES']}"
        )
        perfil_frame.pack(fill="x", pady=5, padx=5)
        
        # Información del perfil
        info_frame = EstiloUtils.crear_frame_con_estilo(perfil_frame)
        info_frame.pack(fill="x", pady=(0, 10))
        
        # Título del perfil con probabilidad
        titulo_texto = f"Perfil {perfil_data['PERFILES']}"
        if 'PROBABILIDAD' in perfil_data:
            prob_valor = perfil_data['PROBABILIDAD']
            titulo_texto += f" (Prob: {prob_valor:.2f} - {prob_valor*100:.1f}%)"
        
        EstiloUtils.crear_label_con_estilo(
            info_frame, 
            titulo_texto, 
            'Subheader.TLabel'
        ).pack(side=tk.LEFT)
        
        # Botón para editar perfil
        btn_editar = EstiloUtils.crear_button_con_estilo(
            info_frame, 
            "✏️ Editar", 
            'TButton',
            command=lambda p=perfil_data: self._editar_perfil(p)
        )
        btn_editar.pack(side=tk.RIGHT)
        
        # Frame para los pesos
        pesos_frame = EstiloUtils.crear_frame_con_estilo(perfil_frame)
        pesos_frame.pack(fill="x")
        
        # Crear controles para cada peso - solo los atributos disponibles
        mapeo_atributos = {
            'distancia': ('DISTANCIA', '#FF6B6B'),
            'seguridad': ('SEGURIDAD', '#4ECDC4'),
            'luminosidad': ('LUMINOSIDAD', '#45B7D1'),
            'inclinacion': ('INCLINACION', '#96CEB4')
        }
        
        # Filtrar solo los atributos que están disponibles
        atributos_ui = []
        for attr_interno in self.atributos_disponibles:
            if attr_interno in mapeo_atributos:
                col_excel, color = mapeo_atributos[attr_interno]
                if col_excel in perfil_data:
                    atributos_ui.append((col_excel, color))
        
        # Si no hay atributos disponibles, mostrar mensaje
        if not atributos_ui:
            EstiloUtils.crear_label_con_estilo(
                pesos_frame,
                "⚠️ No hay atributos disponibles para este perfil",
                'Info.TLabel'
            ).pack(pady=10)
            return
        
        for i, (peso, color) in enumerate(atributos_ui):
            # Frame para cada peso
            peso_frame = EstiloUtils.crear_frame_con_estilo(pesos_frame)
            peso_frame.grid(row=0, column=i, padx=10, pady=5, sticky="ew")
            pesos_frame.columnconfigure(i, weight=1)
            
            # Label del peso
            EstiloUtils.crear_label_con_estilo(
                peso_frame, 
                peso.title(), 
                'Subheader.TLabel'
            ).pack()
            
            # Solo mostrar el valor numérico sin barra de progreso
            valor = perfil_data[peso]
            valor_label = EstiloUtils.crear_label_con_estilo(
                peso_frame, 
                f"{valor:.2f}", 
                'Info.TLabel'
            )
            valor_label.pack(pady=5)
            
            # Guardar referencias
            self.controles_perfiles[f"perfil_{perfil_data['PERFILES']}_{peso}"] = {
                'valor_label': valor_label,
                'valor': valor
            }
    
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
            if 'aplicar_distribucion' in self.callbacks:
                self.callbacks['aplicar_distribucion'](nodo_id, tipo, parametros)
            
            # Actualizar descripción
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
    
    def _editar_perfil(self, perfil_data: pd.Series):
        """Abre una ventana para editar un perfil de ciclista con UI mejorada"""
        # Crear ventana de edición más compacta
        ventana_edicion = tk.Toplevel(self.parent)
        ventana_edicion.title(f"Editar Perfil {perfil_data['PERFILES']}")
        ventana_edicion.geometry("500x450")
        ventana_edicion.resizable(False, False)
        
        # Centrar la ventana
        EstiloUtils.centrar_ventana(ventana_edicion, 500, 450)
        ventana_edicion.transient(self.parent)
        ventana_edicion.grab_set()
        
        # Frame principal con scroll
        canvas = tk.Canvas(ventana_edicion, highlightthickness=0)
        scrollbar = ttk.Scrollbar(ventana_edicion, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configurar scroll
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Frame principal
        main_frame = EstiloUtils.crear_frame_con_estilo(scrollable_frame)
        main_frame.pack(fill="both", expand=True)
        
        # Título
        EstiloUtils.crear_label_con_estilo(
            main_frame, 
            f"✏️ Editar Perfil {perfil_data['PERFILES']}", 
            'Header.TLabel'
        ).pack(pady=(0, 15))
        
        # Variables para los pesos - solo los atributos disponibles
        pesos_vars = {}
        mapeo_atributos = {
            'distancia': ('DISTANCIA', '#FF6B6B'),
            'seguridad': ('SEGURIDAD', '#4ECDC4'),
            'luminosidad': ('LUMINOSIDAD', '#45B7D1'),
            'inclinacion': ('INCLINACION', '#96CEB4')
        }
        
        # Filtrar solo los atributos que están disponibles
        atributos_ui = []
        for attr_interno in self.atributos_disponibles:
            if attr_interno in mapeo_atributos:
                col_excel, color = mapeo_atributos[attr_interno]
                if col_excel in perfil_data:
                    atributos_ui.append((col_excel, color))
        
        # Frame para pesos de atributos
        pesos_frame = EstiloUtils.crear_label_frame_con_estilo(main_frame, "⚖️ Pesos de Atributos")
        pesos_frame.pack(fill="x", pady=(0, 15))
        
        # Si no hay atributos disponibles, mostrar mensaje
        if not atributos_ui:
            EstiloUtils.crear_label_con_estilo(
                pesos_frame,
                "⚠️ No hay atributos disponibles para este perfil",
                'Info.TLabel'
            ).pack(pady=10)
        else:
            # Crear grid de controles más compacto
            for i, (peso, color) in enumerate(atributos_ui):
                # Frame para cada peso (2 columnas)
                row = i // 2
                col = i % 2
                
                peso_frame = EstiloUtils.crear_frame_con_estilo(pesos_frame)
                peso_frame.grid(row=row, column=col, padx=10, pady=8, sticky="ew")
                pesos_frame.columnconfigure(col, weight=1)
                
                # Label del peso con color
                peso_label = EstiloUtils.crear_label_con_estilo(
                    peso_frame, 
                    f"{peso.title()}", 
                    'Subheader.TLabel'
                )
                peso_label.pack()
                
                # Variable para el peso
                var = tk.DoubleVar(value=perfil_data[peso])
                pesos_vars[peso] = var
                
                # Frame para controles del peso
                controls_frame = EstiloUtils.crear_frame_con_estilo(peso_frame)
                controls_frame.pack(fill="x", pady=2)
                
                # Slider más pequeño
                slider = ttk.Scale(controls_frame, from_=0.0, to=1.0, variable=var, 
                                  orient="horizontal", length=120)
                slider.pack(side=tk.LEFT, fill="x", expand=True)
                
                # Valor numérico
                valor_label = EstiloUtils.crear_label_con_estilo(
                    controls_frame, 
                    f"{var.get():.2f}", 
                    'Info.TLabel'
                )
                valor_label.pack(side=tk.RIGHT, padx=(5, 0))
                
                # Input numérico directo
                spinbox = ttk.Spinbox(controls_frame, from_=0.0, to=1.0, increment=0.01, 
                                     textvariable=var, width=8, format="%.2f")
                spinbox.pack(side=tk.RIGHT, padx=(5, 0))
                
                # Actualizar valor cuando cambie el slider o spinbox
                def update_valor(peso=peso, label=valor_label, var=var):
                    label.config(text=f"{var.get():.2f}")
                var.trace('w', lambda *args, p=peso, l=valor_label, v=var: update_valor(p, l, v))
        
        # Frame para resumen y validación
        resumen_frame = EstiloUtils.crear_label_frame_con_estilo(main_frame, "📊 Resumen")
        resumen_frame.pack(fill="x", pady=(0, 15))
        
        # Labels de resumen
        suma_pesos_label = EstiloUtils.crear_label_con_estilo(
            resumen_frame, 
            "Suma de pesos: 0.00", 
            'Info.TLabel'
        )
        suma_pesos_label.pack(pady=5)
        
        # Función para actualizar resumen
        def actualizar_resumen():
            suma_pesos = sum(var.get() for var in pesos_vars.values())
            
            suma_pesos_label.config(text=f"Suma de pesos: {suma_pesos:.2f}")
            
            # Cambiar color según validación
            if abs(suma_pesos - 1.0) <= 0.01:
                suma_pesos_label.config(foreground='green')
            else:
                suma_pesos_label.config(foreground='red')
        
        # Vincular actualización de resumen
        for var in pesos_vars.values():
            var.trace('w', lambda *args: actualizar_resumen())
        
        # Actualizar resumen inicial
        actualizar_resumen()
        
        # Botones
        botones_frame = EstiloUtils.crear_frame_con_estilo(main_frame)
        botones_frame.pack(fill="x", pady=(10, 0))
        
        def guardar_cambios():
            # Validar que la suma de pesos sea 1.0
            suma_pesos = sum(var.get() for var in pesos_vars.values())
            if abs(suma_pesos - 1.0) > 0.01:
                messagebox.showerror("Error", f"La suma de los pesos debe ser 1.0 (actual: {suma_pesos:.2f})")
                return
            
            # Llamar callback para actualizar perfil
            if 'actualizar_perfil' in self.callbacks:
                self.callbacks['actualizar_perfil'](perfil_data['PERFILES'], pesos_vars)
            
            # Cerrar ventana
            ventana_edicion.destroy()
            
            messagebox.showinfo("Éxito", f"Perfil {perfil_data['PERFILES']} actualizado correctamente")
        
        def normalizar_pesos():
            """Normaliza automáticamente los pesos para que sumen 1.0"""
            suma_pesos = sum(var.get() for var in pesos_vars.values())
            if suma_pesos > 0:
                for var in pesos_vars.values():
                    var.set(var.get() / suma_pesos)
        
        # Botones
        EstiloUtils.crear_button_con_estilo(
            botones_frame, 
            "💾 Guardar", 
            'Success.TButton',
            command=guardar_cambios
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        EstiloUtils.crear_button_con_estilo(
            botones_frame, 
            "⚖️ Normalizar", 
            'TButton',
            command=normalizar_pesos
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        EstiloUtils.crear_button_con_estilo(
            botones_frame, 
            "❌ Cancelar", 
            'Danger.TButton',
            command=ventana_edicion.destroy
        ).pack(side=tk.LEFT)
    
    def obtener_estado_panel(self) -> Dict[str, Any]:
        """Retorna el estado actual del panel"""
        return {
            'grafo_cargado': self.grafo_actual is not None,
            'perfiles_cargados': self.perfiles_df is not None,
            'num_controles_distribuciones': len(self.controles_distribuciones),
            'num_controles_perfiles': len(self.controles_perfiles)
        }
