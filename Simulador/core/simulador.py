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
import math
from typing import List, Tuple, Dict, Optional, Any

from ..models.ciclista import Ciclista, PoolCiclistas
from ..distributions.distribucion_nodo import DistribucionNodo, GestorDistribuciones
from ..utils.grafo_utils import GrafoUtils
from ..utils.rutas_utils import RutasUtils
from ..utils.estadisticas_utils import EstadisticasUtils
from ..utils.generador_excel import GeneradorExcel
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
        
        # Sistema de rastreo de arcos/tramos
        self.arcos_utilizados = {}  # Dict[arco_str, contador] para contar uso de arcos
        self.arcos_por_ciclista = {}  # Dict[ciclista_id, lista_arcos] para rastrear arcos por ciclista
        
        # Sistema de rastreo de estado de ciclistas
        self.estado_ciclistas = {}  # Dict[ciclista_id, estado] para rastrear si están activos o completados
        self.ciclistas_por_nodo = {}  # Dict[nodo_origen, contador] para contar ciclistas por nodo de origen
        
        # Sistema de perfiles y rutas
        self.perfiles_df = None  # DataFrame con perfiles de ciclistas
        self.rutas_df = None  # DataFrame con matriz de probabilidades de destino
        self.perfiles_ciclistas = {}  # Dict[ciclista_id, perfil] para rastrear perfil de cada ciclista
        self.contador_perfiles = {}  # Dict[perfil_id, contador] para rastrear uso de perfiles
        
        # Sistema de rastreo de tiempos de desplazamiento
        self.tiempos_por_ciclista = {}  # Dict[ciclista_id, tiempo_total] para rastrear tiempo total de viaje
        self.tiempos_por_tramo = {}  # Dict[ciclista_id, lista_tiempos_tramos] para rastrear tiempo por tramo
        self.tiempo_inicio_viaje = {}  # Dict[ciclista_id, tiempo_inicio] para calcular duración total
        
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
        
        # Generador de Excel para resultados
        self.generador_excel = GeneradorExcel()
        
        # Flag para controlar generación de Excel (evitar duplicación)
        self.excel_generado = False
        self.ruta_excel_generado = None
        
        self.nombre_grafo_actual = "simulacion"
    
    def configurar_grafo(self, grafo: nx.Graph, posiciones: Dict, perfiles_df=None, rutas_df=None, nombre_grafo: str = "simulacion"):
        """Configura el grafo NetworkX y sus posiciones para la simulación"""
        if not GrafoUtils.validar_grafo(grafo):
            print("⚠️ Advertencia: El grafo no es válido")
            self.usar_grafo_real = False
            return False
            
        self.grafo = grafo
        self.pos_grafo = posiciones
        self.usar_grafo_real = True
        self.nombre_grafo_actual = nombre_grafo
        
        # Guardar referencia al grafo base para cache
        self.grafo_base = grafo.copy()
        
        # Configurar perfiles y rutas si están disponibles
        self.perfiles_df = perfiles_df
        self.rutas_df = rutas_df
        
        # Validar probabilidades de perfiles si están disponibles
        if self.perfiles_df is not None:
            self._validar_probabilidades_perfiles()
        
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
    
    def _validar_probabilidades_perfiles(self):
        """Valida que las probabilidades de los perfiles sumen 1.0"""
        if self.perfiles_df is None or 'PROBABILIDAD' not in self.perfiles_df.columns:
            print("ℹ️ No hay datos de probabilidades de perfiles para validar")
            return
        
        probabilidades = self.perfiles_df['PROBABILIDAD'].values
        suma_probabilidades = np.sum(probabilidades)
        
        print(f"📊 Validando probabilidades de perfiles:")
        print(f"   - Suma total: {suma_probabilidades:.4f}")
        
        # Verificar si las probabilidades suman 1.0 (con tolerancia de 0.01)
        if abs(suma_probabilidades - 1.0) > 0.01:
            print(f"⚠️ Advertencia: Las probabilidades suman {suma_probabilidades:.4f}, no 1.0")
            print("   Se normalizarán automáticamente durante la simulación")
        else:
            print("✅ Las probabilidades suman correctamente 1.0")
        
        # Mostrar distribución de probabilidades
        print("   Distribución de probabilidades por perfil:")
        for _, row in self.perfiles_df.iterrows():
            perfil_id = int(row['PERFILES'])
            prob = row['PROBABILIDAD']
            print(f"   - Perfil {perfil_id}: {prob:.2f} ({prob*100:.1f}%)")
    
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
        if self.perfiles_df is None or self.grafo is None:
            return
        
        print("🔄 Pre-calculando rutas por perfil...")
        
        # Obtener atributos comunes entre ARCOS y PERFILES
        atributos_arcos = set(self.rangos_atributos.keys())
        atributos_perfiles = set(self.perfiles_df.columns) - {'PERFILES'}
        atributos_comunes = atributos_arcos.intersection(atributos_perfiles)
        
        print(f"📋 Atributos comunes (ARCOS ∩ PERFILES): {atributos_comunes}")
        print(f"ℹ️ Sólo estos atributos se usarán para decisión de ruta")
        
        # Convertir perfiles a formato requerido
        perfiles = []
        for _, perfil_data in self.perfiles_df.iterrows():
            # Solo incluir atributos que están en AMBOS (ARCOS y PERFILES)
            pesos = {}
            
            # Cargar dinámicamente los atributos que existen en ambas hojas
            for col_excel in atributos_comunes:
                if col_excel in perfil_data.index:
                    # Normalizar nombre a minúsculas para consistencia interna
                    clave_interna = col_excel.lower()
                    pesos[clave_interna] = perfil_data[col_excel]
                    print(f"✅ Atributo {clave_interna} cargado desde {col_excel} (peso: {perfil_data[col_excel]:.2f})")
            
            perfil = {
                'id': int(perfil_data['PERFILES']),
                'pesos': pesos
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
        
        # Resetear flag de Excel para nueva simulación
        self.excel_generado = False
        self.ruta_excel_generado = None
        
        # Limpiar contadores de perfiles
        self.contador_perfiles = {}
        self.perfiles_ciclistas = {}
        
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
            print("Simulacion basica iniciada. Carga un grafo para simulacion avanzada.")
        
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
        
        # Definir trayectorias básicas para cada ruta con inclinaciones simuladas
        trayectorias = {
            "A→B": [
                ((0, 0), 0),    # Punto inicial, inclinación 0%
                ((25, 0), 2),   # Segmento plano con ligera inclinación
                ((50, 0), 5),   # Segmento con inclinación 5%
                ((50, 15), 3),  # Segmento con inclinación 3%
                ((50, 30), 0)   # Punto final, inclinación 0%
            ],
            "A→C": [
                ((0, 0), 0),     # Punto inicial, inclinación 0%
                ((25, 0), 2),    # Segmento plano con ligera inclinación
                ((50, 0), 4),    # Segmento con inclinación 4%
                ((50, -15), 6),  # Segmento con inclinación 6%
                ((50, -30), 0)   # Punto final, inclinación 0%
            ],
            "B→A": [
                ((50, 30), 0),   # Punto inicial, inclinación 0%
                ((50, 15), 3),   # Segmento con inclinación 3%
                ((50, 0), 5),    # Segmento con inclinación 5%
                ((25, 0), 2),    # Segmento plano con ligera inclinación
                ((0, 0), 0)      # Punto final, inclinación 0%
            ],
            "C→A": [
                ((50, -30), 0),  # Punto inicial, inclinación 0%
                ((50, -15), 6),  # Segmento con inclinación 6%
                ((50, 0), 4),    # Segmento con inclinación 4%
                ((25, 0), 2),    # Segmento plano con ligera inclinación
                ((0, 0), 0)      # Punto final, inclinación 0%
            ]
        }
        
        trayectoria = trayectorias.get(ruta, [((0, 0), 0), ((50, 0), 0)])
        
        # Mover a través de la trayectoria
        for i in range(len(trayectoria) - 1):
            punto_actual, inclinacion_actual = trayectoria[i]
            punto_siguiente, inclinacion_siguiente = trayectoria[i + 1]
            
            # Calcular distancia
            distancia = np.sqrt((punto_siguiente[0] - punto_actual[0])**2 + 
                              (punto_siguiente[1] - punto_actual[1])**2)
            
            # Calcular velocidad ajustada por inclinación
            atributos_arco = {'inclinacion': inclinacion_siguiente}
            velocidad_ajustada = GrafoUtils.calcular_velocidad_ajustada(velocidad, atributos_arco)
            
            # Actualizar velocidad del ciclista para estadísticas
            self.velocidades[id] = velocidad_ajustada
            
            # Calcular tiempo de movimiento con velocidad ajustada
            tiempo_movimiento = distancia / velocidad_ajustada
            
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
        
        # Generar archivo Excel con resultados
        self._generar_resultados_excel()
    
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
                    
                    # Rastrear arcos/tramos utilizados
                    arcos_ciclista = []
                    for i in range(len(ruta_nodos) - 1):
                        nodo_origen = ruta_nodos[i]
                        nodo_destino = ruta_nodos[i + 1]
                        arco_str = f"{nodo_origen}->{nodo_destino}"
                        
                        # Actualizar contador de arcos utilizados
                        if arco_str not in self.arcos_utilizados:
                            self.arcos_utilizados[arco_str] = 0
                        self.arcos_utilizados[arco_str] += 1
                        
                        arcos_ciclista.append(arco_str)
                    
                    # Almacenar información de la ruta para este ciclista
                    self.rutas_por_ciclista[ciclista_id] = {
                        'origen': origen,
                        'destino': destino,
                        'ruta_detallada': ruta_detallada,
                        'ruta_simple': ruta_str
                    }
                    
                    # Almacenar arcos utilizados por este ciclista
                    self.arcos_por_ciclista[ciclista_id] = arcos_ciclista
                    
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
            tipo = distribucion.obtener_tipo()
            params = distribucion.obtener_parametros()
            
            if tipo == 'exponencial':
                tasas.append(params.get('lambda', 0.5))
            elif tipo == 'normal':
                # Para normal, usar la media como tasa aproximada
                tasas.append(1.0 / params.get('media', 3.0))
            elif tipo == 'lognormal':
                # Para log-normal, usar la media de la distribución log-normal
                mu = params.get('mu', 0.0)
                sigma = params.get('sigma', 1.0)
                media_lognormal = np.exp(mu + sigma**2 / 2)
                tasas.append(1.0 / media_lognormal)
            elif tipo == 'gamma':
                # Para gamma, usar la media de la distribución gamma
                forma = params.get('forma', 2.0)
                escala = params.get('escala', 1.0)
                media_gamma = forma * escala
                tasas.append(1.0 / media_gamma)
            elif tipo == 'weibull':
                # Para Weibull, usar la media de la distribución Weibull
                forma = params.get('forma', 2.0)
                escala = params.get('escala', 1.0)
                # Media de Weibull = escala * Γ(1 + 1/forma)
                from scipy.special import gamma as gamma_func
                media_weibull = escala * gamma_func(1 + 1/forma)
                tasas.append(1.0 / media_weibull)
            else:
                # Fallback para distribuciones no reconocidas
                tasas.append(0.5)
        
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
        
        # Rastrear uso de perfiles para estadísticas
        perfil_id = perfil.get('id', 0)
        if perfil_id not in self.contador_perfiles:
            self.contador_perfiles[perfil_id] = 0
        self.contador_perfiles[perfil_id] += 1
        
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
        """Selecciona un perfil para un nuevo ciclista basado en las probabilidades de la tabla"""
        if self.perfiles_df is None:
            # Perfil por defecto dinámico: peso 1.0 solo para distancia, 0.0 para otros atributos
            pesos = {}
            
            # Detectar atributos disponibles dinámicamente del grafo
            if hasattr(self, 'rangos_atributos') and self.rangos_atributos:
                for atributo in self.rangos_atributos.keys():
                    if atributo == 'distancia':
                        pesos[atributo] = 1.0  # Peso completo para distancia
                    else:
                        pesos[atributo] = 0.0  # Cero peso para otros atributos
                
                print(f"📋 Perfil por defecto dinámico creado: {pesos}")
            else:
                # Fallback si no hay rangos calculados
                pesos = {'distancia': 1.0}
                print("⚠️ Usando perfil por defecto básico (solo distancia)")
            
            return {
                'id': 0,
                'pesos': pesos
            }
        
        # Verificar que existe la columna PROBABILIDAD
        if 'PROBABILIDAD' not in self.perfiles_df.columns:
            print("⚠️ Advertencia: No se encontró columna PROBABILIDAD, usando selección uniforme")
            perfil_id = int(np.random.choice(self.perfiles_df['PERFILES']))
        else:
            # Usar probabilidades de la tabla para seleccionar perfil
            perfiles = self.perfiles_df['PERFILES'].values
            probabilidades = self.perfiles_df['PROBABILIDAD'].values
            
            # Normalizar probabilidades para asegurar que sumen 1.0
            suma_probabilidades = np.sum(probabilidades)
            if suma_probabilidades > 0:
                probabilidades_normalizadas = probabilidades / suma_probabilidades
            else:
                # Si todas las probabilidades son 0, usar distribución uniforme
                probabilidades_normalizadas = np.ones(len(perfiles)) / len(perfiles)
                print("⚠️ Advertencia: Todas las probabilidades son 0, usando distribución uniforme")
            
            # Seleccionar perfil basado en probabilidades
            perfil_id = int(np.random.choice(perfiles, p=probabilidades_normalizadas))
        
        perfil_data = self.perfiles_df[self.perfiles_df['PERFILES'] == perfil_id].iloc[0]
        
        # Cargar atributos dinámicamente - solo los que están en AMBOS (ARCOS y PERFILES)
        pesos = {}
        if hasattr(self, 'rangos_atributos'):
            atributos_arcos = set(self.rangos_atributos.keys())
            atributos_perfiles = set(self.perfiles_df.columns) - {'PERFILES', 'PROBABILIDAD'}
            
            for col_excel in atributos_arcos.intersection(atributos_perfiles):
                if col_excel in perfil_data.index:
                    clave_interna = col_excel.lower()
                    pesos[clave_interna] = perfil_data[col_excel]
        
        return {
            'id': int(perfil_id),
            'pesos': pesos
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
            
            # Validar y normalizar probabilidades
            suma_probabilidades = np.sum(probabilidades)
            if suma_probabilidades <= 0:
                print(f"⚠️ Advertencia: Probabilidades de destino para {nodo_origen} suman {suma_probabilidades}")
                # Fallback: selección uniforme
                return str(np.random.choice(nodos_destino))
            
            # Normalizar probabilidades para que sumen 1.0
            if abs(suma_probabilidades - 1.0) > 0.01:
                probabilidades_normalizadas = np.array(probabilidades) / suma_probabilidades
                print(f"ℹ️ Probabilidades de destino para {nodo_origen} normalizadas: {suma_probabilidades:.4f} → 1.0")
            else:
                probabilidades_normalizadas = probabilidades
            
            # Seleccionar destino basado en probabilidades normalizadas
            return str(np.random.choice(nodos_destino, p=probabilidades_normalizadas))
            
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
            
            # Obtener atributos del arco para ajustar velocidad y tiempo
            atributos_arco = GrafoUtils.obtener_atributos_arco(self.grafo, nodo_actual, nodo_siguiente)
            velocidad_ajustada = GrafoUtils.calcular_velocidad_ajustada(velocidad, atributos_arco)
            factor_tiempo = GrafoUtils.calcular_factor_tiempo_desplazamiento(atributos_arco)
            
            # Actualizar velocidad del ciclista para estadísticas
            self.velocidades[id] = velocidad_ajustada
            
            # Movimiento interpolado suave entre nodos con velocidad ajustada y factor de tiempo
            yield from self._interpolar_movimiento(pos_actual, pos_siguiente, distancia_real, velocidad_ajustada, id, factor_tiempo)
        
        # Marcar ciclista como completado cuando termine su ruta
        self.estado_ciclistas[id] = 'completado'
        
        # Calcular tiempo total de viaje
        if id in self.tiempo_inicio_viaje:
            tiempo_total_viaje = self.env.now - self.tiempo_inicio_viaje[id]
            self.tiempos_por_ciclista[id] = tiempo_total_viaje
        
        # Mover ciclista fuera de la vista (posición invisible)
        self.coordenadas[id] = (-1000, -1000)  # Posición fuera del área visible
    
    def _interpolar_movimiento(self, origen: Tuple[float, float], destino: Tuple[float, float], 
                             distancia: float, velocidad: float, ciclista_id: int, 
                             factor_tiempo: float = 1.0):
        """Interpola el movimiento suave entre dos puntos del grafo
        
        Args:
            origen: Coordenadas de origen
            destino: Coordenadas de destino
            distancia: Distancia real del arco
            velocidad: Velocidad ajustada del ciclista
            ciclista_id: ID del ciclista
            factor_tiempo: Factor multiplicador para el tiempo (seguridad + iluminación)
        """
        if distancia <= 0 or velocidad <= 0:
            return
        
        # Calcular tiempo total con factor de tiempo de desplazamiento
        tiempo_base = distancia / velocidad
        tiempo_total = tiempo_base * factor_tiempo
        
        # Rastrear tiempo de inicio del tramo
        tiempo_inicio_tramo = self.env.now
        
        # Inicializar tiempo de viaje si es el primer tramo
        if ciclista_id not in self.tiempo_inicio_viaje:
            self.tiempo_inicio_viaje[ciclista_id] = self.env.now
            self.tiempos_por_tramo[ciclista_id] = []
        
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
        
        # Registrar tiempo real del tramo
        tiempo_fin_tramo = self.env.now
        tiempo_real_tramo = tiempo_fin_tramo - tiempo_inicio_tramo
        self.tiempos_por_tramo[ciclista_id].append(tiempo_real_tramo)
    
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
                # Asegurar que las coordenadas sean una tupla de floats válida
                coords = self.coordenadas[i]
                coords_tuple = (0.0, 0.0)  # Valor por defecto
                
                try:
                    if hasattr(coords, '__iter__') and len(coords) == 2:
                        x_val = float(coords[0])
                        y_val = float(coords[1])
                        # Verificar que los valores sean números válidos
                        if not (math.isnan(x_val) or math.isnan(y_val) or 
                               math.isinf(x_val) or math.isinf(y_val)):
                            coords_tuple = (x_val, y_val)
                except (ValueError, TypeError, IndexError) as e:
                    print(f"⚠️ Error procesando coordenadas del ciclista {i}: {e}")
                    coords_tuple = (0.0, 0.0)
                
                ciclistas_activos['coordenadas'].append(coords_tuple)
                ciclistas_activos['colores'].append(self.colores[i])
                ciclistas_activos['ruta_actual'].append(self.rutas[i])
                ciclistas_activos['velocidades'].append(self.velocidades[i])
                ciclistas_activos['trayectorias'].append(self.trayectorias[i])
        
        return ciclistas_activos
    
    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas de la simulación usando el módulo desacoplado"""
        return EstadisticasUtils.calcular_estadisticas_completas(self)
    
    def obtener_estadisticas_tiempo_real(self) -> Dict:
        """Retorna estadísticas en tiempo real para visualización"""
        return EstadisticasUtils.calcular_estadisticas_tiempo_real(self)
    
    def generar_reporte_detallado(self) -> str:
        """Genera un reporte detallado de la simulación"""
        return EstadisticasUtils.generar_reporte_detallado(self)
    
    
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
    
    def _generar_resultados_excel(self):
        """Genera el archivo Excel con los resultados de la simulación"""
        # Verificar si ya se generó el Excel para evitar duplicación
        if self.excel_generado:
            print("ℹ️ Archivo Excel ya fue generado anteriormente, evitando duplicación")
            return self.ruta_excel_generado
            
        try:
            print("📊 Generando archivo Excel con resultados...")
            ruta_archivo = self.generador_excel.generar_archivo_resultados(
                self, 
                self.nombre_grafo_actual
            )
            
            # Marcar como generado y almacenar ruta para evitar duplicación
            self.excel_generado = True
            self.ruta_excel_generado = ruta_archivo
            
            print(f"✅ Archivo Excel generado exitosamente: {ruta_archivo}")
            return ruta_archivo
        except Exception as e:
            print(f"❌ Error generando archivo Excel: {e}")
            return None
    
    def generar_resultados_manual(self) -> str:
        """Método público para generar resultados Excel manualmente"""
        return self._generar_resultados_excel()
