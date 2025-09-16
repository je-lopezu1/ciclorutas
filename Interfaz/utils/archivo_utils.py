"""
Utilidades para manejo de archivos en la interfaz.

Este módulo contiene funciones para cargar, validar y procesar
archivos Excel con datos de grafos de ciclorutas.
"""

import pandas as pd
import networkx as nx
import os
from typing import Dict, List, Tuple, Optional, Any
from tkinter import filedialog, messagebox


class ArchivoUtils:
    """Utilidades para manejo de archivos Excel"""
    
    # Configuración de hojas esperadas
    HOJAS_ESPERADAS = {
        'NODOS': ['NODO', 'ID', 'NOMBRE'],
        'ARCOS': ['ORIGEN', 'DESTINO', 'DISTANCIA'],
        'PERFILES': ['PERFILES', 'DISTANCIA', 'SEGURIDAD', 'LUMINOSIDAD', 'INCLINACION'],
        'RUTAS': ['NODO']  # Las demás columnas son nodos de destino
    }
    
    # Atributos opcionales para arcos
    ATRIBUTOS_OPCIONALES = ['SEGURIDAD', 'LUMINOSIDAD', 'INCLINACION', 'PESO_COMPUESTO']
    
    @staticmethod
    def seleccionar_archivo_excel() -> Optional[str]:
        """Abre un diálogo para seleccionar archivo Excel"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de grafo",
            filetypes=[("Excel files", "*.xlsx"), ("Excel files", "*.xls")]
        )
        return archivo if archivo else None
    
    @staticmethod
    def validar_archivo_excel(archivo: str) -> Tuple[bool, str]:
        """Valida que el archivo Excel tenga la estructura correcta"""
        try:
            # Verificar que el archivo existe
            if not os.path.exists(archivo):
                return False, "El archivo no existe"
            
            # Leer el archivo Excel
            excel_file = pd.ExcelFile(archivo)
            hojas_disponibles = excel_file.sheet_names
            
            # Verificar hojas obligatorias
            hojas_obligatorias = ['NODOS', 'ARCOS']
            hojas_faltantes = [hoja for hoja in hojas_obligatorias if hoja not in hojas_disponibles]
            
            if hojas_faltantes:
                return False, f"Faltan las hojas obligatorias: {', '.join(hojas_faltantes)}"
            
            # Validar estructura de cada hoja
            for hoja in hojas_obligatorias:
                df = pd.read_excel(archivo, sheet_name=hoja, engine="openpyxl")
                columnas_esperadas = ArchivoUtils.HOJAS_ESPERADAS[hoja]
                
                # Verificar que al menos una columna esperada esté presente
                columnas_presentes = [col for col in columnas_esperadas if col in df.columns]
                if not columnas_presentes:
                    return False, f"La hoja '{hoja}' no tiene las columnas esperadas: {', '.join(columnas_esperadas)}"
            
            return True, "Archivo válido"
            
        except Exception as e:
            return False, f"Error al validar el archivo: {str(e)}"
    
    @staticmethod
    def cargar_datos_desde_excel(archivo: str) -> Tuple[Optional[nx.Graph], Optional[Dict], 
                                                       Optional[pd.DataFrame], Optional[pd.DataFrame], str]:
        """Carga datos desde archivo Excel y crea el grafo"""
        try:
            # Validar archivo primero
            es_valido, mensaje = ArchivoUtils.validar_archivo_excel(archivo)
            if not es_valido:
                return None, None, None, None, mensaje
            
            # Leer datos del Excel
            nodos_df = pd.read_excel(archivo, sheet_name="NODOS", engine="openpyxl")
            arcos_df = pd.read_excel(archivo, sheet_name="ARCOS", engine="openpyxl")
            
            # Verificar si hay hojas adicionales
            excel_file = pd.ExcelFile(archivo)
            perfiles_df = None
            rutas_df = None
            
            if "PERFILES" in excel_file.sheet_names:
                perfiles_df = pd.read_excel(archivo, sheet_name="PERFILES", engine="openpyxl")
                print("✅ Hoja PERFILES encontrada")
            
            if "RUTAS" in excel_file.sheet_names:
                rutas_df = pd.read_excel(archivo, sheet_name="RUTAS", engine="openpyxl")
                print("✅ Hoja RUTAS encontrada")
            
            # Crear grafo NetworkX
            G = nx.Graph()
            
            # Agregar nodos
            columna_nodos = ArchivoUtils._encontrar_columna_nodos(nodos_df)
            for nodo in nodos_df[columna_nodos]:
                G.add_node(nodo)
                print(f"✅ Nodo agregado: {nodo}")
            
            # Verificar atributos disponibles en arcos
            atributos_disponibles = ArchivoUtils._verificar_atributos_arcos(arcos_df)
            print(f"📊 Atributos encontrados: {atributos_disponibles}")
            
            # Preparar datos para cálculo dinámico de pesos
            if len(atributos_disponibles) > 1:
                arcos_df = ArchivoUtils._calcular_peso_compuesto(arcos_df, atributos_disponibles)
                print("✅ Datos preparados para cálculo dinámico de pesos")
            
            # Agregar arcos con todos los atributos
            col_origen, col_destino = ArchivoUtils._encontrar_columnas_arco(arcos_df)
            
            for _, fila in arcos_df.iterrows():
                origen, destino = fila[col_origen], fila[col_destino]
                
                # Crear diccionario de atributos
                atributos = {}
                for col in arcos_df.columns:
                    if col not in [col_origen, col_destino]:
                        atributos[col.lower()] = fila[col]
                
                # Configurar pesos para diferentes usos:
                # - weight: para algoritmos de pathfinding (se calculará dinámicamente por usuario)
                # - distancia_real: para simulación de tiempos (distancia real ajustada)
                if 'distancia' in atributos:
                    atributos['weight'] = atributos['distancia']  # Usar distancia como peso base
                
                # Asegurar que siempre tengamos distancia_real para simulación
                if 'distancia_real' not in atributos and 'distancia' in atributos:
                    atributos['distancia_real'] = atributos['distancia']
                
                G.add_edge(origen, destino, **atributos)
                
                # Mostrar información del arco
                info_arco = f"{origen} -> {destino}"
                if 'distancia' in atributos:
                    info_arco += f" (dist: {atributos['distancia']:.0f})"
                if 'peso_compuesto' in atributos:
                    info_arco += f" (peso: {atributos['peso_compuesto']:.3f})"
                print(f"✅ Arco agregado: {info_arco}")
            
            # Verificar que el grafo tenga al menos 3 nodos
            if len(G.nodes()) < 3:
                return None, None, None, None, "El grafo debe tener al menos 3 nodos para la simulación"
            
            # Calcular posiciones del grafo
            pos = nx.spring_layout(G, seed=42, k=2, iterations=50)
            
            return G, pos, perfiles_df, rutas_df, "Archivo cargado exitosamente"
            
        except Exception as e:
            return None, None, None, None, f"Error al cargar el archivo: {str(e)}"
    
    @staticmethod
    def _encontrar_columna_nodos(nodos_df: pd.DataFrame) -> str:
        """Encuentra la columna correcta para los nodos"""
        for col in ArchivoUtils.HOJAS_ESPERADAS['NODOS']:
            if col in nodos_df.columns:
                return col
        return nodos_df.columns[0]  # Fallback a la primera columna
    
    @staticmethod
    def _encontrar_columnas_arco(arcos_df: pd.DataFrame) -> Tuple[str, str]:
        """Encuentra las columnas correctas para origen y destino"""
        columnas_esperadas = ArchivoUtils.HOJAS_ESPERADAS['ARCOS']
        
        origen = None
        destino = None
        
        for col in columnas_esperadas:
            if col in arcos_df.columns:
                if origen is None:
                    origen = col
                elif destino is None:
                    destino = col
                    break
        
        if origen is None or destino is None:
            # Fallback a las primeras dos columnas
            return arcos_df.columns[0], arcos_df.columns[1]
        
        return origen, destino
    
    @staticmethod
    def _verificar_atributos_arcos(arcos_df: pd.DataFrame) -> List[str]:
        """Verifica qué atributos están disponibles en los arcos"""
        atributos_encontrados = []
        for attr in ArchivoUtils.ATRIBUTOS_OPCIONALES:
            if attr in arcos_df.columns:
                atributos_encontrados.append(attr)
        return atributos_encontrados
    
    @staticmethod
    def obtener_informacion_archivo(archivo: str) -> Dict[str, Any]:
        """Obtiene información detallada del archivo Excel"""
        try:
            excel_file = pd.ExcelFile(archivo)
            hojas_disponibles = excel_file.sheet_names
            
            info = {
                'nombre_archivo': os.path.basename(archivo),
                'ruta_completa': archivo,
                'hojas_disponibles': hojas_disponibles,
                'tamaño_archivo': os.path.getsize(archivo),
                'hojas_validas': []
            }
            
            # Validar cada hoja
            for hoja in hojas_disponibles:
                try:
                    df = pd.read_excel(archivo, sheet_name=hoja, engine="openpyxl")
                    info['hojas_validas'].append({
                        'nombre': hoja,
                        'filas': len(df),
                        'columnas': len(df.columns),
                        'columnas_nombres': list(df.columns)
                    })
                except Exception as e:
                    info['hojas_validas'].append({
                        'nombre': hoja,
                        'error': str(e)
                    })
            
            return info
            
        except Exception as e:
            return {
                'error': f"Error al obtener información del archivo: {str(e)}"
            }
    
    @staticmethod
    def mostrar_dialogo_carga_exitosa(archivo: str, grafo: nx.Graph, 
                                    perfiles_df: Optional[pd.DataFrame] = None,
                                    rutas_df: Optional[pd.DataFrame] = None):
        """Muestra un diálogo con información de carga exitosa"""
        num_nodos = len(grafo.nodes())
        num_arcos = len(grafo.edges())
        
        # Obtener atributos disponibles
        atributos_encontrados = set()
        for edge in grafo.edges(data=True):
            for key in edge[2].keys():
                if key not in ['weight']:
                    atributos_encontrados.add(key)
        
        mensaje = f"✅ Grafo cargado exitosamente!\n\n📊 Estadísticas:\n• Nodos: {num_nodos}\n• Arcos: {num_arcos}\n• Atributos: {len(atributos_encontrados)}"
        
        if len(atributos_encontrados) > 1:
            mensaje += f"\n• Peso compuesto: ✅"
        else:
            mensaje += f"\n• Peso compuesto: ❌ (solo distancia)"
        
        if perfiles_df is not None:
            mensaje += f"\n• Perfiles: {len(perfiles_df)} disponibles"
        
        if rutas_df is not None:
            mensaje += f"\n• Matriz de rutas: ✅"
        
        if perfiles_df is not None and rutas_df is not None:
            mensaje += f"\n\n🎭 SISTEMA AVANZADO ACTIVADO:"
            mensaje += f"\n• Perfiles de ciclistas: {len(perfiles_df)} tipos"
            mensaje += f"\n• Rutas probabilísticas: ✅"
            mensaje += f"\n• Simulación realista: ✅"
        else:
            mensaje += f"\n\n🚴 La simulación ahora usa pesos mejorados"
        
        messagebox.showinfo("Grafo Cargado", mensaje)
    
    @staticmethod
    def mostrar_dialogo_error_carga(error: str):
        """Muestra un diálogo de error de carga"""
        messagebox.showerror("Error de Carga", f"No se pudo cargar el archivo:\n\n{error}")
    
    @staticmethod
    def exportar_estadisticas_simulacion(estadisticas: Dict[str, Any], archivo: str):
        """Exporta estadísticas de simulación a un archivo Excel"""
        try:
            with pd.ExcelWriter(archivo, engine='openpyxl') as writer:
                # Hoja de estadísticas generales
                stats_generales = {
                    'Métrica': ['Total Ciclistas', 'Ciclistas Activos', 'Ciclistas Completados',
                               'Velocidad Promedio', 'Velocidad Mínima', 'Velocidad Máxima',
                               'Duración Simulación', 'Rutas Utilizadas', 'Total Viajes'],
                    'Valor': [
                        estadisticas.get('total_ciclistas', 0),
                        estadisticas.get('ciclistas_activos', 0),
                        estadisticas.get('ciclistas_completados', 0),
                        f"{estadisticas.get('velocidad_promedio', 0):.2f} m/s",
                        f"{estadisticas.get('velocidad_minima', 0):.2f} m/s",
                        f"{estadisticas.get('velocidad_maxima', 0):.2f} m/s",
                        f"{estadisticas.get('duracion_simulacion', 0):.0f} s",
                        estadisticas.get('rutas_utilizadas', 0),
                        estadisticas.get('total_viajes', 0)
                    ]
                }
                pd.DataFrame(stats_generales).to_excel(writer, sheet_name='Estadísticas Generales', index=False)
                
                # Hoja de rutas más utilizadas
                if 'rutas_por_frecuencia' in estadisticas:
                    rutas_df = pd.DataFrame(estadisticas['rutas_por_frecuencia'], 
                                          columns=['Ruta', 'Frecuencia'])
                    rutas_df.to_excel(writer, sheet_name='Rutas Más Utilizadas', index=False)
                
                # Hoja de ciclistas por nodo
                if 'ciclistas_por_nodo' in estadisticas:
                    nodos_df = pd.DataFrame(list(estadisticas['ciclistas_por_nodo'].items()),
                                          columns=['Nodo', 'Ciclistas'])
                    nodos_df.to_excel(writer, sheet_name='Ciclistas por Nodo', index=False)
            
            return True, "Estadísticas exportadas exitosamente"
            
        except Exception as e:
            return False, f"Error al exportar estadísticas: {str(e)}"
    
    @staticmethod
    def _calcular_peso_compuesto(arcos_df: pd.DataFrame, atributos_disponibles: List[str]) -> pd.DataFrame:
        """Prepara los datos para cálculo dinámico de pesos compuestos por usuario"""
        df_resultado = arcos_df.copy()
        
        # NO calcular peso compuesto fijo aquí - se hará dinámicamente por usuario
        # Solo calcular distancia real para simulación
        df_resultado['distancia_real'] = ArchivoUtils._calcular_distancia_real(arcos_df, atributos_disponibles)
        
        print(f"📏 Distancia real calculada:")
        print(f"   Rango: {df_resultado['distancia_real'].min():.1f} - {df_resultado['distancia_real'].max():.1f} metros")
        print(f"   Promedio: {df_resultado['distancia_real'].mean():.1f} metros")
        print(f"ℹ️ Los pesos compuestos se calcularán dinámicamente por perfil de usuario")
        
        return df_resultado
    
    @staticmethod
    def _calcular_distancia_real(arcos_df: pd.DataFrame, atributos_disponibles: List[str]) -> pd.Series:
        """Calcula la distancia real igual a la distancia original (sin ajustes)"""
        # La distancia real es igual a la distancia original
        distancias_reales = arcos_df['DISTANCIA'].copy()
        
        print(f"📏 Distancia real = Distancia original (sin ajustes)")
        print(f"   Rango: {distancias_reales.min():.1f} - {distancias_reales.max():.1f} metros")
        print(f"   Promedio: {distancias_reales.mean():.1f} metros")
        print(f"ℹ️ Los otros atributos afectarán la velocidad, no la distancia")
        
        return distancias_reales
