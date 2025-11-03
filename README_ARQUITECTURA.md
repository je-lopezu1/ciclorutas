# 🏗️ Arquitectura y Diseño - Simulador de Ciclorutas v2.0

## 📋 Tabla de Contenidos

- [Visión General](#visión-general)
- [Principios de Diseño](#principios-de-diseño)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Componentes Principales](#componentes-principales)
- [Flujos de Datos](#flujos-de-datos)
- [Carga de Archivos Excel](#carga-de-archivos-excel)
- [Sistema de Visualización](#sistema-de-visualización)
- [Generación de Simulaciones](#generación-de-simulaciones)
- [Sistema de Eventos y Calendario](#sistema-de-eventos-y-calendario)
- [Patrones de Diseño](#patrones-de-diseño)
- [Extensibilidad](#extensibilidad)

---

## 🎯 Visión General

El Simulador de Ciclorutas v2.0 es un sistema modular diseñado para simular el comportamiento de ciclistas en redes de ciclorutas. La arquitectura está basada en principios de **separación de responsabilidades**, **modularidad** y **escalabilidad**.

### Características Arquitectónicas Clave

- **Separación Simulador/Interfaz**: El motor de simulación es completamente independiente de la interfaz gráfica
- **Configuración Centralizada**: Todos los parámetros se gestionan desde `config.py`
- **Componentes Reutilizables**: Módulos diseñados para ser extensibles y reutilizables
- **Gestión Eficiente de Memoria**: Pool de objetos y cache inteligente para optimización

---

## 🎨 Principios de Diseño

### 1. Separación de Responsabilidades

- **Simulador**: Lógica de simulación pura usando SimPy
- **Interfaz**: Presentación y control de usuario usando Tkinter
- **Configuración**: Parámetros centralizados en `config.py`

### 2. Modularidad

- Cada módulo tiene una responsabilidad específica
- Interfaces claras entre componentes
- Bajo acoplamiento, alta cohesión

### 3. Escalabilidad

- Fácil agregar nuevas funcionalidades
- Soporte para diferentes tipos de grafos
- Configuración flexible

---

## 📁 Estructura del Proyecto

```
ciclorutas/
├── main.py                          # Punto de entrada del sistema
├── config.py                        # Configuración centralizada
├── requirements.txt                 # Dependencias del proyecto
│
├── Simulador/                       # 🎮 Motor de simulación
│   ├── __init__.py
│   ├── core/                        # Componentes principales
│   │   ├── simulador.py            # Motor principal SimPy
│   │   └── configuracion.py        # Gestión de configuración
│   ├── models/                      # Modelos de datos
│   │   └── ciclista.py             # Modelo Ciclista y Pool
│   ├── distributions/               # Distribuciones de probabilidad
│   │   └── distribucion_nodo.py    # Distribuciones por nodo
│   └── utils/                       # Utilidades del simulador
│       ├── estadisticas_utils.py   # Cálculo de estadísticas
│       ├── generador_excel.py       # Generación de reportes
│       ├── grafo_utils.py          # Utilidades para grafos NetworkX
│       └── rutas_utils.py          # Cálculo de rutas óptimas
│
└── Interfaz/                        # 🖥️ Interfaz gráfica
    ├── __init__.py
    ├── components/                  # Componentes principales
    │   └── app_principal.py        # Aplicación principal Tkinter
    ├── panels/                      # Paneles de la interfaz
    │   ├── panel_control.py        # Control de simulación
    │   ├── panel_visualizacion.py  # Visualización matplotlib
    │   ├── panel_estadisticas.py   # Estadísticas en tiempo real
    │   └── panel_distribuciones.py # Configuración de distribuciones
    └── utils/                       # Utilidades de interfaz
        ├── archivo_utils.py        # Manejo de archivos Excel
        ├── cache_utils.py          # Sistema de caché
        └── estilo_utils.py         # Estilos y temas
```

---

## 🔧 Componentes Principales

### 🎮 Módulo Simulador

#### **SimuladorCiclorutas** (`Simulador/core/simulador.py`)

**Responsabilidad**: Motor principal de simulación que orquesta toda la simulación usando SimPy.

**Funciones Clave**:

1. **Gestión del Entorno SimPy**:
   - Crea y gestiona el entorno de simulación (`simpy.Environment`)
   - Coordina todos los procesos de simulación
   - Maneja el tiempo de simulación

2. **Generación de Ciclistas**:
   - `_generador_ciclistas_realista()`: Genera ciclistas usando distribuciones de probabilidad
   - Selecciona nodos de origen basado en tasas de arribo
   - Asigna rutas usando perfiles de ciclistas

3. **Gestión de Ciclistas**:
   - Crea procesos SimPy para cada ciclista (`_ciclista()`)
   - Maneja movimiento entre nodos
   - Gestiona estados (activo, completado)

4. **Control de Simulación**:
   - `ejecutar_paso()`: Avanza la simulación un paso
   - `pausar_simulacion()` / `reanudar_simulacion()`: Control de estado
   - `detener_simulacion()`: Finaliza la simulación

**Estado Interno**:
```python
- estado: "detenido" | "ejecutando" | "pausado" | "completada"
- tiempo_actual: tiempo de simulación actual
- coordenadas: lista de posiciones de ciclistas
- rutas: lista de rutas asignadas
- colores: lista de colores por ciclista
```

#### **ConfiguracionSimulacion** (`Simulador/core/configuracion.py`)

**Responsabilidad**: Gestión centralizada de todos los parámetros de simulación.

**Parámetros Principales**:
- Velocidad mínima/máxima
- Duración de simulación
- Límites de ciclistas simultáneos
- Configuraciones de rendimiento

#### **Ciclista** (`Simulador/models/ciclista.py`)

**Responsabilidad**: Modelo de datos para un ciclista individual.

**Atributos**:
```python
- id: identificador único
- coordenadas: posición actual (x, y)
- trayectoria: lista de posiciones históricas
- velocidad: velocidad actual
- estado: 'inactivo' | 'activo' | 'completado'
- ruta: ruta asignada
- color: color para visualización
```

**PoolCiclistas**: Sistema de reutilización de objetos para eficiencia de memoria.

#### **DistribucionNodo** (`Simulador/distributions/distribucion_nodo.py`)

**Responsabilidad**: Gestión de distribuciones de probabilidad para tasas de arribo por nodo.

**Tipos de Distribuciones Soportadas**:
- Exponencial: `lambda` (tasa de arribo)
- Normal: `media`, `desviacion`
- Log-Normal: `mu`, `sigma`
- Gamma: `forma`, `escala`
- Weibull: `forma`, `escala`

**Uso**:
```python
distribucion = DistribucionNodo('exponencial', {'lambda': 0.5})
tiempo_arribo = distribucion.generar_tiempo_arribo()
```

#### **GrafoUtils** (`Simulador/utils/grafo_utils.py`)

**Responsabilidad**: Utilidades para trabajar con grafos NetworkX.

**Funciones Clave**:
- `validar_grafo()`: Valida estructura del grafo
- `obtener_coordenada_nodo()`: Obtiene coordenadas de un nodo
- `obtener_distancia_arco()`: Obtiene distancia real entre nodos
- `calcular_velocidad_ajustada()`: Ajusta velocidad por inclinación
- `precalcular_rangos_atributos()`: Pre-calcula rangos para normalización

#### **RutasUtils** (`Simulador/utils/rutas_utils.py`)

**Responsabilidad**: Cálculo de rutas óptimas basadas en perfiles de ciclistas.

**Funciones Clave**:
- `calcular_ruta_optima()`: Calcula ruta usando Dijkstra con pesos compuestos
- `_calcular_pesos_compuestos()`: Calcula pesos basados en perfil y atributos
- `precalcular_rutas_por_perfil()`: Pre-calcula rutas para optimización

**Algoritmo de Ruta**:
1. Normaliza atributos del grafo (distancia, seguridad, luminosidad, etc.)
2. Calcula peso compuesto usando pesos del perfil
3. Usa algoritmo Dijkstra para encontrar ruta óptima

---

### 🖥️ Módulo Interfaz

#### **InterfazSimulacion** (`Interfaz/components/app_principal.py`)

**Responsabilidad**: Aplicación principal que coordina todos los paneles de la interfaz.

**Funciones**:
- Inicializa y gestiona la ventana principal Tkinter
- Coordina comunicación entre paneles
- Gestiona ciclo de vida de la aplicación
- Maneja eventos de usuario

#### **PanelControl** (`Interfaz/panels/panel_control.py`)

**Responsabilidad**: Control de parámetros y botones de simulación.

**Componentes**:
- Campos de entrada para velocidades
- Campo de duración
- Botones: NUEVA, INICIAR, PAUSAR, REANUDAR, TERMINAR, ADELANTAR, REINICIAR
- Botón de carga de grafo

#### **PanelVisualizacion** (`Interfaz/panels/panel_visualizacion.py`)

**Responsabilidad**: Visualización en tiempo real usando matplotlib.

**Funciones**:
- Dibuja el grafo NetworkX usando `nx.draw()`
- Actualiza posiciones de ciclistas en tiempo real
- Colorea ciclistas según nodo de origen
- Dibuja trayectorias de ciclistas

**Actualización**:
- Se actualiza cada 50ms (`frecuencia_visualizacion`)
- Usa `matplotlib.animation` para animación suave

#### **PanelEstadisticas** (`Interfaz/panels/panel_estadisticas.py`)

**Responsabilidad**: Muestra estadísticas en tiempo real.

**Métricas Mostradas**:
- Ciclistas activos/completados
- Velocidades (promedio, min, max)
- Rutas utilizadas
- Tiempo de simulación
- Estadísticas del grafo

**Actualización**:
- Se actualiza cada 100ms desde el simulador

#### **PanelDistribuciones** (`Interfaz/panels/panel_distribuciones.py`)

**Responsabilidad**: Configuración de distribuciones de probabilidad por nodo.

**Funciones**:
- Selección de nodo
- Selección de tipo de distribución
- Configuración de parámetros
- Vista previa de distribución

#### **ArchivoUtils** (`Interfaz/utils/archivo_utils.py`)

**Responsabilidad**: Carga y validación de archivos Excel.

**Funciones Clave**:
- `validar_archivo_excel()`: Valida estructura del archivo
- `cargar_datos_desde_excel()`: Carga datos y crea grafo NetworkX
- `_calcular_distancia_euclidiana()`: Calcula distancias desde coordenadas LAT/LON

---

## 🔄 Flujos de Datos

### 1. Inicialización del Sistema

```
main.py
  └─> Verificar dependencias
  └─> InterfazSimulacion.__init__()
      └─> Crear ventana Tkinter
      └─> Inicializar paneles (Control, Visualización, Estadísticas, Distribuciones)
      └─> Crear SimuladorCiclorutas (inicialmente sin grafo)
```

### 2. Carga de Grafo

```
Usuario hace clic en "Cargar Grafo"
  └─> ArchivoUtils.seleccionar_archivo_excel()
  └─> ArchivoUtils.validar_archivo_excel()
      └─> Verifica hojas obligatorias (NODOS, ARCOS)
      └─> Verifica columnas requeridas
  └─> ArchivoUtils.cargar_datos_desde_excel()
      └─> Lee hoja "NODOS" → crea nodos
      └─> Lee hoja "ARCOS" → crea arcos con atributos
      └─> Lee hoja "PERFILES" (opcional) → perfiles de ciclistas
      └─> Lee hoja "RUTAS" (opcional) → matriz de probabilidades
      └─> Calcula coordenadas si hay LAT/LON
      └─> Crea grafo NetworkX
  └─> SimuladorCiclorutas.configurar_grafo()
      └─> Valida grafo
      └─> Pre-calcula rangos de atributos
      └─> Inicializa distribuciones por defecto
      └─> Pre-calcula rutas por perfil
  └─> PanelVisualizacion.actualizar_grafo()
      └─> Dibuja grafo en matplotlib
```

### 3. Generación de Simulación

```
Usuario hace clic en "NUEVA"
  └─> SimuladorCiclorutas.inicializar_simulacion()
      └─> Limpia datos anteriores
      └─> Crea nuevo entorno SimPy (simpy.Environment)
      └─> Crea proceso generador de ciclistas (_generador_ciclistas_realista)
      └─> Crea proceso de detención por tiempo (_detener_por_tiempo)

Usuario hace clic en "INICIAR"
  └─> SimuladorCiclorutas.estado = "ejecutando"
  └─> Bucle principal inicia (ejecutar_paso())
      └─> env.step() (avanza simulación un paso)
      └─> Actualiza tiempo_actual
      └─> Gestiona memoria cada 10 pasos
```

### 4. Generación de Ciclistas

```
_generador_ciclistas_realista() (proceso SimPy)
  └─> Bucle while (estado != "completada")
      └─> _seleccionar_nodo_origen()
          └─> Usa distribuciones configuradas
          └─> Selecciona nodo basado en tasas de arribo
      └─> generar_tiempo_arribo() para ese nodo
      └─> yield env.timeout(tiempo_arribo) (espera)
      └─> _asignar_ruta_desde_nodo()
          └─> _seleccionar_perfil_ciclista()
          └─> _seleccionar_destino() (usando matriz RUTAS)
          └─> RutasUtils.calcular_ruta_optima()
      └─> Crear proceso _ciclista() para este ciclista
      └─> Registrar en listas (coordenadas, rutas, colores, etc.)
```

### 5. Movimiento de Ciclistas

```
_ciclista() (proceso SimPy para cada ciclista)
  └─> Obtiene ruta asignada (lista de nodos)
  └─> Para cada segmento de la ruta:
      └─> GrafoUtils.obtener_coordenada_nodo() (posición actual)
      └─> GrafoUtils.obtener_distancia_arco() (distancia real)
      └─> GrafoUtils.obtener_atributos_arco() (atributos del arco)
      └─> GrafoUtils.calcular_velocidad_ajustada() (ajuste por inclinación)
      └─> GrafoUtils.calcular_factor_tiempo_desplazamiento() (ajuste por seguridad/luminosidad)
      └─> _interpolar_movimiento()
          └─> Calcula tiempo de movimiento
          └─> Interpola posición entre nodos
          └─> Actualiza coordenadas del ciclista
          └─> Guarda trayectoria (cada 5 puntos)
  └─> Cuando completa ruta:
      └─> estado = 'completado'
      └─> Calcula tiempo total de viaje
```

### 6. Visualización en Tiempo Real

```
Bucle de actualización (cada 50ms)
  └─> PanelVisualizacion.actualizar()
      └─> SimuladorCiclorutas.obtener_ciclistas_activos()
          └─> Filtra solo ciclistas activos (no completados)
          └─> Retorna coordenadas, colores, rutas
      └─> Limpia gráfico anterior
      └─> Dibuja grafo (nx.draw())
      └─> Dibuja ciclistas (scatter plot)
      └─> Dibuja trayectorias (líneas)
      └─> Actualiza matplotlib canvas
```

### 7. Actualización de Estadísticas

```
Bucle de actualización (cada 100ms)
  └─> PanelEstadisticas.actualizar()
      └─> SimuladorCiclorutas.obtener_estadisticas_tiempo_real()
          └─> EstadisticasUtils.calcular_estadisticas_tiempo_real()
              └─> Calcula ciclistas activos
              └─> Calcula velocidades (promedio, min, max)
              └─> Calcula rutas utilizadas
              └─> Calcula tiempo de simulación
      └─> Actualiza labels en el panel
```

---

## 📊 Carga de Archivos Excel

### Formato Requerido

El sistema carga datos desde archivos Excel (`.xlsx` o `.xls`) con estructura específica.

#### Hoja "NODOS" (Obligatoria)

| Columna | Descripción | Obligatorio |
|---------|-------------|-------------|
| `NODO` | Identificador del nodo (ej: "A", "B", "Nodo1") | ✅ |
| `ID` | ID numérico del nodo | ⚠️ Opcional |
| `NOMBRE` | Nombre descriptivo | ⚠️ Opcional |
| `LAT` | Latitud (coordenada geográfica) | ⚠️ Opcional |
| `LON` | Longitud (coordenada geográfica) | ⚠️ Opcional |

**Nota**: Si existen `LAT` y `LON`, el sistema:
- Calcula distancias euclidianas automáticamente usando fórmula de Haversine
- Ignora la columna `DISTANCIA` de ARCOS (si existe)

#### Hoja "ARCOS" (Obligatoria)

| Columna | Descripción | Obligatorio |
|---------|-------------|-------------|
| `ORIGEN` | Nodo de origen | ✅ |
| `DESTINO` | Nodo de destino | ✅ |
| `DISTANCIA` | Distancia en metros | ✅* |
| `INCLINACION` | Inclinación en porcentaje | ⚠️ Opcional |
| `SEGURIDAD` | Nivel de seguridad (1-10) | ⚠️ Opcional |
| `LUMINOSIDAD` | Nivel de luminosidad (1-10) | ⚠️ Opcional |
| Otros atributos | Cualquier otro atributo numérico | ⚠️ Opcional |

*Obligatorio solo si no hay coordenadas LAT/LON en NODOS

**Procesamiento de ARCOS**:
1. Se cargan todos los atributos dinámicamente
2. Se normalizan a minúsculas para consistencia interna
3. Se calcula `distancia_real` (igual a DISTANCIA original)
4. Se preparan para cálculo dinámico de pesos por perfil

#### Hoja "PERFILES" (Opcional)

| Columna | Descripción | Obligatorio |
|---------|-------------|-------------|
| `PERFILES` | ID del perfil (1, 2, 3, ...) | ✅ |
| `PROBABILIDAD` | Probabilidad de selección (0.0-1.0) | ✅ |
| Atributos dinámicos | Pesos para cada atributo (distancia, seguridad, etc.) | ⚠️ Opcional |

**Validación**:
- Las probabilidades deben sumar 1.0 (con tolerancia de 0.01)
- Los atributos deben coincidir con los de ARCOS

**Ejemplo**:
```
PERFILES | PROBABILIDAD | DISTANCIA | SEGURIDAD | LUMINOSIDAD | INCLINACION
---------|--------------|-----------|-----------|-------------|-------------
1        | 0.4          | 0.4       | 0.3       | 0.2         | 0.1
2        | 0.3          | 0.2       | 0.5       | 0.2         | 0.1
3        | 0.3          | 0.3       | 0.2       | 0.3         | 0.2
```

#### Hoja "RUTAS" (Opcional)

Matriz de probabilidades de destino por nodo origen.

| Columna | Descripción |
|---------|-------------|
| `NODO` | Nodo de origen |
| Nodos destino | Columnas con nombres de nodos destino (probabilidades) |

**Ejemplo**:
```
NODO | A    | B    | C    | D
-----|------|------|------|------
A    | 0.0  | 0.5  | 0.3  | 0.2
B    | 0.4  | 0.0  | 0.4  | 0.2
C    | 0.3  | 0.3  | 0.0  | 0.4
D    | 0.25 | 0.25 | 0.25 | 0.0
```

**Validación**:
- Cada fila debe sumar 1.0 (probabilidades normalizadas)
- Los nodos destino deben existir en la hoja NODOS

### Proceso de Carga

1. **Validación**:
   ```python
   ArchivoUtils.validar_archivo_excel()
   - Verifica existencia del archivo
   - Verifica hojas obligatorias (NODOS, ARCOS)
   - Verifica columnas requeridas
   - Valida probabilidades en PERFILES (si existe)
   ```

2. **Lectura de Datos**:
   ```python
   # Lee cada hoja
   nodos_df = pd.read_excel(archivo, sheet_name="NODOS")
   arcos_df = pd.read_excel(archivo, sheet_name="ARCOS")
   perfiles_df = pd.read_excel(archivo, sheet_name="PERFILES")  # Opcional
   rutas_df = pd.read_excel(archivo, sheet_name="RUTAS")  # Opcional
   ```

3. **Creación del Grafo**:
   ```python
   G = nx.Graph()
   # Agregar nodos
   for nodo in nodos_df['NODO']:
       G.add_node(nodo)
   
   # Agregar arcos con atributos
   for _, fila in arcos_df.iterrows():
       atributos = {col.lower(): fila[col] for col in arcos_df.columns 
                   if col not in ['ORIGEN', 'DESTINO']}
       G.add_edge(fila['ORIGEN'], fila['DESTINO'], **atributos)
   ```

4. **Cálculo de Coordenadas**:
   ```python
   # Si hay LAT/LON
   if tiene_lat_lon:
       # Calcular distancias euclidianas usando Haversine
       for arco in arcos_df:
           distancia = calcular_distancia_euclidiana(lat1, lon1, lat2, lon2)
           # Reemplazar DISTANCIA calculada
   ```

5. **Configuración en Simulador**:
   ```python
   simulador.configurar_grafo(grafo, posiciones, perfiles_df, rutas_df)
   - Pre-calcula rangos de atributos
   - Inicializa distribuciones por defecto
   - Pre-calcula rutas por perfil
   ```

---

## 🎨 Sistema de Visualización

### Componente Principal

**PanelVisualizacion** (`Interfaz/panels/panel_visualizacion.py`)

### Tecnologías

- **matplotlib**: Biblioteca para visualización
- **NetworkX**: Dibujo de grafos
- **Tkinter**: Integración con interfaz

### Proceso de Visualización

1. **Inicialización**:
   ```python
   self.fig, self.ax = plt.subplots(figsize=(10, 6))
   self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
   ```

2. **Dibujo del Grafo**:
   ```python
   # Dibujar grafo base
   nx.draw(self.grafo, self.pos_grafo, ax=self.ax,
           node_color='lightblue',
           node_size=500,
           with_labels=True,
           font_size=10)
   ```

3. **Actualización de Ciclistas**:
   ```python
   # Obtener ciclistas activos
   ciclistas = self.simulador.obtener_ciclistas_activos()
   
   # Dibujar ciclistas
   for coords, color in zip(ciclistas['coordenadas'], ciclistas['colores']):
       self.ax.scatter(coords[0], coords[1], c=color, s=120, alpha=0.95)
   ```

4. **Actualización en Tiempo Real**:
   ```python
   # Cada 50ms (configurable)
   def actualizar():
       self.ax.clear()
       self._dibujar_grafo()
       self._dibujar_ciclistas()
       self.canvas.draw()
   ```

### Características

- **Colores Dinámicos**: Cada nodo tiene un color asignado; los ciclistas heredan el color del nodo origen
- **Trayectorias**: Se muestran las últimas posiciones de cada ciclista
- **Actualización Suave**: Usa matplotlib animation para actualización fluida

---

## 🎲 Generación de Simulaciones

### Inicialización

Cuando el usuario hace clic en "NUEVA":

```python
simulador.inicializar_simulacion()
```

**Pasos**:
1. Limpia datos de simulación anterior
2. Crea nuevo entorno SimPy (`simpy.Environment()`)
3. Inicializa contadores (ciclista_id_counter = 0)
4. Crea procesos SimPy:
   - `_generador_ciclistas_realista()`: Genera nuevos ciclistas
   - `_detener_por_tiempo()`: Detiene simulación al finalizar tiempo

### Generación de Ciclistas

**Proceso**: `_generador_ciclistas_realista()`

**Algoritmo**:
```python
while estado != "completada":
    1. Seleccionar nodo origen (_seleccionar_nodo_origen)
       - Usa distribuciones configuradas
       - Selecciona basado en tasas de arribo (lambda)
    
    2. Generar tiempo de arribo
       - distribucion.generar_tiempo_arribo(nodo_origen)
       - Espera ese tiempo (yield env.timeout())
    
    3. Asignar ruta (_asignar_ruta_desde_nodo)
       - Seleccionar perfil (_seleccionar_perfil_ciclista)
       - Seleccionar destino (_seleccionar_destino)
       - Calcular ruta óptima (RutasUtils.calcular_ruta_optima)
    
    4. Crear proceso de ciclista
       - Crear proceso SimPy _ciclista()
       - Registrar en listas (coordenadas, rutas, colores)
```

### Asignación de Rutas

**Proceso**: `_asignar_ruta_desde_nodo()`

**Algoritmo**:
1. **Selección de Perfil**:
   ```python
   _seleccionar_perfil_ciclista()
   - Si hay hoja PERFILES: selecciona basado en probabilidades
   - Si no hay PERFILES: usa perfil por defecto (solo distancia)
   ```

2. **Selección de Destino**:
   ```python
   _seleccionar_destino(nodo_origen)
   - Si hay hoja RUTAS: usa probabilidades de la matriz
   - Si no hay RUTAS: selección aleatoria uniforme
   ```

3. **Cálculo de Ruta**:
   ```python
   RutasUtils.calcular_ruta_optima()
   - Pre-calcula pesos compuestos por arco
   - Usa algoritmo Dijkstra con pesos compuestos
   - Retorna lista de nodos (ruta completa)
   ```

### Movimiento de Ciclistas

**Proceso**: `_ciclista()`

**Algoritmo**:
```python
1. Obtener ruta asignada (lista de nodos: [A, B, C, D])

2. Para cada segmento de la ruta:
   a. Obtener coordenadas de nodos
   b. Obtener distancia real del arco
   c. Obtener atributos del arco
   d. Calcular velocidad ajustada (por inclinación)
   e. Calcular factor de tiempo (por seguridad/luminosidad)
   f. Interpolar movimiento suave
      - Calcula tiempo de movimiento
      - Interpola posición entre nodos
      - Actualiza coordenadas cada 0.5s

3. Cuando completa ruta:
   - estado = 'completado'
   - Calcular tiempo total de viaje
   - Mover fuera de vista
```

---

## 📅 Sistema de Eventos y Calendario

### Motor de Simulación: SimPy

El sistema usa **SimPy** (Simulation in Python) para simulación de eventos discretos.

### Conceptos Clave

1. **Environment (Entorno)**: `simpy.Environment`
   - Mantiene el tiempo de simulación
   - Gestiona el calendario de eventos
   - Procesa eventos en orden temporal

2. **Process (Proceso)**: Funciones generadoras (`yield`)
   - Representan actividades que toman tiempo
   - Usan `yield env.timeout()` para esperar tiempo

3. **Event**: Instancia en el calendario de eventos
   - Tiempo: cuándo ocurrirá
   - Proceso: qué proceso se ejecutará

### Calendario de Eventos

El calendario se gestiona automáticamente por SimPy:

```python
env = simpy.Environment()  # Inicializa calendario vacío

# Agregar proceso al calendario
env.process(generador_ciclistas())  # Evento inicial

# Avanzar tiempo
env.step()  # Procesa próximo evento
```

### Tipos de Eventos en el Sistema

#### 1. Eventos de Arribo de Ciclistas

**Proceso**: `_generador_ciclistas_realista()`

**Cómo funciona**:
```python
def _generador_ciclistas_realista():
    while estado != "completada":
        # Seleccionar nodo origen
        nodo_origen = seleccionar_nodo_origen()
        
        # Generar tiempo de arribo (evento futuro)
        tiempo_arribo = distribucion.generar_tiempo_arribo(nodo_origen)
        
        # Esperar tiempo (agrega evento al calendario)
        yield env.timeout(tiempo_arribo)  # Evento: arribo de ciclista
        
        # Crear nuevo ciclista (evento inmediato)
        crear_ciclista(nodo_origen)
```

**Eventos generados**:
- `env.timeout(tiempo_arribo)`: Evento de arribo futuro
- Creación de proceso `_ciclista()`: Evento de inicio de viaje

#### 2. Eventos de Movimiento

**Proceso**: `_ciclista()` y `_interpolar_movimiento()`

**Cómo funciona**:
```python
def _ciclista(id, velocidad):
    ruta = obtener_ruta(id)  # [A, B, C, D]
    
    for i in range(len(ruta) - 1):
        origen = ruta[i]
        destino = ruta[i + 1]
        
        # Calcular tiempo de movimiento
        distancia = obtener_distancia_arco(origen, destino)
        tiempo = distancia / velocidad_ajustada
        
        # Interpolar movimiento (eventos cada 0.5s)
        yield from _interpolar_movimiento(origen, destino, tiempo)
```

**Eventos generados**:
- `env.timeout(0.5)`: Actualización de posición cada 0.5 segundos
- Finalización de tramo: Evento de llegada a nodo intermedio
- Finalización de ruta: Evento de completación de viaje

#### 3. Eventos de Detención

**Proceso**: `_detener_por_tiempo()`

**Cómo funciona**:
```python
def _detener_por_tiempo():
    # Esperar duración completa de simulación
    yield env.timeout(duracion_simulacion)
    
    # Evento: finalización de simulación
    estado = "completada"
    generar_resultados_excel()
```

**Eventos generados**:
- `env.timeout(duracion_simulacion)`: Evento de finalización

### Definición de Eventos

Los eventos se definen implícitamente mediante:

1. **`yield env.timeout(tiempo)`**: Crea evento futuro
   ```python
   yield env.timeout(5.0)  # Evento en t+5 segundos
   ```

2. **`env.process(función())`**: Crea proceso (evento inicial)
   ```python
   env.process(_generador_ciclistas_realista())  # Evento en t=0
   ```

3. **`yield from`**: Delega a otro proceso
   ```python
   yield from _interpolar_movimiento(...)  # Eventos anidados
   ```

### Gestión del Calendario

SimPy gestiona automáticamente:
- Ordenamiento temporal de eventos
- Ejecución en orden cronológico
- Gestión de eventos concurrentes (mismo tiempo)

**Ejemplo de calendario**:
```
Tiempo | Evento
-------|------------------------
0.0    | Inicio: generador_ciclistas
0.0    | Inicio: detener_por_tiempo
2.5    | Arribo: ciclista #1 en nodo A
5.0    | Arribo: ciclista #2 en nodo B
7.5    | Movimiento: ciclista #1 de A→B (actualización posición)
10.0   | Completación: ciclista #1 llega a B
...
300.0  | Finalización: tiempo de simulación
```

---

## 🎭 Patrones de Diseño

### 1. MVC (Model-View-Controller)

- **Model**: `SimuladorCiclorutas`, `Ciclista`, `Grafo`
- **View**: Paneles de la interfaz (`PanelControl`, `PanelVisualizacion`, etc.)
- **Controller**: `InterfazSimulacion` (coordina modelo y vista)

### 2. Observer Pattern

- Los paneles observan cambios en el simulador
- Actualización automática cuando cambia el estado

### 3. Factory Pattern

- Creación de distribuciones (`DistribucionNodo`)
- Creación de perfiles de ciclistas

### 4. Singleton Pattern

- Configuración centralizada (`config.py`)
- Gestión de recursos compartidos

### 5. Pool Pattern

- Reutilización de objetos `Ciclista` (`PoolCiclistas`)
- Gestión eficiente de memoria

---

## 🔌 Extensibilidad

### Agregar Nuevas Distribuciones

1. Crear clase en `Simulador/distributions/distribucion_nodo.py`:
```python
class DistribucionNueva(DistribucionBase):
    def _validar_parametros(self):
        # Validar parámetros específicos
    
    def generar_tiempo_arribo(self):
        # Implementar generación
```

2. Registrar en `DistribucionNodo._crear_distribucion()`:
```python
if tipo == 'nueva':
    return DistribucionNueva(parametros)
```

### Agregar Nuevos Atributos

1. Agregar columna en hoja ARCOS del Excel
2. El sistema detecta automáticamente atributos nuevos
3. Se pueden usar en perfiles (hoja PERFILES)

### Agregar Nuevos Paneles

1. Crear clase en `Interfaz/panels/`:
```python
class PanelNuevo:
    def __init__(self, parent, simulador):
        # Inicializar panel
```

2. Agregar a `InterfazSimulacion`:
```python
self.panel_nuevo = PanelNuevo(self.frame, self.simulador)
```

### Modificar Algoritmo de Rutas

1. Modificar `RutasUtils.calcular_ruta_optima()`
2. Cambiar función de peso en `_calcular_pesos_compuestos()`
3. Cambiar algoritmo (Dijkstra → A*, etc.)

---

## 📚 Referencias

- **SimPy Documentation**: https://simpy.readthedocs.io/
- **NetworkX Documentation**: https://networkx.org/
- **matplotlib Documentation**: https://matplotlib.org/
- **Python Style Guide (PEP 8)**: https://pep8.org/

---

Este documento proporciona una visión completa de la arquitectura del sistema. Para detalles específicos del modelo de simulación, consulte **README_MODELO_SIMULACION.md**.

