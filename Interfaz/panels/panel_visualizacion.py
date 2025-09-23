"""
Panel de visualización de la simulación.

Este módulo contiene el panel de visualización con matplotlib
para mostrar el grafo y los ciclistas en tiempo real.
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
from typing import Dict, List, Tuple, Optional, Any, Callable

from ..utils.estilo_utils import EstiloUtils


class PanelVisualizacion:
    """Panel de visualización con matplotlib"""
    
    def __init__(self, parent, callbacks: Dict[str, Callable]):
        self.parent = parent
        self.callbacks = callbacks
        
        # Variables de control
        self.grafo_actual = None
        self.pos_grafo_actual = None
        self.nombre_archivo_excel = None
        
        # Crear el panel
        self.crear_panel()
    
    def crear_panel(self):
        """Crea el panel de visualización principal"""
        # Frame principal
        self.frame_principal = EstiloUtils.crear_label_frame_con_estilo(
            self.parent, 
            "[GRAFICO] VISUALIZACIÓN EN TIEMPO REAL"
        )
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Crear controles de visualización
        self._crear_controles_visualizacion()
        
        # Crear figura de matplotlib
        self._crear_figura_matplotlib()
        
        # Configurar gráfico inicial
        self.configurar_grafico_inicial()
    
    def _crear_controles_visualizacion(self):
        """Crea los controles de visualización"""
        # Frame para controles
        controles_frame = EstiloUtils.crear_frame_con_estilo(self.frame_principal)
        controles_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Configurar grid
        controles_frame.columnconfigure(0, weight=0)  # Label fijo
        controles_frame.columnconfigure(1, weight=1)  # Combobox expandible
        controles_frame.columnconfigure(2, weight=0)  # Botón fijo
        controles_frame.columnconfigure(3, weight=2)  # Info expandible
        
        # Selector de atributo para visualización
        EstiloUtils.crear_label_con_estilo(
            controles_frame, 
            "[OBJETIVO] Mostrar:", 
            'Subheader.TLabel'
        ).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        # Lista desplegable para seleccionar atributo
        self.combo_atributo = ttk.Combobox(controles_frame, state="readonly", width=25)
        self.combo_atributo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Botón para aplicar cambios
        self.btn_aplicar = EstiloUtils.crear_button_con_estilo(
            controles_frame, 
            "[OK] Aplicar", 
            'Accent.TButton',
            command=self._aplicar_visualizacion
        )
        self.btn_aplicar.grid(row=0, column=2, sticky=tk.W, padx=(0, 15))
        
        # Información sobre la simulación
        self.info_simulacion_label = EstiloUtils.crear_label_con_estilo(
            controles_frame, 
            "[INFO] Simulación: distancias reales | Usa 'Aplicar' para actualizar", 
            'Info.TLabel'
        )
        self.info_simulacion_label.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(15, 0))
    
    def _crear_figura_matplotlib(self):
        """Crea la figura de matplotlib"""
        # Crear figura con configuración optimizada
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        
        # Configurar estilo de matplotlib optimizado
        plt.style.use('default')
        self.ax.set_facecolor('#f8f9fa')
        
        # Optimizaciones de rendimiento
        self.fig.patch.set_facecolor('#f8f9fa')
        self.ax.set_autoscale_on(False)  # Desactivar autoescalado para mejor rendimiento
        
        # Crear canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self.frame_principal)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Configurar eventos
        self.canvas.mpl_connect('button_press_event', self._on_click)
        
        # Variables para control de actualización
        self._ultima_actualizacion = 0
        self._intervalo_actualizacion = 0.1  # Actualizar máximo cada 100ms
    
    def _on_click(self, event):
        """Maneja clics en el gráfico"""
        if event.inaxes == self.ax and event.button == 1:  # Clic izquierdo
            if 'click_grafico' in self.callbacks:
                self.callbacks['click_grafico'](event.xdata, event.ydata)
    
    def _aplicar_visualizacion(self):
        """Aplica la visualización seleccionada"""
        if 'actualizar_visualizacion' in self.callbacks:
            self.callbacks['actualizar_visualizacion']()
    
    def configurar_grafico_inicial(self):
        """Configura el gráfico inicial sin grafo cargado"""
        self.ax.clear()
        self.ax.set_title("[BICICLETA] SIMULADOR DE CICLORUTAS v2.0", 
                         fontsize=14, fontweight='bold', color='#212529', pad=15)
        self.ax.set_xlabel("Distancia (metros)", fontsize=12, fontweight='bold', color='#495057')
        self.ax.set_ylabel("Desviación (metros)", fontsize=12, fontweight='bold', color='#495057')
        self.ax.grid(True, alpha=0.3, color='#adb5bd', linestyle='-', linewidth=0.5)
        
        # Configurar ejes elegantes
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#6c757d')
        self.ax.spines['bottom'].set_color('#6c757d')
        
        # NO dibujar red básica - solo mostrar mensaje
        # self._dibujar_red_basica()  # COMENTADO: No dibujar puntos y tramos
        
        # Scatter plot para ciclistas (vacío inicialmente)
        self.scatter = self.ax.scatter([], [], s=120, alpha=0.95, edgecolors='white', 
                                     linewidth=2, zorder=10)
        
        # Mensaje inicial - SOLO mensaje, sin red básica
        self.ax.text(0.5, 0.5, '[ARCHIVO] Carga un grafo Excel para comenzar la simulación\n\n' +
                    'El grafo debe tener:\n' +
                    '• Hoja "NODOS" con lista de nodos\n' +
                    '• Hoja "ARCOS" con origen, destino y peso\n\n' +
                    'Una vez cargado el grafo, podrás:\n' +
                    '• Configurar distribuciones por nodo\n' +
                    '• Iniciar la simulación en tiempo real\n' +
                    '• Visualizar ciclistas en movimiento', 
                    transform=self.ax.transAxes, fontsize=11, ha='center', va='center',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))
        
        # Configurar límites del gráfico para centrar el mensaje
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        
        self.canvas.draw_idle()
    
    def _dibujar_red_basica(self):
        """Dibuja la red básica en forma de Y"""
        # Definir puntos de la red
        puntos = {
            'A': (0, 0),
            'X': (50, 0),
            'B': (50, 30),
            'C': (50, -30)
        }
        
        # Dibujar nodos
        for nombre, (x, y) in puntos.items():
            self.ax.plot(x, y, 'o', markersize=12, color='#2E86AB', markeredgecolor='white', 
                        markeredgewidth=2, zorder=5)
            self.ax.text(x, y+5, nombre, ha='center', va='bottom', fontsize=12, 
                        fontweight='bold', color='#2E86AB', zorder=6)
        
        # Dibujar arcos
        arcos = [
            (puntos['A'], puntos['X'], '#AAB7B8', 3),  # A→X (gris)
            (puntos['X'], puntos['B'], '#4ECDC4', 3),  # X→B (azul)
            (puntos['X'], puntos['C'], '#FF6B6B', 3)   # X→C (rojo)
        ]
        
        for (x1, y1), (x2, y2), color, width in arcos:
            self.ax.plot([x1, x2], [y1, y2], color=color, linewidth=width, 
                        alpha=0.8, zorder=4)
        
        # Configurar límites del gráfico
        self.ax.set_xlim(-10, 60)
        self.ax.set_ylim(-40, 40)
    
    def configurar_grafico_con_grafo(self, grafo: nx.Graph, pos_grafo: Dict, nombre_archivo: str = None):
        """Configura el gráfico cuando hay un grafo cargado"""
        self.grafo_actual = grafo
        self.pos_grafo_actual = pos_grafo
        self.nombre_archivo_excel = nombre_archivo
        
        self.ax.clear()
        
        # Dibujar el grafo NetworkX
        nx.draw(grafo, pos_grafo, ax=self.ax, 
                with_labels=True, node_color="#2E86AB", edge_color="#AAB7B8",
                node_size=800, font_size=10, font_color="white", font_weight='bold')
        
        # Agregar etiquetas de peso en los arcos
        self._agregar_etiquetas_arcos()
        
        # Configurar el gráfico
        titulo = "[BICICLETA] RED CICLORUTAS"
        if nombre_archivo:
            titulo += f" | [ARCHIVO] {nombre_archivo}"
        
        self.ax.set_title(titulo, fontsize=14, fontweight='bold', color='#212529', pad=15)
        self.ax.set_xlabel("Coordenada X", fontsize=12, fontweight='bold', color='#495057')
        self.ax.set_ylabel("Coordenada Y", fontsize=12, fontweight='bold', color='#495057')
        
        # Configurar ejes elegantes
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#6c757d')
        self.ax.spines['bottom'].set_color('#6c757d')
        
        # Scatter plot para ciclistas con zorder alto
        self.scatter = self.ax.scatter([], [], s=120, alpha=0.95, edgecolors='white', 
                                     linewidth=2, zorder=10)
        
        self.canvas.draw_idle()
    
    def _agregar_etiquetas_arcos(self):
        """Agrega etiquetas a los arcos del grafo"""
        if not self.grafo_actual or not self.pos_grafo_actual:
            return
        
        etiquetas = {}
        atributo_seleccionado = self.combo_atributo.get()
        
        for edge in self.grafo_actual.edges(data=True):
            origen, destino, datos = edge
            valor_mostrar = self._obtener_valor_mostrar(datos, atributo_seleccionado)
            
            if valor_mostrar is not None:
                etiquetas[(origen, destino)] = valor_mostrar
        
        # Dibujar etiquetas
        nx.draw_networkx_edge_labels(self.grafo_actual, self.pos_grafo_actual, 
                                   edge_labels=etiquetas, ax=self.ax, font_size=8)
    
    def _obtener_valor_mostrar(self, datos_arco: Dict, atributo_seleccionado: str) -> Optional[str]:
        """Obtiene el valor a mostrar para un arco según la selección"""
        if not atributo_seleccionado:
            return None
        
        # Determinar qué valor mostrar según la selección
        if "Distancia Real (Simulación)" in atributo_seleccionado:
            if 'distancia_real' in datos_arco:
                return f"{datos_arco['distancia_real']:.0f}m"
            elif 'distancia' in datos_arco:
                return f"{datos_arco['distancia']:.0f}m"
            elif 'weight' in datos_arco and datos_arco['weight'] >= 10.0:
                return f"{datos_arco['weight']:.0f}m"
                
        elif "Distancia Original" in atributo_seleccionado:
            if 'distancia' in datos_arco:
                return f"{datos_arco['distancia']:.0f}m"
            elif 'weight' in datos_arco and datos_arco['weight'] >= 10.0:
                return f"{datos_arco['weight']:.0f}m"
        
        else:
            # Buscar atributo específico seleccionado
            attr_name = atributo_seleccionado.split(' ', 1)[-1].lower()
            
            # Mapear nombres de atributos
            attr_mapping = {
                'seguridad': 'seguridad',
                'luminosidad': 'luminosidad', 
                'inclinacion': 'inclinacion',
                'safety': 'seguridad',
                'luminosity': 'luminosidad',
                'inclination': 'inclinacion'
            }
            
            attr_key = attr_mapping.get(attr_name, attr_name)
            
            if attr_key in datos_arco:
                valor = datos_arco[attr_key]
                if attr_key in ['seguridad', 'luminosidad']:
                    return f"{valor:.1f}/10"
                elif attr_key == 'inclinacion':
                    return f"{valor:.1f}%"
                else:
                    return f"{valor:.2f}"
        
        return None
    
    def actualizar_visualizacion(self, ciclistas_activos: Dict[str, List] = None):
        """Actualiza la visualización con los datos actuales"""
        if not hasattr(self, 'scatter'):
            return
        
        # Control de frecuencia de actualización para optimizar rendimiento
        import time
        tiempo_actual = time.time()
        if tiempo_actual - self._ultima_actualizacion < self._intervalo_actualizacion:
            return  # Saltar esta actualización si es muy frecuente
        
        self._ultima_actualizacion = tiempo_actual
        
        # Si no se proporcionan datos, usar datos vacíos
        if ciclistas_activos is None:
            ciclistas_activos = {
                'coordenadas': [],
                'colores': [],
                'ruta_actual': [],
                'velocidades': [],
                'trayectorias': []
            }
        
        try:
            if not ciclistas_activos['coordenadas']:
                # No hay ciclistas activos para mostrar
                import numpy as np
                self.scatter.set_offsets(np.empty((0, 2)))  # Array 2D vacío
                self.canvas.draw_idle()
                return
            
            # Verificar que las coordenadas tengan el formato correcto
            coordenadas = ciclistas_activos['coordenadas']
            
            if not coordenadas or len(coordenadas) == 0:
                import numpy as np
                self.scatter.set_offsets(np.empty((0, 2)))  # Array 2D vacío
                self.canvas.draw_idle()
                return
            
            # Verificar que las coordenadas sean una lista
            if not isinstance(coordenadas, list):
                print(f"⚠️ Coordenadas no es una lista: {type(coordenadas)}")
                import numpy as np
                self.scatter.set_offsets(np.empty((0, 2)))  # Array 2D vacío
                self.canvas.draw_idle()
                return
            
            # Verificar que la lista no esté vacía
            if len(coordenadas) == 0:
                import numpy as np
                self.scatter.set_offsets(np.empty((0, 2)))  # Array 2D vacío
                self.canvas.draw_idle()
                return
            
            # Verificar que el primer elemento sea una tupla válida
            # Manejar tanto listas como arrays de numpy
            try:
                primer_elemento = coordenadas[0]
                if not isinstance(primer_elemento, (tuple, list)) or len(primer_elemento) != 2:
                    print(f"⚠️ Formato de coordenadas inválido: {type(primer_elemento)} - {primer_elemento}")
                    import numpy as np
                    self.scatter.set_offsets(np.empty((0, 2)))  # Array 2D vacío
                    self.canvas.draw_idle()
                    return
            except (IndexError, TypeError) as e:
                print(f"⚠️ Error accediendo a coordenadas[0]: {e}")
                import numpy as np
                self.scatter.set_offsets(np.empty((0, 2)))  # Array 2D vacío
                self.canvas.draw_idle()
                return
            
            # Extraer coordenadas de ciclistas activos
            try:
                # Convertir a lista si es un array de numpy
                if hasattr(coordenadas, 'tolist'):
                    coordenadas = coordenadas.tolist()
                elif not isinstance(coordenadas, list):
                    coordenadas = list(coordenadas)
                
                # Verificar que todas las coordenadas sean tuplas válidas
                coordenadas_validas = []
                for coord in coordenadas:
                    if isinstance(coord, (tuple, list)) and len(coord) == 2:
                        try:
                            x_val = float(coord[0])
                            y_val = float(coord[1])
                            coordenadas_validas.append((x_val, y_val))
                        except (ValueError, TypeError):
                            print(f"⚠️ Coordenada inválida ignorada: {coord}")
                            continue
                    else:
                        print(f"⚠️ Formato de coordenada inválido ignorado: {coord}")
                        continue
                
                if not coordenadas_validas:
                    print("⚠️ No hay coordenadas válidas para mostrar")
                    import numpy as np
                    self.scatter.set_offsets(np.empty((0, 2)))  # Array 2D vacío
                    self.canvas.draw_idle()
                    return
                
                x, y = zip(*coordenadas_validas)
            except (ValueError, TypeError) as e:
                print(f"⚠️ Error procesando coordenadas: {e}")
                import numpy as np
                self.scatter.set_offsets(np.empty((0, 2)))  # Array 2D vacío
                self.canvas.draw_idle()
                return
            
            # Actualizar posiciones de los ciclistas activos
            self.scatter.set_offsets(list(zip(x, y)))
            
            # Ajustar colores para que coincidan con el número de coordenadas válidas
            num_coordenadas_validas = len(coordenadas_validas)
            colores_ajustados = ciclistas_activos['colores'][:num_coordenadas_validas]
            if len(colores_ajustados) < num_coordenadas_validas:
                # Si no hay suficientes colores, usar el último color disponible
                color_default = colores_ajustados[-1] if colores_ajustados else '#6C757D'
                colores_ajustados.extend([color_default] * (num_coordenadas_validas - len(colores_ajustados)))
            
            self.scatter.set_color(colores_ajustados)
            
            # Configurar apariencia de los ciclistas activos
            self.scatter.set_sizes([120] * num_coordenadas_validas)
            self.scatter.set_alpha(0.95)
            
            # Configurar bordes según si hay grafo o no
            if self.grafo_actual:
                # Con grafo: bordes blancos para contraste
                self.scatter.set_edgecolors('white')
                self.scatter.set_linewidth(2)
            else:
                # Sin grafo: bordes blancos para contraste con la red básica
                self.scatter.set_edgecolors('white')
                self.scatter.set_linewidth(2)
            
            # Actualizar canvas de forma optimizada
            self.canvas.draw_idle()  # draw_idle es más eficiente que draw()
            
        except Exception as e:
            print(f"⚠️ Error actualizando visualización: {e}")
            # En caso de error, intentar redibujar el gráfico
            if self.grafo_actual:
                self.configurar_grafico_con_grafo(self.grafo_actual, self.pos_grafo_actual, self.nombre_archivo_excel)
            else:
                self.configurar_grafico_inicial()
    
    def limpiar_mensaje_inicial(self):
        """Limpia el mensaje inicial para mostrar la simulación"""
        # Limpiar el texto del mensaje inicial
        for text in self.ax.texts:
            if 'Simulador de Ciclorutas v2.0' in text.get_text():
                text.remove()
                break
        self.canvas.draw_idle()
    
    def actualizar_controles_visualizacion(self, atributos_disponibles: List[str]):
        """Actualiza la lista desplegable con los atributos disponibles"""
        if not atributos_disponibles:
            # Sin atributos: deshabilitar controles
            self.combo_atributo.config(state='disabled')
            self.combo_atributo['values'] = []
            self.btn_aplicar.config(state='disabled')
            self.info_simulacion_label.config(text="[INFO] Carga un grafo para ver sus atributos reales")
            return
        
        # Crear lista de opciones para el combobox
        opciones = []
        
        # Agregar opciones especiales solo si existen en el grafo
        if 'distancia_real' in atributos_disponibles:
            opciones.append("[DISTANCIA] Distancia Real (Simulación)")
        if 'distancia' in atributos_disponibles:
            opciones.append("[DISTANCIA] Distancia Original")
        
        # Agregar todos los atributos individuales que están realmente en el grafo
        for attr in sorted(atributos_disponibles):
            if attr not in ['distancia_real', 'distancia']:
                # Agregar prefijo según el tipo de atributo
                if attr.lower() in ['seguridad', 'safety']:
                    opciones.append(f"[SEGURIDAD] {attr.title()}")
                elif attr.lower() in ['luminosidad', 'luminosity', 'light']:
                    opciones.append(f"[LUZ] {attr.title()}")
                elif attr.lower() in ['inclinacion', 'inclination', 'slope']:
                    opciones.append(f"[MONTAÑA] {attr.title()}")
                else:
                    opciones.append(f"[DATOS] {attr.title()}")
        
        # Actualizar combobox
        self.combo_atributo['values'] = opciones
        self.combo_atributo.config(state='readonly')
        
        # Habilitar botón aplicar
        self.btn_aplicar.config(state='normal')
        
        # Seleccionar "Distancia Real (Simulación)" por defecto si está disponible
        if opciones:
            if "[DISTANCIA] Distancia Real (Simulación)" in opciones:
                self.combo_atributo.set("[DISTANCIA] Distancia Real (Simulación)")
            else:
                self.combo_atributo.set(opciones[0])
        
        # Actualizar información
        num_atributos = len(atributos_disponibles)
        if num_atributos > 1:
            self.info_simulacion_label.config(text=f"[INFO] Simulación: distancias reales | Visualización: {num_atributos} atributos reales")
        else:
            self.info_simulacion_label.config(text="[INFO] Simulación: distancias reales | Visualización: solo distancias")
    
    def obtener_atributo_seleccionado(self) -> str:
        """Retorna el atributo actualmente seleccionado"""
        return self.combo_atributo.get()
    
    def establecer_atributo_seleccionado(self, atributo: str):
        """Establece el atributo seleccionado"""
        self.combo_atributo.set(atributo)
    
    def limpiar_visualizacion(self):
        """Limpia la visualización actual"""
        if hasattr(self, 'scatter'):
            import numpy as np
            self.scatter.set_offsets(np.empty((0, 2)))  # Array 2D vacío
            self.canvas.draw_idle()
    
    def redibujar_grafo(self):
        """Redibuja el grafo con la configuración actual"""
        if self.grafo_actual and self.pos_grafo_actual:
            self.configurar_grafico_con_grafo(self.grafo_actual, self.pos_grafo_actual, self.nombre_archivo_excel)
    
    def obtener_estado_panel(self) -> Dict[str, Any]:
        """Retorna el estado actual del panel"""
        return {
            'atributo_seleccionado': self.combo_atributo.get(),
            'grafo_cargado': self.grafo_actual is not None,
            'nombre_archivo': self.nombre_archivo_excel
        }
