"""
Utilidades para manejo de archivos en la interfaz.

Este módulo contiene funciones para cargar, validar y procesar
archivos Excel con datos de grafos de ciclorutas.
"""

import pandas as pd
import networkx as nx
import os
import math
from typing import Dict, List, Tuple, Optional, Any
from tkinter import filedialog, messagebox


class ArchivoUtils:
    """Utilidades para manejo de archivos Excel"""
    
    # Configuración de hojas esperadas
    HOJAS_ESPERADAS = {
        'NODOS': ['NODO', 'ID', 'NOMBRE'],
        'ARCOS': ['ORIGEN', 'DESTINO', 'DISTANCIA', 'INCLINACION'],  # Obligatorias
        'PERFILES': ['PERFILES', 'PROBABILIDAD'],  # PERFILES y PROBABILIDAD son obligatorias
        'RUTAS': ['NODO']  # Las demás columnas son nodos de destino
    }
    
    # Atributos obligatorios en ARCOS
    ATRIBUTOS_OBLIGATORIOS_ARCOS = ['ORIGEN', 'DESTINO', 'DISTANCIA', 'INCLINACION']
    
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
            
            # Validar estructura de cada hoja obligatoria
            for hoja in hojas_obligatorias:
                df = pd.read_excel(archivo, sheet_name=hoja, engine="openpyxl")
                columnas_esperadas = ArchivoUtils.HOJAS_ESPERADAS[hoja]
                
                # Verificar que al menos una columna esperada esté presente
                columnas_presentes = [col for col in columnas_esperadas if col in df.columns]
                if not columnas_presentes:
                    return False, f"La hoja '{hoja}' no tiene las columnas esperadas: {', '.join(columnas_esperadas)}"
            
            # Validar hoja PERFILES si existe (debe tener PERFILES y PROBABILIDAD)
            if "PERFILES" in hojas_disponibles:
                df_perfiles = pd.read_excel(archivo, sheet_name="PERFILES", engine="openpyxl")
                columnas_perfiles_obligatorias = ['PERFILES', 'PROBABILIDAD']
                columnas_faltantes = [col for col in columnas_perfiles_obligatorias if col not in df_perfiles.columns]
                
                if columnas_faltantes:
                    return False, f"La hoja PERFILES debe tener las columnas obligatorias: {', '.join(columnas_faltantes)}"
                
                # Validar que las probabilidades sumen 1.0
                try:
                    probabilidades = df_perfiles['PROBABILIDAD'].values
                    suma_probabilidades = sum(probabilidades)
                    if abs(suma_probabilidades - 1.0) > 0.01:
                        return False, f"Las probabilidades en PERFILES suman {suma_probabilidades:.4f}, deben sumar 1.0"
                except Exception:
                    return False, "Error al validar probabilidades en PERFILES"
            
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
            
            # Verificar si hay coordenadas LAT/LON en la hoja NODOS
            tiene_lat_lon = 'LAT' in nodos_df.columns and 'LON' in nodos_df.columns
            coordenadas_nodos = {}
            
            # Agregar nodos y almacenar coordenadas si existen
            columna_nodos = ArchivoUtils._encontrar_columna_nodos(nodos_df)
            for idx, fila in nodos_df.iterrows():
                nodo = fila[columna_nodos]
                G.add_node(nodo)
                
                # Guardar coordenadas si existen
                if tiene_lat_lon:
                    try:
                        lat = float(fila['LAT'])
                        lon = float(fila['LON'])
                        coordenadas_nodos[nodo] = (lat, lon)
                        G.nodes[nodo]['lat'] = lat
                        G.nodes[nodo]['lon'] = lon
                        print(f"✅ Nodo agregado: {nodo} (LAT: {lat:.6f}, LON: {lon:.6f})")
                    except (ValueError, KeyError):
                        print(f"✅ Nodo agregado: {nodo} (sin coordenadas válidas)")
                else:
                    print(f"✅ Nodo agregado: {nodo}")
            
            if tiene_lat_lon:
                print(f"📍 Coordenadas LAT/LON detectadas en {len(coordenadas_nodos)} nodos")
            
            # Verificar atributos disponibles en arcos (dinámicamente)
            atributos_disponibles = ArchivoUtils._verificar_atributos_arcos(arcos_df)
            print(f"📊 Atributos encontrados en ARCOS: {atributos_disponibles}")
            
            # Si hay coordenadas LAT/LON, calcular distancias euclidianas e ignorar DISTANCIA de ARCOS
            if tiene_lat_lon:
                tiene_distancia_en_arcos = 'DISTANCIA' in atributos_disponibles
                if tiene_distancia_en_arcos:
                    print("⚠️ Se detectó columna DISTANCIA en ARCOS, pero será ignorada")
                    print("📐 Usando coordenadas LAT/LON para calcular distancias euclidianas...")
                    # Eliminar la columna DISTANCIA del DataFrame para que no se use
                    if 'DISTANCIA' in arcos_df.columns:
                        arcos_df = arcos_df.drop(columns=['DISTANCIA'])
                        atributos_disponibles.remove('DISTANCIA')
                else:
                    print("📐 Calculando distancias euclidianas desde coordenadas LAT/LON...")
                
                # Calcular distancias euclidianas desde coordenadas
                col_origen, col_destino = ArchivoUtils._encontrar_columnas_arco(arcos_df)
                distancias_calculadas = []
                
                for _, fila in arcos_df.iterrows():
                    origen = fila[col_origen]
                    destino = fila[col_destino]
                    
                    if origen in coordenadas_nodos and destino in coordenadas_nodos:
                        lat1, lon1 = coordenadas_nodos[origen]
                        lat2, lon2 = coordenadas_nodos[destino]
                        distancia = ArchivoUtils._calcular_distancia_euclidiana(lat1, lon1, lat2, lon2)
                        distancias_calculadas.append(distancia)
                    else:
                        # Si faltan coordenadas para algún nodo, usar distancia por defecto
                        distancias_calculadas.append(100.0)  # 100 metros por defecto
                        print(f"⚠️ Nodo {origen if origen not in coordenadas_nodos else destino} sin coordenadas, usando distancia por defecto")
                
                # Reemplazar/Agregar columna DISTANCIA con valores calculados
                arcos_df['DISTANCIA'] = distancias_calculadas
                if 'DISTANCIA' not in atributos_disponibles:
                    atributos_disponibles.append('DISTANCIA')
                print(f"✅ Distancias euclidianas calculadas: {len(distancias_calculadas)} arcos")
                print(f"   Rango: {min(distancias_calculadas):.1f} - {max(distancias_calculadas):.1f} metros")
                print(f"   Promedio: {sum(distancias_calculadas)/len(distancias_calculadas):.1f} metros")
            
            # Preparar datos - calcular distancia real si hay DISTANCIA
            if 'DISTANCIA' in atributos_disponibles:
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
        """Verifica qué atributos están disponibles dinámicamente en los arcos"""
        # Obtener columnas obligatorias (ORIGEN y DESTINO)
        col_origen, col_destino = ArchivoUtils._encontrar_columnas_arco(arcos_df)
        
        # Obtener TODOS los atributos excepto ORIGEN y DESTINO
        atributos_encontrados = []
        for col in arcos_df.columns:
            if col not in [col_origen, col_destino]:
                atributos_encontrados.append(col)
        
        print(f"📋 Atributos dinámicos detectados en ARCOS: {atributos_encontrados}")
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
    def _calcular_distancia_euclidiana(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcula distancia entre dos coordenadas usando fórmula de Haversine
        
        Para coordenadas geográficas (LAT/LON en grados), usa la fórmula de Haversine
        que calcula la distancia real en línea recta sobre la superficie de la Tierra.
        Ideal para distancias urbanas dentro de una ciudad para simular desplazamientos en bicicleta.
        
        Para distancias cortas urbanas (< 10 km), la precisión de Haversine es óptima y proporciona
        una buena aproximación de la distancia real entre nodos de ciclorutas.
        
        Args:
            lat1, lon1: Coordenadas del punto origen (en grados decimales, ej: 4.6097, -74.0817)
            lat2, lon2: Coordenadas del punto destino (en grados decimales)
            
        Returns:
            Distancia en metros (distancia real en línea recta entre los puntos)
        """
        # Detectar si las coordenadas están en grados (valores pequeños) o metros (valores grandes)
        if abs(lat1) < 1000 and abs(lat2) < 1000 and abs(lon1) < 1000 and abs(lon2) < 1000:
            # Coordenadas geográficas en grados - usar FÓRMULA DE HAVERSINE
            # Radio medio de la Tierra en metros (6371 km)
            R = 6371000
            
            # Convertir grados a radianes
            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            delta_lat = math.radians(lat2 - lat1)
            delta_lon = math.radians(lon2 - lon1)
            
            # Fórmula de Haversine para distancia en esfera
            # Calcula la distancia real en línea recta sobre la superficie terrestre
            a = (math.sin(delta_lat / 2) ** 2 + 
                 math.cos(lat1_rad) * math.cos(lat2_rad) * 
                 math.sin(delta_lon / 2) ** 2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distancia = R * c
        else:
            # Coordenadas ya están en metros o UTM - usar euclidiana plana
            distancia = math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
        
        return distancia
    
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
