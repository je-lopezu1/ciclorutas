"""
Utilidades para manejo de grafos NetworkX.

Este módulo contiene funciones auxiliares para trabajar con grafos
en el contexto de la simulación de ciclorutas.
"""

import networkx as nx
import numpy as np
import math
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd


class GrafoUtils:
    """Utilidades para manejo de grafos"""
    
    @staticmethod
    def validar_grafo(grafo: nx.Graph) -> bool:
        """Valida que el grafo sea adecuado para la simulación"""
        if not grafo or len(grafo.nodes()) < 2:
            return False
        
        # Verificar que hay al menos algunos arcos
        if len(grafo.edges()) == 0:
            return False
        
        # Verificar que todos los arcos tienen peso
        for edge in grafo.edges(data=True):
            if 'weight' not in edge[2] or edge[2]['weight'] <= 0:
                print(f"⚠️ Advertencia: Arco {edge[0]}-{edge[1]} no tiene peso válido")
                return False
        
        return True
    
    @staticmethod
    def calcular_posiciones_grafo(grafo: nx.Graph, seed: int = 42) -> Dict:
        """Calcula posiciones para visualización del grafo
        
        Si el grafo tiene coordenadas LAT/LON en los nodos, las usa directamente
        para organizar espacialmente los nodos respetando su ubicación geográfica.
        Si no hay coordenadas, usa un layout automático (spring_layout).
        
        Args:
            grafo: Grafo NetworkX con posibles atributos 'lat' y 'lon' en los nodos
            seed: Semilla para layouts aleatorios (solo si no hay coordenadas)
            
        Returns:
            Diccionario con posiciones (x, y) para cada nodo
        """
        # Verificar si hay coordenadas geográficas en los nodos
        nodos_con_coordenadas = []
        nodos_sin_coordenadas = []
        lats = []
        lons = []
        
        for nodo in grafo.nodes():
            if 'lat' in grafo.nodes[nodo] and 'lon' in grafo.nodes[nodo]:
                try:
                    lat = float(grafo.nodes[nodo]['lat'])
                    lon = float(grafo.nodes[nodo]['lon'])
                    nodos_con_coordenadas.append(nodo)
                    lats.append(lat)
                    lons.append(lon)
                except (ValueError, TypeError):
                    nodos_sin_coordenadas.append(nodo)
            else:
                nodos_sin_coordenadas.append(nodo)
        
        # Requerir que TODOS los nodos tengan coordenadas para usar organización geográfica
        if len(nodos_con_coordenadas) == len(grafo.nodes()):
            print(f"📍 Usando coordenadas geográficas para TODOS los nodos ({len(nodos_con_coordenadas)} nodos)")
            
            # Calcular rangos de coordenadas
            min_lat, max_lat = min(lats), max(lats)
            min_lon, max_lon = min(lons), max(lons)
            
            # Determinar si son coordenadas geográficas (grados) o UTM/metros
            es_geografico = (abs(min_lat) < 1000 and abs(max_lat) < 1000 and 
                           abs(min_lon) < 1000 and abs(max_lon) < 1000)
            
            pos = {}
            for nodo in grafo.nodes():
                # Todos los nodos tienen coordenadas (ya validado arriba)
                lat = float(grafo.nodes[nodo]['lat'])
                lon = float(grafo.nodes[nodo]['lon'])
                
                if es_geografico:
                    # Coordenadas geográficas: mapear al espacio de visualización
                    # RESPETANDO ORIENTACIÓN ESPACIAL REAL:
                    # - LAT (latitud) → Y (eje vertical) → Norte-Sur
                    #   * Valores mayores de LAT = más al norte = más arriba en pantalla
                    #   * Valores menores de LAT = más al sur = más abajo en pantalla
                    # - LON (longitud) → X (eje horizontal) → Este-Oeste  
                    #   * Valores mayores de LON = más al este = más a la derecha en pantalla
                    #   * Valores menores de LON = más al oeste = más a la izquierda en pantalla
                    # Esto garantiza que los nodos y arcos respeten las direcciones geográficas reales
                    
                    # Calcular rangos
                    rango_lat = max_lat - min_lat if max_lat - min_lat > 0 else 1.0
                    rango_lon = max_lon - min_lon if max_lon - min_lon > 0 else 1.0
                    
                    # Convertir coordenadas geográficas a metros (aproximación)
                    # 1 grado de latitud ≈ 111,000 metros (constante en todo el mundo)
                    # 1 grado de longitud ≈ 111,000 * cos(latitud_promedio) metros (varía con latitud)
                    lat_promedio = (min_lat + max_lat) / 2.0
                    metros_por_grado_lat = 111000.0
                    metros_por_grado_lon = 111000.0 * abs(math.cos(math.radians(lat_promedio)))
                    
                    # Convertir a metros relativos al punto mínimo (suroeste)
                    # Esto mantiene las proporciones espaciales reales
                    x_metros = (lon - min_lon) * metros_por_grado_lon  # Este-Oeste: mayor LON = mayor X
                    y_metros = (lat - min_lat) * metros_por_grado_lat  # Norte-Sur: mayor LAT = mayor Y
                    
                    # Usar las coordenadas en metros directamente
                    # El punto (0,0) corresponde al nodo más al sur y más al oeste
                    # Los arcos se dibujarán como líneas rectas respetando estas posiciones espaciales
                    x = x_metros
                    y = y_metros
                    
                else:
                    # Coordenadas ya en metros/UTM: usar directamente
                    x = lon
                    y = lat
                
                pos[nodo] = (x, y)
            
            print(f"   Rango LAT: {min_lat:.6f} a {max_lat:.6f}")
            print(f"   Rango LON: {min_lon:.6f} a {max_lon:.6f}")
            print(f"   ✓ Organización espacial: respetando ubicación geográfica")
            print(f"   ✓ Orientación: Norte↑ Sur↓ Este→ Oeste←")
            print(f"   ✓ Los arcos respetan las direcciones geográficas reales")
            
            return pos
        else:
            # No todos los nodos tienen coordenadas: usar layout automático y advertir
            total_nodos = len(grafo.nodes())
            nodos_con_coords = len(nodos_con_coordenadas)
            nodos_faltantes = len(nodos_sin_coordenadas)
            
            print(f"⚠️ ADVERTENCIA: No todos los nodos tienen coordenadas geográficas")
            print(f"   • Nodos con coordenadas: {nodos_con_coords}/{total_nodos}")
            print(f"   • Nodos sin coordenadas: {nodos_faltantes}")
            if nodos_sin_coordenadas:
                print(f"   • Nodos faltantes: {', '.join(map(str, nodos_sin_coordenadas[:10]))}")
                if len(nodos_sin_coordenadas) > 10:
                    print(f"     ... y {len(nodos_sin_coordenadas) - 10} más")
            print(f"   • Usando layout automático (spring_layout)")
            print(f"   💡 Para usar organización geográfica, TODOS los nodos deben tener columnas LAT y LON")
            
            return nx.spring_layout(grafo, seed=seed, k=2, iterations=50)
    
    @staticmethod
    def obtener_coordenada_nodo(pos_grafo: Dict, nodo_id: str) -> Tuple[float, float]:
        """Obtiene las coordenadas reales del nodo en el grafo"""
        if pos_grafo and nodo_id in pos_grafo:
            coords = pos_grafo[nodo_id]
            # Asegurar que sea una tupla de floats
            if hasattr(coords, '__iter__') and len(coords) == 2:
                return (float(coords[0]), float(coords[1]))
            else:
                return (0.0, 0.0)
        return (0.0, 0.0)  # Fallback
    
    @staticmethod
    def obtener_distancia_arco(grafo: nx.Graph, origen: str, destino: str) -> float:
        """Obtiene la distancia real del arco entre dos nodos para simulación"""
        if not grafo:
            return 50.0  # Distancia por defecto
        
        try:
            if grafo.has_edge(origen, destino):
                # SIEMPRE priorizar distancia_real para simulación (tiempos realistas)
                if 'distancia_real' in grafo[origen][destino]:
                    return grafo[origen][destino]['distancia_real']
                
                # Fallback: usar distancia original si no hay distancia_real
                elif 'distancia' in grafo[origen][destino]:
                    return grafo[origen][destino]['distancia']
                
                # Fallback: usar weight si es una distancia real (no normalizada)
                else:
                    peso = grafo[origen][destino].get('weight', 50.0)
                    if peso >= 10.0:  # Es distancia real directa
                        return peso
                    else:  # Es peso compuesto normalizado, convertir a distancia real
                        # Convertir peso compuesto (0-1) a distancia real (20-200m)
                        return 20 + (1 - peso) * 180
            else:
                # Si no hay arco directo, calcular distancia euclidiana
                pos_origen = grafo.nodes[origen].get('pos', (0, 0))
                pos_destino = grafo.nodes[destino].get('pos', (0, 0))
                return np.sqrt((pos_destino[0] - pos_origen[0])**2 + (pos_destino[1] - pos_origen[1])**2)
        except Exception:
            return 50.0  # Fallback
    
    @staticmethod
    def obtener_atributos_arco(grafo: nx.Graph, origen: str, destino: str) -> dict:
        """Obtiene todos los atributos del arco entre dos nodos"""
        if not grafo or not grafo.has_edge(origen, destino):
            return {}
        
        try:
            return dict(grafo[origen][destino])
        except Exception:
            return {}
    
    @staticmethod
    def calcular_velocidad_ajustada(velocidad_base: float, atributos_arco: dict, 
                                   velocidad_min_config: float = None, 
                                   velocidad_max_config: float = None) -> float:
        """Calcula la velocidad ajustada por inclinación
        
        NOTA: La inclinación NO afecta la decisión de ruta, solo la velocidad de movimiento.
        La decisión de ruta se basa únicamente en distancia, seguridad y luminosidad.
        
        Args:
            velocidad_base: Velocidad base del ciclista (m/s)
            atributos_arco: Atributos del arco (solo inclinación afecta velocidad)
            velocidad_min_config: Velocidad mínima configurada (m/s)
            velocidad_max_config: Velocidad máxima configurada (m/s)
        
        Returns:
            Velocidad ajustada por inclinación:
            - Inclinación positiva (subida): reduce velocidad
            - Inclinación negativa (bajada): aumenta velocidad
        """
        if not atributos_arco:
            return velocidad_base
        
        # Solo la inclinación afecta la velocidad
        factor_inclinacion = 1.0
        
        # Ajuste por inclinación: maneja valores positivos y negativos
        if 'inclinacion' in atributos_arco:
            inclinacion = float(atributos_arco['inclinacion'])  # Convertir a float para decimales
            
            # Inclinación positiva (subida): reduce velocidad
            # Inclinación negativa (bajada): aumenta velocidad
            if inclinacion > 0:
                # Subida: reducir velocidad (máximo 50% de reducción)
                porcentaje_reduccion = min(50, abs(inclinacion))
                factor_inclinacion = 1.0 - (porcentaje_reduccion / 100.0)
            elif inclinacion < 0:
                # Bajada: aumentar velocidad (máximo 30% de aumento)
                porcentaje_aumento = min(30, abs(inclinacion))
                factor_inclinacion = 1.0 + (porcentaje_aumento / 100.0)
            else:
                # Inclinación = 0: velocidad normal
                factor_inclinacion = 1.0
        
        # Aplicar el factor de inclinación
        velocidad_ajustada = velocidad_base * factor_inclinacion
        
        # Limitar la velocidad ajustada respetando la configuración del usuario
        if velocidad_min_config is not None and velocidad_max_config is not None:
            # Usar límites de configuración si están disponibles
            return max(velocidad_min_config, min(velocidad_max_config, velocidad_ajustada))
        else:
            # Fallback: usar límites relativos a la velocidad base
            return max(velocidad_base * 0.3, min(velocidad_base * 1.0, velocidad_ajustada))
    
    @staticmethod
    def calcular_factor_tiempo_desplazamiento(atributos_arco: dict) -> float:
        """Calcula el factor de tiempo de desplazamiento basado en seguridad e iluminación
        
        Args:
            atributos_arco: Atributos del arco (seguridad, luminosidad)
        
        Returns:
            Factor multiplicador para el tiempo de desplazamiento (>1 = más lento, <1 = más rápido)
        """
        if not atributos_arco:
            return 1.0
        
        # Factores de ajuste para tiempo de desplazamiento
        factor_seguridad = 1.0
        factor_luminosidad = 1.0
        
        # Ajuste por seguridad (valores más bajos = menos confianza = más tiempo)
        if 'seguridad' in atributos_arco:
            seguridad = atributos_arco['seguridad']
            # Seguridad 5-9, factor 1.3-0.8 (menos seguridad = más tiempo)
            factor_seguridad = 1.3 - (seguridad - 5) * 0.125
        
        # Ajuste por luminosidad (valores más bajos = menos visibilidad = más tiempo)
        if 'luminosidad' in atributos_arco:
            luminosidad = atributos_arco['luminosidad']
            # Luminosidad 4-8, factor 1.2-0.9 (menos luminosidad = más tiempo)
            factor_luminosidad = 1.2 - (luminosidad - 4) * 0.075
        
        # Aplicar ambos factores (multiplicativo)
        factor_tiempo = factor_seguridad * factor_luminosidad
        
        # Limitar el factor entre 0.5 y 2.0 (máximo 50% más rápido o 100% más lento)
        return max(0.5, min(2.0, factor_tiempo))
    
    @staticmethod
    def precalcular_rangos_atributos(grafo: nx.Graph) -> Dict[str, Tuple[float, float]]:
        """Pre-calcula los rangos de atributos del grafo completo"""
        rangos_atributos = {}
        atributos_valores = {}
        
        # Recopilar todos los valores una sola vez
        for edge in grafo.edges(data=True):
            for attr, valor in edge[2].items():
                if isinstance(valor, (int, float)):
                    if attr not in atributos_valores:
                        atributos_valores[attr] = []
                    atributos_valores[attr].append(valor)
            
            # También incluir 'weight' como 'distancia' si no hay atributo 'distancia' explícito
            if 'weight' in edge[2] and 'distancia' not in edge[2]:
                if 'distancia' not in atributos_valores:
                    atributos_valores['distancia'] = []
                atributos_valores['distancia'].append(edge[2]['weight'])
        
        # Calcular rangos una sola vez
        for attr, valores in atributos_valores.items():
            if valores:
                rangos_atributos[attr] = (min(valores), max(valores))
        
        return rangos_atributos
    
    @staticmethod
    def calcular_peso_compuesto_perfil(atributos_arco: dict, perfil_ciclista: dict, 
                                     rangos_atributos: Dict[str, Tuple[float, float]]) -> float:
        """Calcula peso compuesto dinámicamente usando los pesos del perfil del ciclista"""
        peso = 0.0
        
        for attr, valor in atributos_arco.items():
            # Solo procesar atributos que están en el perfil del ciclista
            if attr in perfil_ciclista['pesos'] and attr in rangos_atributos:
                min_val, max_val = rangos_atributos[attr]
                
                if max_val > min_val and isinstance(valor, (int, float)):
                    # Normalización genérica: asumir que valores más altos = mejor
                    # Si un atributo debe invertirse (mayor = peor), se hace externamente
                    norm_val = (valor - min_val) / (max_val - min_val)
                    
                    # Detectar si el atributo debe invertirse basándose en su nombre
                    # Atributos que típicamente son "más alto = peor" (como distancia, inclinacion)
                    atributos_invertidos = ['distancia', 'inclinacion', 'tiempo', 'coste', 'peso']
                    if any(inv in attr.lower() for inv in atributos_invertidos):
                        norm_val = 1 - norm_val
                    
                    # Aplicar peso del perfil del ciclista
                    peso += norm_val * perfil_ciclista['pesos'][attr]
        
        return peso
    
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
    def crear_grafo_desde_excel(archivo_excel: str) -> Tuple[nx.Graph, Dict, Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """Crea un grafo NetworkX desde un archivo Excel"""
        # Leer datos del Excel
        nodos_df = pd.read_excel(archivo_excel, sheet_name="NODOS", engine="openpyxl")
        arcos_df = pd.read_excel(archivo_excel, sheet_name="ARCOS", engine="openpyxl")
        
        # Verificar si hay hojas adicionales
        excel_file = pd.ExcelFile(archivo_excel)
        perfiles_df = None
        rutas_df = None
        
        if "PERFILES" in excel_file.sheet_names:
            perfiles_df = pd.read_excel(archivo_excel, sheet_name="PERFILES", engine="openpyxl")
        
        if "RUTAS" in excel_file.sheet_names:
            rutas_df = pd.read_excel(archivo_excel, sheet_name="RUTAS", engine="openpyxl")
        
        # Crear grafo NetworkX
        G = nx.Graph()
        
        # Verificar si hay coordenadas LAT/LON en la hoja NODOS
        tiene_lat_lon = 'LAT' in nodos_df.columns and 'LON' in nodos_df.columns
        coordenadas_nodos = {}
        
        # Agregar nodos y almacenar coordenadas si existen
        columna_nodos = nodos_df.columns[0]  # Primera columna es la de nodos
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
                except (ValueError, KeyError):
                    pass
        
        # Verificar atributos disponibles en arcos
        atributos_disponibles = []
        for attr in ['DISTANCIA', 'SEGURIDAD', 'LUMINOSIDAD', 'INCLINACION']:
            if attr in arcos_df.columns:
                atributos_disponibles.append(attr)
        
        # Si hay coordenadas LAT/LON, calcular distancias euclidianas e ignorar DISTANCIA de ARCOS
        if tiene_lat_lon:
            tiene_distancia_en_arcos = 'DISTANCIA' in atributos_disponibles
            if tiene_distancia_en_arcos:
                # Eliminar la columna DISTANCIA del DataFrame para que no se use
                if 'DISTANCIA' in arcos_df.columns:
                    arcos_df = arcos_df.drop(columns=['DISTANCIA'])
                    atributos_disponibles.remove('DISTANCIA')
            
            # Calcular distancias euclidianas desde coordenadas
            col_origen = arcos_df.columns[0]
            col_destino = arcos_df.columns[1]
            distancias_calculadas = []
            
            for _, fila in arcos_df.iterrows():
                origen = fila[col_origen]
                destino = fila[col_destino]
                
                if origen in coordenadas_nodos and destino in coordenadas_nodos:
                    lat1, lon1 = coordenadas_nodos[origen]
                    lat2, lon2 = coordenadas_nodos[destino]
                    distancia = GrafoUtils._calcular_distancia_euclidiana(lat1, lon1, lat2, lon2)
                    distancias_calculadas.append(distancia)
                else:
                    distancias_calculadas.append(100.0)  # Distancia por defecto
            
            # Reemplazar/Agregar columna DISTANCIA con valores calculados
            arcos_df['DISTANCIA'] = distancias_calculadas
            if 'DISTANCIA' not in atributos_disponibles:
                atributos_disponibles.append('DISTANCIA')
        
        # Agregar arcos con todos los atributos
        for _, fila in arcos_df.iterrows():
            origen, destino = fila[0], fila[1]
            
            # Crear diccionario de atributos
            atributos = {}
            for col in arcos_df.columns:
                if col not in ['ORIGEN', 'DESTINO']:
                    atributos[col.lower()] = fila[col]
            
            # Configurar pesos para diferentes usos
            if 'distancia' in atributos:
                atributos['weight'] = atributos['distancia']
            
            # Asegurar que siempre tengamos distancia_real para simulación
            if 'distancia_real' not in atributos and 'distancia' in atributos:
                atributos['distancia_real'] = atributos['distancia']
            
            G.add_edge(origen, destino, **atributos)
        
        # Calcular posiciones del grafo
        pos = GrafoUtils.calcular_posiciones_grafo(G)
        
        return G, pos, perfiles_df, rutas_df
    
    @staticmethod
    def obtener_ruta_optima(grafo: nx.Graph, origen: str, destino: str, 
                          perfil_ciclista: dict, rangos_atributos: Dict) -> Optional[List[str]]:
        """Obtiene la ruta óptima para un perfil de ciclista específico"""
        try:
            # Crear grafo temporal con pesos ajustados al perfil
            grafo_temp = grafo.copy()
            
            # Recalcular pesos basados en el perfil
            for edge in grafo_temp.edges(data=True):
                origen_edge, destino_edge, datos = edge
                atributos_arco = {k: v for k, v in datos.items() if k not in ['weight', 'distancia_real']}
                
                nuevo_peso = GrafoUtils.calcular_peso_compuesto_perfil(
                    atributos_arco, perfil_ciclista, rangos_atributos
                )
                grafo_temp[origen_edge][destino_edge]['weight'] = nuevo_peso
            
            # Encontrar ruta óptima
            return nx.shortest_path(grafo_temp, origen, destino, weight='weight')
            
        except nx.NetworkXNoPath:
            return None
        except Exception:
            return None
