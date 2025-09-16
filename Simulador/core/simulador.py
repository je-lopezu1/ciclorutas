"""
Motor principal del simulador de ciclorutas.

Este módulo contiene la clase principal SimuladorCiclorutas que orquesta
toda la simulación usando SimPy y NetworkX.
"""

import simpy
import random
import numpy as np
import networkx as nx
import time
from typing import List, Tuple, Dict, Optional, Any

from ..models.ciclista import Ciclista, PoolCiclistas
from ..distributions.distribucion_nodo import DistribucionNodo, GestorDistribuciones
from ..utils.grafo_utils import GrafoUtils
from ..utils.rutas_utils import RutasUtils
from .configuracion import ConfiguracionSimulacion


class SimuladorCiclorutas:
    """Clase principal para manejar la simulación de ciclorutas"""
    
    def __init__(self, config: ConfiguracionSimulacion, grafo_networkx: Optional[nx.Graph] = None):
        self.config = config
        self.env = None
        self.coordenadas = []
        self.rutas = []
        self.colores = []
        self.trayectorias = []
        self.velocidades = []
        self.procesos = []
        self.estado = "detenido"  # detenido, ejecutando, pausado
        self.tiempo_actual = 0
        self.tiempo_total = 0
        
        # Integración con NetworkX
        self.grafo = grafo_networkx
        self.pos_grafo = None
        self.usar_grafo_real = grafo_networkx is not None
        
        # Sistema de distribuciones de probabilidad
        self.gestor_distribuciones = GestorDistribuciones()
        
        # Sistema de colores dinámico basado en nodos
        self.colores_nodos = {}  # Dict[nodo_id, color]
        self.rutas_dinamicas = []  # Lista de rutas calculadas dinámicamente
        
        # Sistema de rastreo de rutas
        self.rutas_utilizadas = {}  # Dict[ruta_str, contador] para contar uso de rutas
        self.rutas_por_ciclista = {}  # Dict[ciclista_id, ruta_info] para rastrear rutas individuales
        
        # Sistema de rastreo de estado de ciclistas
        self.estado_ciclistas = {}  # Dict[ciclista_id, estado] para rastrear si están activos o completados
        self.ciclistas_por_nodo = {}  # Dict[nodo_origen, contador] para contar ciclistas por nodo de origen
        
        # Sistema de perfiles y rutas
        self.perfiles_df = None  # DataFrame con perfiles de ciclistas
        self.rutas_df = None  # DataFrame con matriz de probabilidades de destino
        self.perfiles_ciclistas = {}  # Dict[ciclista_id, perfil] para rastrear perfil de cada ciclista
        
        # Cache de rendimiento
        self.rangos_atributos = {}  # Rangos pre-calculados de atributos
        self.rangos_calculados = False  # Flag para evitar recálculos
        self.grafos_por_perfil = {}  # Cache de grafos optimizados por perfil
        self.grafo_base = None  # Referencia al grafo original
        
        # Cache inteligente de rutas
        self.rutas_por_perfil = {}  # Cache de rutas por perfil
        
        # Pool de objetos para ciclistas
        self.pool_ciclistas = PoolCiclistas(
            tamaño_inicial=100,
            tamaño_maximo=config.max_ciclistas_simultaneos
        )
        
        self.estadisticas_persistentes = {
            'total_ciclistas_creados': 0,
            'total_ciclistas_completados': 0,
            'total_ciclistas_eliminados': 0,
            'total_viajes_completados': 0,
            'total_distancia_recorrida': 0.0
        }
    
    def configurar_grafo(self, grafo: nx.Graph, posiciones: Dict, perfiles_df=None, rutas_df=None):
        """Configura el grafo NetworkX y sus posiciones para la simulación"""
        if not GrafoUtils.validar_grafo(grafo):
            print("⚠️ Advertencia: El grafo no es válido")
            self.usar_grafo_real = False
            return False
            
        self.grafo = grafo
        self.pos_grafo = posiciones
        self.usar_grafo_real = True
        
        # Guardar referencia al grafo base para cache
        self.grafo_base = grafo.copy()
        
        # Configurar perfiles y rutas si están disponibles
        self.perfiles_df = perfiles_df
        self.rutas_df = rutas_df
        
        # Pre-calcular rangos al cargar el grafo
        self._precalcular_rangos_atributos()
        
        # Configurar límites adaptativos
        self._configurar_limites_adaptativos()
        
        # Pre-calcular rutas por perfil si hay perfiles disponibles
        if self.perfiles_df is not None:
            self._precalcular_rutas_por_perfil()
        
        # Limpiar cache de grafos por perfil al cambiar grafo
        self.grafos_por_perfil = {}
        self.rutas_por_perfil = {}
        
        self._inicializar_grafo()
        
        # Inicializar distribuciones por defecto
        self._inicializar_distribuciones_por_defecto()
        
        return True
    
    def _inicializar_distribuciones_por_defecto(self):
        """Inicializa distribuciones por defecto para todos los nodos"""
        if not self.grafo:
            return
        
        nodos = list(self.grafo.nodes())
        if len(nodos) < 2:
            print("⚠️ Advertencia: El grafo necesita al menos 2 nodos para la simulación")
            return
        
        # Inicializar distribuciones por defecto para todos los nodos
        for i, nodo in enumerate(nodos):
            if not self.gestor_distribuciones.tiene_distribucion(nodo):
                # Distribución exponencial por defecto con tasas variadas
                lambda_val = 0.3 + (i * 0.2)  # Tasas de 0.3 a 0.9
                self.gestor_distribuciones.configurar_distribucion(
                    nodo, 'exponencial', {'lambda': lambda_val}
                )
        
        print(f"✅ Distribuciones por defecto inicializadas para {len(nodos)} nodos")
    
    def _precalcular_rangos_atributos(self):
        """Pre-calcula los rangos de atributos una sola vez al cargar el grafo"""
        if self.rangos_calculados or not self.grafo:
            return
        
        self.rangos_atributos = GrafoUtils.precalcular_rangos_atributos(self.grafo)
        self.rangos_calculados = True
        print(f"✅ Rangos pre-calculados para {len(self.rangos_atributos)} atributos")
    
    def _configurar_limites_adaptativos(self):
        """Configura límites según el tamaño del grafo"""
        if not self.grafo:
            return
        
        num_nodos = len(self.grafo.nodes())
        num_perfiles = len(self.perfiles_df) if self.perfiles_df is not None else 1
        
        # Límites adaptativos
        if num_nodos <= 10:
            self.config.max_rutas_por_perfil = 50
            self.config.max_rutas_total = 200
        elif num_nodos <= 20:
            self.config.max_rutas_por_perfil = 100
            self.config.max_rutas_total = 500
        else:
            self.config.max_rutas_por_perfil = 200
            self.config.max_rutas_total = 1000
        
        print(f"✅ Límites adaptativos: {self.config.max_rutas_por_perfil} rutas/perfil, {self.config.max_rutas_total} total")
    
    def _precalcular_rutas_por_perfil(self):
        """Pre-calcula rutas para cada perfil de ciclista para optimizar rendimiento"""
        if not self.perfiles_df is not None or not self.grafo:
            return
        
        print("🔄 Pre-calculando rutas por perfil...")
        
        # Convertir perfiles a formato requerido
        perfiles = []
        for _, perfil_data in self.perfiles_df.iterrows():
            perfil = {
                'id': int(perfil_data['PERFILES']),
                'pesos': {
                    'distancia': perfil_data['DISTANCIA'],
                    'seguridad': perfil_data['SEGURIDAD'],
                    'luminosidad': perfil_data['LUMINOSIDAD'],
                    'inclinacion': perfil_data['INCLINACION']
                }
            }
            perfiles.append(perfil)
        
        # Pre-calcular rutas
        self.rutas_por_perfil = RutasUtils.precalcular_rutas_por_perfil(
            self.grafo, perfiles, self.rangos_atributos, self.config.max_rutas_por_perfil
        )
        
        total_rutas = sum(len(rutas) for rutas in self.rutas_por_perfil.values())
        print(f"✅ Pre-calculadas {total_rutas} rutas para {len(perfiles)} perfiles")
    
    def _inicializar_grafo(self):
        """Inicializa el grafo y configura distribuciones por defecto"""
        if not self.grafo or not self.pos_grafo:
            return
        
        nodos = list(self.grafo.nodes())
        if len(nodos) < 2:
            print("⚠️ Advertencia: El grafo necesita al menos 2 nodos para la simulación")
            return
        
        # Las distribuciones se inicializarán después en _inicializar_distribuciones_por_defecto
        
        # Inicializar colores para cada nodo
        self._inicializar_colores_nodos(nodos)
        
        # Calcular rutas dinámicas
        self._calcular_rutas_dinamicas()
        
        print(f"✅ Grafo inicializado con {len(nodos)} nodos")
    
    def _inicializar_colores_nodos(self, nodos: List[str]):
        """Inicializa colores únicos para cada nodo"""
        colores_base = [
            '#CC0000', '#006666', '#003366', '#006600', '#CC6600',
            '#660066', '#006633', '#CC9900', '#663399', '#003399',
            '#CC3300', '#006600', '#990000', '#4B0082', '#2F4F2F',
            '#8B4513', '#800080', '#191970', '#2E8B57', '#8B0000'
        ]
        
        for i, nodo in enumerate(nodos):
            color = colores_base[i % len(colores_base)]
            self.colores_nodos[nodo] = color
        
        print(f"🎨 Colores asignados a {len(nodos)} nodos")
    
    def _calcular_rutas_dinamicas(self):
        """Calcula todas las rutas posibles entre nodos del grafo"""
        if not self.grafo:
            return
        
        self.rutas_dinamicas = []
        nodos = list(self.grafo.nodes())
        
        # Calcular rutas entre todos los pares de nodos
        for origen in nodos:
            for destino in nodos:
                if origen != destino:
                    try:
                        if self.grafo.has_edge(origen, destino):
                            self.rutas_dinamicas.append((origen, destino))
                        elif nx.has_path(self.grafo, origen, destino):
                            self.rutas_dinamicas.append((origen, destino))
                    except:
                        continue
        
        print(f"✅ {len(self.rutas_dinamicas)} rutas dinámicas calculadas")
    
    def inicializar_simulacion(self):
        """Inicializa una nueva simulación con los parámetros configurados"""
        # Limpiar datos anteriores
        self.coordenadas = []
        self.rutas = []
        self.colores = []
        self.trayectorias = []
        self.velocidades = []
        self.procesos = []
        self.ciclista_id_counter = 0
        
        # Crear entorno SimPy
        self.env = simpy.Environment()
        
        # Crear procesos de ciclistas
        if self.usar_grafo_real and self.gestor_distribuciones.distribuciones:
            self.env.process(self._generador_ciclistas_realista())
            self.env.process(self._detener_por_tiempo())
        else:
            # Crear simulación básica sin grafo
            self.env.process(self._generador_ciclistas_basico())
            self.env.process(self._detener_por_tiempo())
            print("ℹ️ Simulación básica iniciada. Carga un grafo para simulación avanzada.")
        
        self.estado = "detenido"
        self.tiempo_actual = 0
        self.tiempo_total = self.config.duracion_simulacion
    
    def _generador_ciclistas_basico(self):
        """Genera ciclistas para simulación básica sin grafo"""
        while self.estado != "completada":
            # Generar tiempo de arribo aleatorio
            tiempo_arribo = np.random.exponential(2.0)  # 0.5 arribos por segundo
            yield self.env.timeout(tiempo_arribo)
            
            # Crear nuevo ciclista
            ciclista_id = self.ciclista_id_counter
            self.ciclista_id_counter += 1
            
            # Generar ruta básica
            rutas_basicas = ["A→B", "A→C", "B→A", "C→A"]
            ruta = str(np.random.choice(rutas_basicas))
            velocidad = random.uniform(self.config.velocidad_min, self.config.velocidad_max)
            
            # Colores para cada ruta
            colores_rutas = {
                "A→B": '#FF6B35',  # Naranja
                "A→C": '#FF1744',  # Rojo
                "B→A": '#00E676',  # Verde
                "C→A": '#2979FF'   # Azul
            }
            
            # Agregar datos del ciclista
            self.rutas.append(ruta)
            self.colores.append(colores_rutas[ruta])
            self.velocidades.append(velocidad)
            self.coordenadas.append((-1000, -1000))  # Posición inicial invisible
            self.trayectorias.append([])
            
            # Marcar ciclista como activo
            self.estado_ciclistas[ciclista_id] = 'activo'
            
            # Crear proceso del ciclista
            proceso = self.env.process(self._ciclista_basico(ciclista_id, velocidad, ruta))
            self.procesos.append(proceso)
    
    def _ciclista_basico(self, id: int, velocidad: float, ruta: str):
        """Lógica de movimiento de un ciclista en simulación básica"""
        # Esperar tiempo de arribo
        yield self.env.timeout(random.uniform(1.0, 3.0))
        
        # Definir trayectorias básicas para cada ruta
        trayectorias = {
            "A→B": [(0, 0), (25, 0), (50, 0), (50, 15), (50, 30)],
            "A→C": [(0, 0), (25, 0), (50, 0), (50, -15), (50, -30)],
            "B→A": [(50, 30), (50, 15), (50, 0), (25, 0), (0, 0)],
            "C→A": [(50, -30), (50, -15), (50, 0), (25, 0), (0, 0)]
        }
        
        trayectoria = trayectorias.get(ruta, [(0, 0), (50, 0)])
        
        # Mover a través de la trayectoria
        for i in range(len(trayectoria) - 1):
            punto_actual = trayectoria[i]
            punto_siguiente = trayectoria[i + 1]
            
            # Calcular distancia
            distancia = np.sqrt((punto_siguiente[0] - punto_actual[0])**2 + 
                              (punto_siguiente[1] - punto_actual[1])**2)
            
            # Calcular tiempo de movimiento
            tiempo_movimiento = distancia / velocidad
            
            # Interpolar movimiento
            pasos = max(1, int(tiempo_movimiento / 0.5))  # 0.5 segundos por paso
            for paso in range(pasos + 1):
                yield self.env.timeout(0.5)
                
                # Interpolación lineal
                t = paso / pasos if pasos > 0 else 0
                x = float(punto_actual[0] + t * (punto_siguiente[0] - punto_actual[0]))
                y = float(punto_actual[1] + t * (punto_siguiente[1] - punto_actual[1]))
                
                # Actualizar posición
                if id < len(self.coordenadas):
                    self.coordenadas[id] = (x, y)
                    self.trayectorias[id].append((x, y))
        
        # Marcar ciclista como completado
        self.estado_ciclistas[id] = 'completado'
        
        # Mover ciclista fuera de la vista
        if id < len(self.coordenadas):
            self.coordenadas[id] = (-1000, -1000)
    
    def _detener_por_tiempo(self):
        """Detiene la simulación después del tiempo configurado"""
        yield self.env.timeout(self.config.duracion_simulacion)
        self.estado = "completada"
        print(f"✅ Simulación completada después de {self.config.duracion_simulacion} segundos")
    
    def _generador_ciclistas_realista(self):
        """Genera ciclistas de manera realista usando las distribuciones de arribo"""
        while self.estado != "completada":
            # Seleccionar nodo origen basado en las distribuciones
            nodo_origen = self._seleccionar_nodo_origen()
            
            if nodo_origen:
                # Generar tiempo de arribo para este nodo
                tiempo_arribo = self.gestor_distribuciones.generar_tiempo_arribo(nodo_origen)
                yield self.env.timeout(tiempo_arribo)
                
                # Crear nuevo ciclista
                ciclista_id = self.ciclista_id_counter
                self.ciclista_id_counter += 1
                
                # Generar ruta usando perfiles y matriz de rutas
                origen, destino, ruta_nodos = self._asignar_ruta_desde_nodo(nodo_origen, ciclista_id)
                if origen and destino:
                    velocidad = random.uniform(self.config.velocidad_min, self.config.velocidad_max)
                    
                    # Crear representación de la ruta para almacenar
                    ruta_str = f"{origen}->{destino}"
                    ruta_detallada = "->".join(ruta_nodos)
                    
                    # Rastrear la ruta utilizada
                    if ruta_detallada not in self.rutas_utilizadas:
                        self.rutas_utilizadas[ruta_detallada] = 0
                    self.rutas_utilizadas[ruta_detallada] += 1
                    
                    # Almacenar información de la ruta para este ciclista
                    self.rutas_por_ciclista[ciclista_id] = {
                        'origen': origen,
                        'destino': destino,
                        'ruta_detallada': ruta_detallada,
                        'ruta_simple': ruta_str
                    }
                    
                    # Marcar ciclista como activo
                    self.estado_ciclistas[ciclista_id] = 'activo'
                    
                    # Rastrear ciclistas por nodo de origen
                    if nodo_origen not in self.ciclistas_por_nodo:
                        self.ciclistas_por_nodo[nodo_origen] = 0
                    self.ciclistas_por_nodo[nodo_origen] += 1
                    
                    # Agregar datos del ciclista
                    self.rutas.append(ruta_str)
                    self.colores.append(self.colores_nodos.get(nodo_origen, '#6C757D'))
                    self.velocidades.append(velocidad)
                    self.coordenadas.append((-1000, -1000))  # Posición inicial invisible
                    self.trayectorias.append([])
                    
                    # Crear proceso del ciclista
                    proceso = self.env.process(self._ciclista(ciclista_id, velocidad))
                    self.procesos.append(proceso)
            else:
                # Fallback: esperar un poco y reintentar
                yield self.env.timeout(1.0)
    
    def _seleccionar_nodo_origen(self) -> Optional[str]:
        """Selecciona un nodo origen basado en las distribuciones configuradas"""
        distribuciones = self.gestor_distribuciones.distribuciones
        if not distribuciones:
            return None
        
        # Seleccionar nodo basado en las tasas de arribo (lambda)
        nodos = list(distribuciones.keys())
        tasas = []
        
        for nodo in nodos:
            distribucion = distribuciones[nodo]
            if distribucion.obtener_tipo() in ['exponencial', 'poisson']:
                tasas.append(distribucion.obtener_parametros().get('lambda', 0.5))
            else:
                # Para uniforme, usar tasa promedio
                params = distribucion.obtener_parametros()
                min_val = params.get('min', 1.0)
                max_val = params.get('max', 5.0)
                tasas.append(2.0 / ((min_val + max_val) / 2))  # Aproximación
        
        # Selección ponderada por tasas
        if tasas:
            total_tasa = sum(tasas)
            if total_tasa > 0:
                probabilidades = [tasa / total_tasa for tasa in tasas]
                return str(np.random.choice(nodos, p=probabilidades))
        
        return random.choice(nodos) if nodos else None
    
    def _asignar_ruta_desde_nodo(self, nodo_origen: str, ciclista_id: int) -> tuple:
        """Genera una ruta desde el nodo origen usando perfiles y matriz de rutas"""
        if not self.grafo or nodo_origen not in self.grafo.nodes():
            return None, None, None
        
        # Seleccionar perfil para este ciclista
        perfil = self._seleccionar_perfil_ciclista()
        self.perfiles_ciclistas[ciclista_id] = perfil
        
        # Seleccionar destino usando matriz de rutas
        nodo_destino = self._seleccionar_destino(nodo_origen)
        
        if not nodo_destino:
            return None, None, None
        
        # Intentar obtener ruta desde cache primero
        perfil_id = perfil.get('id', 0)
        ruta_nodos = RutasUtils.obtener_ruta_desde_cache(
            self.rutas_por_perfil, perfil_id, nodo_origen, nodo_destino
        )
        
        # Si no está en cache, calcular dinámicamente
        if not ruta_nodos:
            try:
                ruta_nodos = RutasUtils.calcular_ruta_optima(
                    self.grafo, nodo_origen, nodo_destino, perfil, self.rangos_atributos
                )
            except Exception as e:
                print(f"⚠️ Error calculando ruta dinámica: {e}")
                ruta_nodos = []
        
        if not ruta_nodos:
            return None, None, None
        
        return nodo_origen, nodo_destino, ruta_nodos
    
    def _seleccionar_perfil_ciclista(self) -> dict:
        """Selecciona un perfil aleatorio para un nuevo ciclista"""
        if self.perfiles_df is None:
            # Perfil por defecto si no hay perfiles disponibles
            return {
                'id': 0,
                'pesos': {
                    'distancia': 0.4,
                    'seguridad': 0.3,
                    'luminosidad': 0.2,
                    'inclinacion': 0.1
                }
            }
        
        # Seleccionar perfil aleatorio
        perfil_id = int(np.random.choice(self.perfiles_df['PERFILES']))
        perfil_data = self.perfiles_df[self.perfiles_df['PERFILES'] == perfil_id].iloc[0]
        
        return {
            'id': int(perfil_id),
            'pesos': {
                'distancia': perfil_data['DISTANCIA'],
                'seguridad': perfil_data['SEGURIDAD'],
                'luminosidad': perfil_data['LUMINOSIDAD'],
                'inclinacion': perfil_data['INCLINACION']
            }
        }
    
    def _seleccionar_destino(self, nodo_origen: str) -> str:
        """Selecciona un destino basado en las probabilidades de la matriz RUTAS"""
        if self.rutas_df is None:
            # Selección aleatoria simple si no hay matriz de rutas
            nodos_destino = [nodo for nodo in self.grafo.nodes() if nodo != nodo_origen]
            return str(np.random.choice(nodos_destino)) if nodos_destino else None
        
        try:
            # Buscar la fila correspondiente al nodo origen
            fila_origen = self.rutas_df[self.rutas_df['NODO'] == nodo_origen]
            if fila_origen.empty:
                # Fallback si no se encuentra el nodo
                nodos_destino = [nodo for nodo in self.grafo.nodes() if nodo != nodo_origen]
                return str(np.random.choice(nodos_destino)) if nodos_destino else None
            
            fila_origen = fila_origen.iloc[0]
            nodos_destino = [col for col in self.rutas_df.columns if col != 'NODO']
            probabilidades = [fila_origen[nodo] for nodo in nodos_destino]
            
            # Seleccionar destino basado en probabilidades
            return str(np.random.choice(nodos_destino, p=probabilidades))
            
        except Exception as e:
            print(f"⚠️ Error seleccionando destino: {e}")
            # Fallback en caso de error
            nodos_destino = [nodo for nodo in self.grafo.nodes() if nodo != nodo_origen]
            return str(np.random.choice(nodos_destino)) if nodos_destino else None
    
    def _ciclista(self, id: int, velocidad: float):
        """Lógica de movimiento de un ciclista individual usando grafo real"""
        ruta = self.rutas[id]
        if not ruta or ruta == "N/A":
            return
            
        origen, destino = ruta.split('->')
        yield from self._ciclista_grafo_real(id, origen, destino, velocidad)
    
    def _ciclista_grafo_real(self, id: int, origen: str, destino: str, velocidad: float):
        """Movimiento usando coordenadas reales del grafo NetworkX con rutas dinámicas"""
        # Verificar que los nodos existen en el grafo
        if origen not in self.grafo.nodes() or destino not in self.grafo.nodes():
            print(f"⚠️ Error: Nodos {origen} o {destino} no existen en el grafo")
            return
        
        # Esperar tiempo de arribo basado en la distribución del nodo origen
        tiempo_arribo = self.gestor_distribuciones.generar_tiempo_arribo(origen)
        yield self.env.timeout(tiempo_arribo)
        
        # Obtener la ruta detallada para este ciclista
        if id in self.rutas_por_ciclista:
            ruta_detallada = self.rutas_por_ciclista[id]['ruta_detallada']
            nodos_ruta = ruta_detallada.split('->')
        else:
            # Fallback: ruta directa
            nodos_ruta = [origen, destino]
        
        # Posición inicial en el nodo origen
        pos_inicial = GrafoUtils.obtener_coordenada_nodo(self.pos_grafo, nodos_ruta[0])
        self.coordenadas[id] = pos_inicial
        self.trayectorias[id].append(pos_inicial)
        
        # Mover a través de cada segmento de la ruta
        for i in range(len(nodos_ruta) - 1):
            nodo_actual = nodos_ruta[i]
            nodo_siguiente = nodos_ruta[i + 1]
            
            # Obtener coordenadas de los nodos
            pos_actual = GrafoUtils.obtener_coordenada_nodo(self.pos_grafo, nodo_actual)
            pos_siguiente = GrafoUtils.obtener_coordenada_nodo(self.pos_grafo, nodo_siguiente)
            
            # Obtener distancia real del arco
            distancia_real = GrafoUtils.obtener_distancia_arco(self.grafo, nodo_actual, nodo_siguiente)
            
            # Obtener atributos del arco para ajustar velocidad
            atributos_arco = GrafoUtils.obtener_atributos_arco(self.grafo, nodo_actual, nodo_siguiente)
            velocidad_ajustada = GrafoUtils.calcular_velocidad_ajustada(velocidad, atributos_arco)
            
            # Actualizar velocidad del ciclista para estadísticas
            self.velocidades[id] = velocidad_ajustada
            
            # Movimiento interpolado suave entre nodos con velocidad ajustada
            yield from self._interpolar_movimiento(pos_actual, pos_siguiente, distancia_real, velocidad_ajustada, id)
        
        # Marcar ciclista como completado cuando termine su ruta
        self.estado_ciclistas[id] = 'completado'
        
        # Mover ciclista fuera de la vista (posición invisible)
        self.coordenadas[id] = (-1000, -1000)  # Posición fuera del área visible
    
    def _interpolar_movimiento(self, origen: Tuple[float, float], destino: Tuple[float, float], 
                             distancia: float, velocidad: float, ciclista_id: int):
        """Interpola el movimiento suave entre dos puntos del grafo"""
        if distancia <= 0 or velocidad <= 0:
            return
        
        # Reducir frecuencia de actualización para mejor rendimiento
        tiempo_total = distancia / velocidad
        pasos = max(1, min(int(tiempo_total / 0.5), 200))  # Máximo 200 pasos
        
        # Pre-calcular incrementos para eficiencia
        dx = (destino[0] - origen[0]) / pasos
        dy = (destino[1] - origen[1]) / pasos
        
        for i in range(pasos + 1):
            yield self.env.timeout(0.5)  # 0.5 segundos por paso
            
            # Interpolación lineal optimizada
            x = float(origen[0] + i * dx)
            y = float(origen[1] + i * dy)
            
            self.coordenadas[ciclista_id] = (x, y)
            
            # Solo guardar cada 5to punto para reducir memoria
            if i % 5 == 0 and len(self.trayectorias[ciclista_id]) < 100:
                self.trayectorias[ciclista_id].append((x, y))
    
    def ejecutar_paso(self):
        """Ejecuta un paso de la simulación"""
        if self.env and self.estado == "ejecutando":
            self.env.step()
            self.tiempo_actual = self.env.now
            
            # Gestión inteligente de memoria cada 10 pasos
            if int(self.tiempo_actual) % 10 == 0:
                self._gestionar_memoria_inteligente()
            
            return True
        return False
    
    def pausar_simulacion(self):
        """Pausa la simulación"""
        if self.estado == "ejecutando":
            self.estado = "pausado"
    
    def reanudar_simulacion(self):
        """Reanuda la simulación pausada"""
        if self.estado == "pausado":
            self.estado = "ejecutando"
    
    def detener_simulacion(self):
        """Detiene la simulación"""
        self.estado = "detenido"
        self.tiempo_actual = 0
    
    def reiniciar_simulacion(self):
        """Reinicia la simulación desde el principio"""
        self.inicializar_simulacion()
    
    def _gestionar_memoria_inteligente(self):
        """Gestión inteligente de memoria para múltiples ciclistas"""
        # Limpiar ciclistas antiguos
        ciclistas_limpiados = self.pool_ciclistas.limpiar_ciclistas_antiguos()
        if ciclistas_limpiados > 0:
            print(f"✅ Limpiados {ciclistas_limpiados} ciclistas antiguos")
    
    def obtener_estado_actual(self) -> Dict:
        """Retorna el estado actual de la simulación"""
        return {
            'estado': self.estado,
            'tiempo_actual': self.tiempo_actual,
            'coordenadas': self.coordenadas.copy(),
            'colores': self.colores.copy(),
            'ruta_actual': self.rutas.copy()
        }
    
    def obtener_ciclistas_activos(self) -> Dict:
        """Retorna solo los ciclistas que están activos (no completados)"""
        ciclistas_activos = {
            'coordenadas': [],
            'colores': [],
            'ruta_actual': [],
            'velocidades': [],
            'trayectorias': []
        }
        
        # Verificar que todas las listas tengan la misma longitud
        if not self.coordenadas or not self.colores or not self.rutas or not self.velocidades or not self.trayectorias:
            return ciclistas_activos
        
        # Verificar que todas las listas tengan la misma longitud
        min_length = min(len(self.coordenadas), len(self.colores), len(self.rutas), 
                        len(self.velocidades), len(self.trayectorias))
        
        if min_length == 0:
            return ciclistas_activos
        
        for i in range(min_length):
            # Solo incluir si el ciclista está activo
            if i in self.estado_ciclistas and self.estado_ciclistas[i] == 'activo':
                # Asegurar que las coordenadas sean una tupla de floats
                coords = self.coordenadas[i]
                if hasattr(coords, '__iter__') and len(coords) == 2:
                    coords_tuple = (float(coords[0]), float(coords[1]))
                else:
                    coords_tuple = (0.0, 0.0)
                
                ciclistas_activos['coordenadas'].append(coords_tuple)
                ciclistas_activos['colores'].append(self.colores[i])
                ciclistas_activos['ruta_actual'].append(self.rutas[i])
                ciclistas_activos['velocidades'].append(self.velocidades[i])
                ciclistas_activos['trayectorias'].append(self.trayectorias[i])
        
        return ciclistas_activos
    
    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas de la simulación"""
        # Contar ciclistas activos
        ciclistas_activos = sum(1 for estado in self.estado_ciclistas.values() if estado == 'activo')
        ciclistas_completados = sum(1 for estado in self.estado_ciclistas.values() if estado == 'completado')
        
        # Obtener velocidades solo de ciclistas activos
        velocidades_activas = []
        for i, velocidad in enumerate(self.velocidades):
            if i in self.estado_ciclistas and self.estado_ciclistas[i] == 'activo':
                velocidades_activas.append(velocidad)
        
        stats = {
            'total_ciclistas': len(self.coordenadas),
            'ciclistas_activos': ciclistas_activos,
            'ciclistas_completados': ciclistas_completados,
            'velocidad_promedio': np.mean(velocidades_activas) if velocidades_activas else 0,
            'velocidad_minima': min(velocidades_activas) if velocidades_activas else 0,
            'velocidad_maxima': max(velocidades_activas) if velocidades_activas else 0,
            'usando_grafo_real': self.usar_grafo_real,
            'duracion_simulacion': self.config.duracion_simulacion
        }
        
        # Agregar estadísticas del grafo si está disponible
        if self.usar_grafo_real and self.grafo:
            stats.update({
                'grafo_nodos': len(self.grafo.nodes()),
                'grafo_arcos': len(self.grafo.edges()),
                'grafo_conectado': nx.is_connected(self.grafo)
            })
            
            # Calcular distancia promedio de arcos
            if self.grafo.edges():
                distancias = [self.grafo[u][v].get('weight', 0) for u, v in self.grafo.edges()]
                stats['distancia_promedio_arcos'] = np.mean(distancias) if distancias else 0
            
            # Estadísticas de distribuciones
            stats_distribuciones = self.gestor_distribuciones.obtener_estadisticas()
            stats.update(stats_distribuciones)
        
        # Agregar estadísticas de rutas
        stats.update({
            'rutas_utilizadas': len(self.rutas_utilizadas),
            'total_viajes': sum(self.rutas_utilizadas.values()) if self.rutas_utilizadas else 0,
            'ruta_mas_usada': self._obtener_ruta_mas_usada(),
            'rutas_por_frecuencia': self._obtener_rutas_por_frecuencia()
        })
        
        # Agregar estadísticas de ciclistas por nodo
        stats.update({
            'ciclistas_por_nodo': self.ciclistas_por_nodo.copy(),
            'nodo_mas_activo': self._obtener_nodo_mas_activo()
        })
        
        # Agregar estadísticas del pool y memoria
        stats.update({
            'estadisticas_persistentes': self.estadisticas_persistentes.copy(),
            'pool_estadisticas': self.pool_ciclistas.obtener_estadisticas()
        })
        
        return stats
    
    def _obtener_ruta_mas_usada(self) -> str:
        """Obtiene la ruta más utilizada"""
        if not self.rutas_utilizadas:
            return "N/A"
        
        ruta_mas_usada = max(self.rutas_utilizadas.items(), key=lambda x: x[1])
        return f"{ruta_mas_usada[0]} ({ruta_mas_usada[1]} viajes)"
    
    def _obtener_rutas_por_frecuencia(self) -> list:
        """Obtiene las rutas ordenadas por frecuencia de uso"""
        if not self.rutas_utilizadas:
            return []
        
        # Ordenar rutas por frecuencia (descendente)
        rutas_ordenadas = sorted(self.rutas_utilizadas.items(), key=lambda x: x[1], reverse=True)
        
        # Retornar las top 5 rutas
        return rutas_ordenadas[:5]
    
    def _obtener_nodo_mas_activo(self) -> str:
        """Obtiene el nodo que ha generado más ciclistas"""
        if not self.ciclistas_por_nodo:
            return "N/A"
        
        nodo_mas_activo = max(self.ciclistas_por_nodo.items(), key=lambda x: x[1])
        return f"Nodo {nodo_mas_activo[0]} ({nodo_mas_activo[1]} ciclistas)"
    
    def configurar_distribuciones_nodos(self, distribuciones: Dict[str, Dict]):
        """Configura las distribuciones de probabilidad para cada nodo"""
        self.gestor_distribuciones.configurar_desde_dict(distribuciones)
        print(f"✅ Distribuciones configuradas para {len(distribuciones)} nodos")
    
    def obtener_distribuciones_nodos(self) -> Dict[str, Dict]:
        """Retorna la configuración actual de distribuciones"""
        return self.gestor_distribuciones.obtener_todas_distribuciones()
    
    def actualizar_distribucion_nodo(self, nodo_id: str, tipo: str, parametros: Dict):
        """Actualiza la distribución de un nodo específico"""
        self.gestor_distribuciones.configurar_distribucion(nodo_id, tipo, parametros)
        print(f"✅ Distribución actualizada para nodo {nodo_id}: {tipo}")
    
    def limpiar_cache_optimizaciones(self):
        """Limpia el cache de optimizaciones para liberar memoria"""
        self.grafos_por_perfil = {}
        self.rutas_por_perfil = {}
        self.pool_ciclistas.reiniciar_pool()
        print("✅ Cache de optimizaciones limpiado")
