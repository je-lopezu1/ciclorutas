"""
Panel de estadísticas de la simulación.

Este módulo contiene el panel de estadísticas que muestra métricas
en tiempo real de la simulación.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Any, Callable

from ..utils.estilo_utils import EstiloUtils


class PanelEstadisticas:
    """Panel de estadísticas con métricas en tiempo real"""
    
    def __init__(self, parent, callbacks: Dict[str, Callable]):
        self.parent = parent
        self.callbacks = callbacks
        
        # Diccionario para almacenar referencias a los labels
        self.stats_labels = {}
        
        # Crear el panel
        self.crear_panel()
    
    def crear_panel(self):
        """Crea el panel de estadísticas principal"""
        # Frame principal
        self.frame_principal = EstiloUtils.crear_label_frame_con_estilo(
            self.parent, 
            "📈 ESTADÍSTICAS DE SIMULACIÓN"
        )
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Crear el contenido del panel
        self._crear_contenido_estadisticas()
    
    def _crear_contenido_estadisticas(self):
        """Crea el contenido principal del panel de estadísticas"""
        # Frame interno para estadísticas
        stats_inner = EstiloUtils.crear_frame_con_estilo(self.frame_principal)
        stats_inner.pack(fill=tk.BOTH, expand=True)
        
        # Configurar grid responsivo
        EstiloUtils.configurar_grid_responsivo(stats_inner, 10)
        
        # Crear secciones de estadísticas
        self._crear_seccion_estadisticas_basicas(stats_inner, 0)
        self._crear_seccion_estadisticas_grafo(stats_inner, 1)
        self._crear_seccion_estadisticas_distribuciones(stats_inner, 2)
        self._crear_seccion_estadisticas_rutas(stats_inner, 3)
        self._crear_seccion_estadisticas_adicionales(stats_inner, 4)
        self._crear_seccion_estadisticas_atributos(stats_inner, 5)
        self._crear_seccion_estadisticas_perfiles(stats_inner, 6)
    
    def _crear_seccion_estadisticas_basicas(self, parent, fila_inicio):
        """Crea la sección de estadísticas básicas"""
        # Primera fila - Estadísticas básicas
        ttk.Label(parent, text="Ciclistas Activos:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=fila_inicio, column=0, sticky=tk.W, padx=5)
        self.stats_labels['total_ciclistas'] = EstiloUtils.crear_label_con_estilo(
            parent, "0", 'Info.TLabel'
        )
        self.stats_labels['total_ciclistas'].grid(row=fila_inicio, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(parent, text="Velocidad Promedio:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=fila_inicio, column=2, sticky=tk.W, padx=5)
        self.stats_labels['velocidad_promedio'] = EstiloUtils.crear_label_con_estilo(
            parent, "0.0 m/s", 'Info.TLabel'
        )
        self.stats_labels['velocidad_promedio'].grid(row=fila_inicio, column=3, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(parent, text="Velocidad Mín:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=fila_inicio, column=4, sticky=tk.W, padx=5)
        self.stats_labels['velocidad_min'] = EstiloUtils.crear_label_con_estilo(
            parent, "0.0 m/s", 'Info.TLabel'
        )
        self.stats_labels['velocidad_min'].grid(row=fila_inicio, column=5, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(parent, text="Velocidad Máx:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=fila_inicio, column=6, sticky=tk.W, padx=5)
        self.stats_labels['velocidad_max'] = EstiloUtils.crear_label_con_estilo(
            parent, "0.0 m/s", 'Info.TLabel'
        )
        self.stats_labels['velocidad_max'].grid(row=fila_inicio, column=7, sticky=tk.W, padx=(0, 20))
    
    def _crear_seccion_estadisticas_grafo(self, parent, fila_inicio):
        """Crea la sección de estadísticas del grafo"""
        # Segunda fila - Estadísticas del grafo
        ttk.Label(parent, text="Nodos del Grafo:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=fila_inicio, column=0, sticky=tk.W, padx=5, pady=5)
        self.stats_labels['grafo_nodos'] = EstiloUtils.crear_label_con_estilo(
            parent, "0", 'Info.TLabel'
        )
        self.stats_labels['grafo_nodos'].grid(row=fila_inicio, column=1, sticky=tk.W, padx=(0, 20), pady=5)
        
        ttk.Label(parent, text="Arcos del Grafo:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=fila_inicio, column=2, sticky=tk.W, padx=5, pady=5)
        self.stats_labels['grafo_arcos'] = EstiloUtils.crear_label_con_estilo(
            parent, "0", 'Info.TLabel'
        )
        self.stats_labels['grafo_arcos'].grid(row=fila_inicio, column=3, sticky=tk.W, padx=(0, 20), pady=5)
        
        ttk.Label(parent, text="Modo:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=fila_inicio, column=4, sticky=tk.W, padx=5, pady=5)
        self.stats_labels['modo_simulacion'] = EstiloUtils.crear_label_con_estilo(
            parent, "Original", 'Info.TLabel'
        )
        self.stats_labels['modo_simulacion'].grid(row=fila_inicio, column=5, sticky=tk.W, padx=(0, 20), pady=5)
    
    def _crear_seccion_estadisticas_distribuciones(self, parent, fila_inicio):
        """Crea la sección de estadísticas de distribuciones"""
        # Tercera fila - Estadísticas de distribuciones
        ttk.Label(parent, text="Distribuciones:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=fila_inicio, column=0, sticky=tk.W, padx=5)
        self.stats_labels['distribuciones_configuradas'] = EstiloUtils.crear_label_con_estilo(
            parent, "0", 'Info.TLabel'
        )
        self.stats_labels['distribuciones_configuradas'].grid(row=fila_inicio, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(parent, text="Tasa Promedio:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=fila_inicio, column=2, sticky=tk.W, padx=5)
        self.stats_labels['tasa_arribo_promedio'] = EstiloUtils.crear_label_con_estilo(
            parent, "0.0", 'Info.TLabel'
        )
        self.stats_labels['tasa_arribo_promedio'].grid(row=fila_inicio, column=3, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(parent, text="Duración:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=fila_inicio, column=4, sticky=tk.W, padx=5)
        self.stats_labels['duracion_simulacion'] = EstiloUtils.crear_label_con_estilo(
            parent, "300s", 'Info.TLabel'
        )
        self.stats_labels['duracion_simulacion'].grid(row=fila_inicio, column=5, sticky=tk.W, padx=(0, 20))
    
    def _crear_seccion_estadisticas_rutas(self, parent, fila_inicio):
        """Crea la sección de estadísticas de rutas"""
        # Cuarta fila - Estadísticas de rutas
        ttk.Label(parent, text="Rutas Utilizadas:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=fila_inicio, column=0, sticky=tk.W, padx=5, pady=5)
        self.stats_labels['rutas_utilizadas'] = EstiloUtils.crear_label_con_estilo(
            parent, "0", 'Info.TLabel'
        )
        self.stats_labels['rutas_utilizadas'].grid(row=fila_inicio, column=1, sticky=tk.W, padx=(0, 20), pady=5)
        
        ttk.Label(parent, text="Total Viajes:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=fila_inicio, column=2, sticky=tk.W, padx=5, pady=5)
        self.stats_labels['total_viajes'] = EstiloUtils.crear_label_con_estilo(
            parent, "0", 'Info.TLabel'
        )
        self.stats_labels['total_viajes'].grid(row=fila_inicio, column=3, sticky=tk.W, padx=(0, 20), pady=5)
        
        ttk.Label(parent, text="Ruta Más Usada:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=fila_inicio, column=4, sticky=tk.W, padx=5, pady=5)
        self.stats_labels['ruta_mas_usada'] = EstiloUtils.crear_label_con_estilo(
            parent, "N/A", 'Info.TLabel'
        )
        self.stats_labels['ruta_mas_usada'].grid(row=fila_inicio, column=5, sticky=tk.W, padx=(0, 20), pady=5)
    
    def _crear_seccion_estadisticas_adicionales(self, parent, fila_inicio):
        """Crea la sección de estadísticas adicionales"""
        # Quinta fila - Estadísticas adicionales
        ttk.Label(parent, text="Ciclistas Completados:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=fila_inicio, column=0, sticky=tk.W, padx=5, pady=5)
        self.stats_labels['ciclistas_completados'] = EstiloUtils.crear_label_con_estilo(
            parent, "0", 'Success.TLabel'
        )
        self.stats_labels['ciclistas_completados'].grid(row=fila_inicio, column=1, sticky=tk.W, padx=(0, 20), pady=5)
        
        ttk.Label(parent, text="Nodo Más Activo:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=fila_inicio, column=2, sticky=tk.W, padx=5, pady=5)
        self.stats_labels['nodo_mas_activo'] = EstiloUtils.crear_label_con_estilo(
            parent, "N/A", 'Info.TLabel'
        )
        self.stats_labels['nodo_mas_activo'].grid(row=fila_inicio, column=3, sticky=tk.W, padx=(0, 20), pady=5)
    
    def _crear_seccion_estadisticas_atributos(self, parent, fila_inicio):
        """Crea la sección de estadísticas de atributos"""
        # Sexta fila - Información de atributos
        ttk.Label(parent, text="Atributos:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=fila_inicio, column=0, sticky=tk.W, padx=5, pady=5)
        self.stats_labels['atributos_disponibles'] = EstiloUtils.crear_label_con_estilo(
            parent, "0", 'Info.TLabel'
        )
        self.stats_labels['atributos_disponibles'].grid(row=fila_inicio, column=1, sticky=tk.W, padx=(0, 20), pady=5)
        
        ttk.Label(parent, text="Sistema Pesos:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=fila_inicio, column=2, sticky=tk.W, padx=5, pady=5)
        self.stats_labels['peso_compuesto'] = EstiloUtils.crear_label_con_estilo(
            parent, "Simple", 'Info.TLabel'
        )
        self.stats_labels['peso_compuesto'].grid(row=fila_inicio, column=3, sticky=tk.W, padx=(0, 20), pady=5)
    
    def _crear_seccion_estadisticas_perfiles(self, parent, fila_inicio):
        """Crea la sección de estadísticas de perfiles"""
        # Séptima fila - Información de perfiles y rutas
        ttk.Label(parent, text="Perfiles:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=fila_inicio, column=0, sticky=tk.W, padx=5, pady=5)
        self.stats_labels['perfiles_disponibles'] = EstiloUtils.crear_label_con_estilo(
            parent, "0", 'Info.TLabel'
        )
        self.stats_labels['perfiles_disponibles'].grid(row=fila_inicio, column=1, sticky=tk.W, padx=(0, 20), pady=5)
        
        ttk.Label(parent, text="Matriz Rutas:", 
                 font=EstiloUtils.FUENTES['normal']).grid(row=fila_inicio, column=2, sticky=tk.W, padx=5, pady=5)
        self.stats_labels['matriz_rutas'] = EstiloUtils.crear_label_con_estilo(
            parent, "No", 'Info.TLabel'
        )
        self.stats_labels['matriz_rutas'].grid(row=fila_inicio, column=3, sticky=tk.W, padx=(0, 20), pady=5)
    
    def actualizar_estadisticas(self, stats: Dict[str, Any]):
        """Actualiza las estadísticas mostradas"""
        try:
            # Estadísticas básicas
            self._actualizar_estadistica('total_ciclistas', stats.get('ciclistas_activos', 0))
            self._actualizar_estadistica('velocidad_promedio', f"{stats.get('velocidad_promedio', 0):.1f} m/s")
            self._actualizar_estadistica('velocidad_min', f"{stats.get('velocidad_minima', 0):.1f} m/s")
            self._actualizar_estadistica('velocidad_max', f"{stats.get('velocidad_maxima', 0):.1f} m/s")
            self._actualizar_estadistica('duracion_simulacion', f"{stats.get('duracion_simulacion', 300):.0f}s")
            
            # Estadísticas del grafo
            if stats.get('usando_grafo_real', False):
                self._actualizar_estadistica('grafo_nodos', stats.get('grafo_nodos', 0))
                self._actualizar_estadistica('grafo_arcos', stats.get('grafo_arcos', 0))
                self._actualizar_estadistica('modo_simulacion', "Grafo Real", 'exito')
                
                # Estadísticas de distribuciones
                self._actualizar_estadistica('distribuciones_configuradas', stats.get('distribuciones_configuradas', 0))
                tasa_promedio = stats.get('tasa_arribo_promedio', 0)
                self._actualizar_estadistica('tasa_arribo_promedio', f"{tasa_promedio:.2f}")
            else:
                self._actualizar_estadistica('grafo_nodos', "0")
                self._actualizar_estadistica('grafo_arcos', "0")
                self._actualizar_estadistica('modo_simulacion', "Sistema Original", 'info')
                self._actualizar_estadistica('distribuciones_configuradas', "0")
                self._actualizar_estadistica('tasa_arribo_promedio', "0.0")
            
            # Estadísticas de rutas
            self._actualizar_estadistica('rutas_utilizadas', stats.get('rutas_utilizadas', 0))
            self._actualizar_estadistica('total_viajes', stats.get('total_viajes', 0))
            
            # Ruta más usada (truncar si es muy larga)
            ruta_mas_usada = stats.get('ruta_mas_usada', 'N/A')
            if len(ruta_mas_usada) > 30:
                ruta_mas_usada = ruta_mas_usada[:27] + "..."
            self._actualizar_estadistica('ruta_mas_usada', ruta_mas_usada)
            
            # Ciclistas completados
            self._actualizar_estadistica('ciclistas_completados', stats.get('ciclistas_completados', 0), 'exito')
            
            # Nodo más activo (truncar si es muy largo)
            nodo_mas_activo = stats.get('nodo_mas_activo', 'N/A')
            if len(nodo_mas_activo) > 25:
                nodo_mas_activo = nodo_mas_activo[:22] + "..."
            self._actualizar_estadistica('nodo_mas_activo', nodo_mas_activo)
            
            # Información de atributos (si está disponible)
            self._actualizar_atributos_disponibles(stats)
            
            # Información de perfiles y rutas (si está disponible)
            self._actualizar_perfiles_rutas(stats)
            
        except Exception as e:
            print(f"⚠️ Error actualizando estadísticas: {e}")
    
    def _actualizar_estadistica(self, key: str, valor: Any, tipo: str = 'normal'):
        """Actualiza una estadística específica"""
        if key in self.stats_labels:
            EstiloUtils.aplicar_estilo_estadistica(self.stats_labels[key], valor, tipo)
    
    def _actualizar_atributos_disponibles(self, stats: Dict[str, Any]):
        """Actualiza la información de atributos disponibles"""
        # Obtener información del grafo actual si está disponible
        grafo_actual = self.callbacks.get('obtener_grafo_actual', lambda: None)()
        if grafo_actual:
            # Contar atributos disponibles en los arcos
            atributos_encontrados = set()
            for edge in grafo_actual.edges(data=True):
                for key in edge[2].keys():
                    if key not in ['weight']:
                        atributos_encontrados.add(key)
            
            num_atributos = len(atributos_encontrados)
            
            # Verificar tipo de sistema de pesos
            tiene_distancia_real = any('distancia_real' in edge[2] for edge in grafo_actual.edges(data=True))
            tiene_atributos_multiples = len(atributos_encontrados) > 1
            
            if tiene_distancia_real and tiene_atributos_multiples:
                sistema_pesos = "Dinámico"
            elif tiene_distancia_real:
                sistema_pesos = "Real"
            elif tiene_atributos_multiples:
                sistema_pesos = "Atributos"
            else:
                sistema_pesos = "Simple"
            
            self._actualizar_estadistica('atributos_disponibles', str(num_atributos))
            self._actualizar_estadistica('peso_compuesto', sistema_pesos, 
                                       'exito' if sistema_pesos in ['Dinámico', 'Real', 'Atributos'] else 'info')
        else:
            self._actualizar_estadistica('atributos_disponibles', "0")
            self._actualizar_estadistica('peso_compuesto', "Simple", 'info')
    
    def _actualizar_perfiles_rutas(self, stats: Dict[str, Any]):
        """Actualiza la información de perfiles y rutas"""
        # Obtener información de perfiles y rutas si están disponibles
        num_perfiles = 0
        tiene_matriz = False
        
        perfiles_df = self.callbacks.get('obtener_perfiles_df', lambda: None)()
        rutas_df = self.callbacks.get('obtener_rutas_df', lambda: None)()
        
        if perfiles_df is not None:
            num_perfiles = len(perfiles_df)
        
        if rutas_df is not None:
            tiene_matriz = True
        
        self._actualizar_estadistica('perfiles_disponibles', str(num_perfiles))
        self._actualizar_estadistica('matriz_rutas', "Sí" if tiene_matriz else "No", 
                                   'exito' if tiene_matriz else 'info')
    
    def establecer_atributos_disponibles(self, num_atributos: int, sistema_pesos: str):
        """Establece la información de atributos disponibles"""
        self._actualizar_estadistica('atributos_disponibles', str(num_atributos))
        
        # Determinar color según el tipo de sistema
        if sistema_pesos in ['Dinámico', 'Real', 'Atributos']:
            self._actualizar_estadistica('peso_compuesto', sistema_pesos, 'exito')
        else:
            self._actualizar_estadistica('peso_compuesto', sistema_pesos, 'info')
    
    def establecer_perfiles_rutas(self, num_perfiles: int, tiene_matriz: bool):
        """Establece la información de perfiles y rutas"""
        self._actualizar_estadistica('perfiles_disponibles', str(num_perfiles))
        
        if tiene_matriz:
            self._actualizar_estadistica('matriz_rutas', "Sí", 'exito')
        else:
            self._actualizar_estadistica('matriz_rutas', "No", 'info')
    
    def limpiar_estadisticas(self):
        """Limpia todas las estadísticas"""
        valores_por_defecto = {
            'total_ciclistas': "0",
            'velocidad_promedio': "0.0 m/s",
            'velocidad_min': "0.0 m/s",
            'velocidad_max': "0.0 m/s",
            'grafo_nodos': "0",
            'grafo_arcos': "0",
            'modo_simulacion': "Original",
            'distribuciones_configuradas': "0",
            'tasa_arribo_promedio': "0.0",
            'duracion_simulacion': "300s",
            'rutas_utilizadas': "0",
            'total_viajes': "0",
            'ruta_mas_usada': "N/A",
            'ciclistas_completados': "0",
            'nodo_mas_activo': "N/A",
            'atributos_disponibles': "0",
            'peso_compuesto': "Simple",
            'perfiles_disponibles': "0",
            'matriz_rutas': "No"
        }
        
        for key, valor in valores_por_defecto.items():
            if key in self.stats_labels:
                self.stats_labels[key].config(text=valor)
    
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
