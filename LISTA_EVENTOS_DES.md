# 📅 LISTA DE EVENTOS DEL SISTEMA DES (SimPy)

## 🎯 Resumen

Este documento lista todos los eventos que se generan en el calendario de SimPy durante la simulación de ciclorutas. El sistema funciona como un **calendario de eventos discretos** donde cada evento tiene un tiempo específico y se procesa en orden cronológico.

---

## 📋 CATEGORÍAS DE EVENTOS

### 1️⃣ EVENTOS DE INICIALIZACIÓN

| Evento | Tiempo | Proceso | Descripción |
|--------|--------|---------|-------------|
| **Inicio de Simulación** | `0.0` | `inicializar_simulacion()` | Se crea el entorno SimPy (`simpy.Environment()`) |
| **Inicio Generador de Ciclistas** | `0.0` | `_generador_ciclistas_realista()` | Se inicia el proceso que genera ciclistas |
| **Inicio Contador de Tiempo** | `0.0` | `_detener_por_tiempo()` | Se inicia el proceso que detiene la simulación al final |

---

### 2️⃣ EVENTOS DE ARRIBO DE CICLISTAS

Estos eventos se generan según las distribuciones de probabilidad configuradas para cada nodo.

| Evento | Tiempo | Proceso | Descripción |
|--------|--------|---------|-------------|
| **Arribo a Nodo Origen** | `t = distribucion.generar_tiempo_arribo(nodo)` | `_generador_ciclistas_por_nodo()` | Un nuevo ciclista arriba a un nodo origen específico |
| **Creación de Ciclista** | `t` (mismo tiempo) | `_generador_ciclistas_por_nodo()` | Se crea el objeto ciclista con ID único |
| **Inicio de Proceso de Ciclista** | `t` (mismo tiempo) | `_ciclista()` | Se inicia el proceso de movimiento del ciclista |

**Distribuciones que generan estos eventos:**
- **Exponencial**: `lambda` (tasa de arribo)
- **Normal**: `media`, `desviacion`
- **Log-Normal**: `mu`, `sigma`
- **Gamma**: `forma`, `escala`
- **Weibull**: `forma`, `escala`

**Ejemplo:**
```
Tiempo: 5.2 segundos
Evento: Arribo de ciclista #15 al nodo A
Acción: Crear proceso _ciclista() para ciclista #15
```

---

### 3️⃣ EVENTOS DE DECISIÓN

Estos eventos ocurren cuando se toman decisiones sobre el comportamiento del ciclista.

| Evento | Tiempo | Proceso | Descripción |
|--------|--------|---------|-------------|
| **Selección de Perfil** | `t` (al crear ciclista) | `_seleccionar_perfil_ciclista()` | Se decide qué tipo de ciclista será (basado en probabilidades de PERFILES) |
| **Selección de Destino** | `t` (al crear ciclista) | `_seleccionar_destino()` | Se decide a qué nodo va el ciclista (basado en matriz RUTAS) |
| **Cálculo de Ruta Óptima** | `t` (al crear ciclista) | `RutasUtils.calcular_ruta_optima()` | Se calcula la ruta óptima según preferencias del perfil |

**Algoritmo de Decisión:**
1. Seleccionar perfil basado en probabilidades de la tabla PERFILES
2. Seleccionar destino basado en probabilidades de la matriz RUTAS
3. Calcular ruta óptima usando algoritmo de caminos cortos ponderados

---

### 4️⃣ EVENTOS DE MOVIMIENTO

Estos eventos actualizan la posición de los ciclistas en el tiempo.

| Evento | Tiempo | Proceso | Descripción |
|--------|--------|---------|-------------|
| **Actualización de Posición** | `t + 0.5 * paso` | `_interpolar_movimiento()` | Actualización de coordenadas cada 0.5 segundos |
| **Entrada a Arco** | `t_entrada` | `_interpolar_movimiento()` | Ciclista entra a un arco/tramo específico |
| **Recálculo de Factor de Densidad** | `t + 25% del tiempo del tramo` | `_interpolar_movimiento()` | Se recalcula el factor de densidad cada 25% del recorrido |
| **Salida de Arco** | `t_salida` | `_interpolar_movimiento()` | Ciclista sale de un arco/tramo específico |
| **Llegada a Nodo Intermedio** | `t_llegada` | `_ciclista_grafo_real()` | Ciclista llega a un nodo intermedio de su ruta |
| **Inicio de Nuevo Tramo** | `t_llegada` (mismo tiempo) | `_ciclista_grafo_real()` | Ciclista inicia el siguiente tramo de su ruta |

**Frecuencia de Actualización:**
- Cada **0.5 segundos** se actualiza la posición
- Máximo **200 pasos** por tramo (para eficiencia)

**Ejemplo:**
```
Tiempo: 7.5 segundos
Evento: Actualización de posición de ciclista #10
Acción: Mover de posición (10.2, 5.3) a (10.5, 5.4)
```

---

### 5️⃣ EVENTOS DE ESTADO DE ARCOS

Estos eventos rastrean la ocupación y uso de los arcos/tramos.

| Evento | Tiempo | Proceso | Descripción |
|--------|--------|---------|-------------|
| **Registro de Entrada a Arco** | `t_entrada` | `_interpolar_movimiento()` | Se registra que un ciclista entró a un arco |
| **Registro de Salida de Arco** | `t_salida` | `_interpolar_movimiento()` | Se registra que un ciclista salió de un arco |
| **Actualización de Ocupación** | `t` (cada actualización) | `_calcular_factor_densidad()` | Se actualiza el número de bicicletas en un arco |

**Datos Registrados:**
- `eventos_arcos`: Lista de tuplas `(tiempo, arco_str, tipo_evento, ciclista_id)`
- `bicicletas_en_arco`: Conjunto de ciclistas activos en cada arco
- `ocupacion_arcos_tiempo`: Historial de ocupación a lo largo del tiempo

---

### 6️⃣ EVENTOS DE FINALIZACIÓN

Estos eventos marcan el fin de actividades o la simulación completa.

| Evento | Tiempo | Proceso | Descripción |
|--------|--------|---------|-------------|
| **Finalización de Viaje** | `t_final` | `_ciclista_grafo_real()` | Ciclista completa su ruta y llega al destino |
| **Cálculo de Tiempo Total** | `t_final` (mismo tiempo) | `_ciclista_grafo_real()` | Se calcula el tiempo total de viaje |
| **Marcado como Completado** | `t_final` (mismo tiempo) | `_ciclista_grafo_real()` | Se marca el ciclista como `'completado'` |
| **Finalización de Simulación** | `duracion_simulacion` | `_detener_por_tiempo()` | Se cumple el tiempo máximo configurado |
| **Generación de Excel** | `duracion_simulacion` (mismo tiempo) | `_generar_resultados_excel()` | Se genera el archivo Excel con resultados |

**Ejemplo:**
```
Tiempo: 12.8 segundos
Evento: Finalización de viaje de ciclista #1
Acción: Ciclista #1 completa viaje, se calcula tiempo total, se marca como completado
```

---

### 7️⃣ EVENTOS DE GESTIÓN DE MEMORIA

Estos eventos optimizan el uso de memoria durante la simulación.

| Evento | Tiempo | Proceso | Descripción |
|--------|--------|---------|-------------|
| **Limpieza de Ciclistas Antiguos** | `t % 10 == 0` | `_gestionar_memoria_inteligente()` | Cada 10 segundos se limpian ciclistas completados |
| **Reinicio de Pool** | `t` (cuando se requiere) | `PoolCiclistas.reiniciar_pool()` | Se reinicia el pool de objetos ciclista |

---

## 📊 EJEMPLO DE CALENDARIO DE EVENTOS

```
Calendario de Eventos (cola prioritaria ordenada por tiempo)

Tiempo | Tipo de Evento           | Proceso              | Descripción
-------|--------------------------|----------------------|-----------------------------
0.0    | Inicio                   | generador_ciclistas  | Inicia generación de ciclistas
0.0    | Inicio                   | detener_por_tiempo   | Inicia contador de tiempo
2.3    | Arribo                   | generador_nodo_A     | Arribo ciclista #1 a nodo A
2.3    | Decisión                 | ciclista_1           | Selección de perfil y destino
2.3    | Decisión                 | ciclista_1           | Cálculo de ruta óptima
2.3    | Inicio Viaje             | ciclista_1           | Ciclista #1 inicia viaje A→C
2.3    | Entrada a Arco           | ciclista_1           | Ciclista #1 entra a arco A→B
2.8    | Movimiento               | ciclista_1           | Actualización posición #1
3.3    | Movimiento               | ciclista_1           | Actualización posición #2
3.8    | Movimiento               | ciclista_1           | Actualización posición #3
4.7    | Arribo                   | generador_nodo_B     | Arribo ciclista #2 a nodo B
4.7    | Decisión                 | ciclista_2           | Selección de perfil y destino
4.7    | Inicio Viaje             | ciclista_2           | Ciclista #2 inicia viaje B→D
5.1    | Movimiento               | ciclista_1           | Actualización posición #4
5.6    | Movimiento               | ciclista_1           | Actualización posición #5
6.1    | Movimiento               | ciclista_1           | Actualización posición #6
6.6    | Movimiento               | ciclista_1           | Actualización posición #7
7.1    | Movimiento               | ciclista_1           | Actualización posición #8
7.5    | Movimiento               | ciclista_1           | Actualización posición #9
8.0    | Llegada a Nodo           | ciclista_1           | Ciclista #1 llega a nodo B
8.0    | Salida de Arco           | ciclista_1           | Ciclista #1 sale de arco A→B
8.0    | Inicio Tramo             | ciclista_1           | Ciclista #1 inicia tramo B→C
8.0    | Entrada a Arco           | ciclista_1           | Ciclista #1 entra a arco B→C
10.0   | Limpieza Memoria         | gestionar_memoria    | Limpieza de ciclistas antiguos
12.8   | Finalización Viaje       | ciclista_1           | Ciclista #1 completa viaje
12.8   | Cálculo Tiempo Total     | ciclista_1           | Tiempo total: 10.5 segundos
12.8   | Marcado Completado       | ciclista_1           | Ciclista #1 marcado como completado
15.3   | Arribo                   | generador_nodo_A     | Arribo ciclista #3 a nodo A
...    | ...                      | ...                  | ...
300.0  | Finalización             | detener_por_tiempo   | Simulación completa
300.0  | Generación Excel         | generar_excel        | Archivo Excel generado
```

---

## 🔄 FLUJO DE EVENTOS POR CICLISTA

```
1. EVENTO DE ARRIBO (t_arribo)
   └─> Generado por distribución de probabilidad del nodo
   
2. EVENTOS DE DECISIÓN (t_arribo, mismo tiempo)
   ├─> Selección de perfil
   ├─> Selección de destino
   └─> Cálculo de ruta óptima
   
3. EVENTO DE INICIO DE VIAJE (t_arribo, mismo tiempo)
   └─> Se inicia el proceso de movimiento
   
4. EVENTOS DE MOVIMIENTO (t_arribo + 0.5 * paso)
   ├─> Entrada a arco (t_entrada)
   ├─> Actualización de posición cada 0.5s
   ├─> Recálculo de factor de densidad (cada 25% del tramo)
   └─> Salida de arco (t_salida)
   
5. EVENTOS DE LLEGADA A NODOS INTERMEDIOS (t_llegada)
   ├─> Llegada a nodo intermedio
   └─> Inicio de nuevo tramo
   
6. EVENTO DE FINALIZACIÓN (t_final)
   ├─> Finalización de viaje
   ├─> Cálculo de tiempo total
   └─> Marcado como completado
```

---

## 📈 ESTADÍSTICAS DE EVENTOS

### Eventos por Categoría

| Categoría | Frecuencia | Descripción |
|-----------|------------|-------------|
| **Arribos** | Variable (según distribuciones) | Depende de la tasa de arribo (lambda) de cada nodo |
| **Movimientos** | Cada 0.5 segundos por ciclista activo | Actualizaciones de posición |
| **Decisiones** | 1 por ciclista | Al momento de crear el ciclista |
| **Finalizaciones** | 1 por ciclista | Al completar su viaje |
| **Gestión de Memoria** | Cada 10 segundos | Limpieza automática |

### Eventos Totales Estimados

Para una simulación de **300 segundos** con **5 nodos** y **lambda promedio de 0.5**:

- **Arribos**: ~750 eventos (5 nodos × 0.5 arribos/seg × 300 seg)
- **Movimientos**: ~150,000 eventos (750 ciclistas × 200 pasos promedio)
- **Decisiones**: ~750 eventos (1 por ciclista)
- **Finalizaciones**: ~750 eventos (1 por ciclista)
- **Gestión de Memoria**: ~30 eventos (cada 10 segundos)

**Total estimado**: ~153,280 eventos

---

## 🎯 NOTAS IMPORTANTES

1. **Ordenamiento Temporal**: Todos los eventos se procesan en orden cronológico estricto
2. **Eventos Simultáneos**: Si múltiples eventos ocurren al mismo tiempo, se procesan en orden de creación
3. **Eficiencia**: El sistema limita los pasos de movimiento a máximo 200 por tramo
4. **Memoria**: Se limpia automáticamente cada 10 segundos para optimizar recursos
5. **Rastreo**: Todos los eventos de arcos se registran para análisis posterior

---

## 📝 REFERENCIAS

- **Archivo Principal**: `Simulador/core/simulador.py`
- **Documentación del Modelo**: `README_MODELO_SIMULACION.md`
- **Documentación de Arquitectura**: `README_ARQUITECTURA.md`
- **Framework**: SimPy (Simulation in Python)

---

**Generado automáticamente para el Sistema de Simulación de Ciclorutas v2.0**


