# 🎲 Modelo de Simulación - Simulador de Ciclorutas

## 📋 Tabla de Contenidos

- [Visión General del Modelo](#visión-general-del-modelo)
- [Tipo de Simulación](#tipo-de-simulación)
- [Entidades del Modelo](#entidades-del-modelo)
- [Eventos del Modelo](#eventos-del-modelo)
- [Calendario de Eventos](#calendario-de-eventos)
- [Mecánica de Decisión](#mecánica-de-decisión)
- [Gestión del Tiempo](#gestión-del-tiempo)
- [Estado del Sistema](#estado-del-sistema)
- [Flujo de Ejecución](#flujo-de-ejecución)
- [Limitaciones y Supuestos](#limitaciones-y-supuestos)

---

## 🎯 Visión General del Modelo

El modelo de simulación implementa un **sistema de eventos discretos** para simular el comportamiento de ciclistas en una red de ciclorutas. El modelo se basa en:

- **Simulación de eventos discretos (DES)**: Los eventos ocurren en instantes específicos de tiempo
- **Modelo estocástico**: Incorpora incertidumbre mediante distribuciones de probabilidad
- **Modelo basado en agentes**: Cada ciclista es una entidad independiente con comportamiento propio

### Objetivo del Modelo

Simular el movimiento de ciclistas a través de una red de ciclorutas considerando:
- Tiempos de arribo estocásticos por nodo
- Selección de rutas basada en preferencias de ciclistas
- Ajuste de velocidad por características del camino
- Tiempo de desplazamiento afectado por seguridad e iluminación

---

## 📊 Tipo de Simulación

### Simulación de Eventos Discretos (DES)

El modelo utiliza **SimPy** (Simulation in Python), un framework para simulación de eventos discretos.

**Características**:
- El tiempo avanza en pasos discretos (eventos)
- No hay tiempo continuo entre eventos
- Los eventos ocurren en instantes específicos
- El sistema procesa eventos en orden cronológico

**Ventajas**:
- Eficiente para simulaciones de larga duración
- Manejo natural de colas y procesos
- Modelado intuitivo de sistemas complejos

### Comparación con Otros Tipos

| Aspecto | Eventos Discretos | Simulación Continua |
|---------|-------------------|---------------------|
| Tiempo | Discreto (eventos) | Continuo |
| Estado | Cambia en eventos | Cambia continuamente |
| Uso | Sistemas con eventos puntuales | Sistemas físicos continuos |
| Eficiencia | Muy eficiente | Menos eficiente |

**Este modelo usa Eventos Discretos** porque:
- Los arribos de ciclistas son eventos puntuales
- El movimiento puede discretizarse en pasos
- Es más eficiente computacionalmente

---

## 👥 Entidades del Modelo

### 1. Ciclista

**Descripción**: Entidad individual que representa un ciclista en la red.

**Atributos**:
```python
{
    'id': int,                    # Identificador único
    'coordenadas': (float, float), # Posición actual (x, y)
    'trayectoria': List[(x, y)],  # Historial de posiciones
    'velocidad': float,            # Velocidad actual (m/s)
    'estado': str,                 # 'inactivo' | 'activo' | 'completado'
    'ruta': List[str],             # Secuencia de nodos [A, B, C, D]
    'color': str,                  # Color para visualización
    'perfil': Dict,                # Perfil de preferencias del ciclista
    'nodo_origen': str,            # Nodo donde inicia el viaje
    'nodo_destino': str,           # Nodo destino final
    'tiempo_inicio_viaje': float,  # Tiempo de simulación cuando inicia
    'tiempo_total_viaje': float,   # Duración total del viaje
    'tiempos_por_tramo': List[float] # Tiempo gastado en cada tramo
}
```

**Estados del Ciclista**:
- **Inactivo**: Ciclista creado pero aún no iniciado
- **Activo**: Ciclista en movimiento en la red
- **Completado**: Ciclista terminó su viaje

**Ciclo de Vida**:
```
Creación → Estado: 'inactivo'
    ↓
Inicio de viaje → Estado: 'activo'
    ↓
Movimiento por ruta
    ↓
Llegada a destino → Estado: 'completado'
```

### 2. Nodo

**Descripción**: Punto en la red donde los ciclistas pueden iniciar o terminar viajes.

**Atributos**:
```python
{
    'id': str,                     # Identificador (ej: "A", "Nodo1")
    'nombre': str,                  # Nombre descriptivo
    'coordenadas': (float, float), # Posición en el grafo
    'distribucion_arribo': DistribucionNodo,  # Distribución de tiempos entre arribos
    'tasa_arribo': float,          # Tasa promedio de arribos (lambda)
    'probabilidades_destino': Dict[str, float]  # Probabilidades de destino por nodo
}
```

**Funciones**:
- Generar ciclistas según distribución de arribo
- Servir como origen o destino de viajes
- Mantener estadísticas de arribos

### 3. Arco (Tramo)

**Descripción**: Conexión entre dos nodos con atributos físicos.

**Atributos**:
```python
{
    'origen': str,                  # Nodo de origen
    'destino': str,                 # Nodo de destino
    'distancia': float,             # Distancia real en metros
    'distancia_real': float,        # Distancia para cálculo de tiempo
    'inclinacion': float,           # Inclinación en porcentaje (-50% a +50%)
    'seguridad': float,             # Nivel de seguridad (1-10)
    'luminosidad': float,           # Nivel de luminosidad (1-10)
    'weight': float                 # Peso compuesto para cálculo de ruta
}
```

**Efectos en el Modelo**:
- **Distancia**: Determina tiempo base de desplazamiento
- **Inclinación**: Afecta velocidad del ciclista
- **Seguridad**: Afecta tiempo de desplazamiento (factor multiplicador)
- **Luminosidad**: Afecta tiempo de desplazamiento (factor multiplicador)

### 4. Perfil de Ciclista

**Descripción**: Preferencias de un tipo de ciclista para seleccionar rutas.

**Atributos**:
```python
{
    'id': int,                      # ID del perfil (1, 2, 3, ...)
    'probabilidad': float,          # Probabilidad de selección (0.0-1.0)
    'pesos': {                       # Pesos para atributos
        'distancia': float,          # Importancia de distancia (0.0-1.0)
        'seguridad': float,          # Importancia de seguridad (0.0-1.0)
        'luminosidad': float,        # Importancia de luminosidad (0.0-1.0)
        'inclinacion': float,        # Importancia de inclinación (0.0-1.0)
        ...
    }
}
```

**Uso**:
- Selección aleatoria basada en probabilidad
- Cálculo de pesos compuestos para rutas
- Normalización: suma de pesos debe ser 1.0

**Ejemplo**:
```python
perfil_1 = {
    'id': 1,
    'probabilidad': 0.4,
    'pesos': {
        'distancia': 0.4,      # Prioriza distancia corta
        'seguridad': 0.3,      # Importante pero secundario
        'luminosidad': 0.2,    # Menos importante
        'inclinacion': 0.1     # Poco importante
    }
}
```

### 5. Red (Grafo)

**Descripción**: Estructura completa de la red de ciclorutas.

**Atributos**:
```python
{
    'nodos': Set[str],              # Conjunto de nodos
    'arcos': Set[Tuple(str, str)],   # Conjunto de arcos (origen, destino)
    'atributos_arcos': Dict,         # Atributos por arco
    'posiciones': Dict[str, Tuple],  # Posiciones de nodos para visualización
    'rangos_atributos': Dict,        # Rangos min/max de atributos
    'rutas_precalculadas': Dict      # Cache de rutas por perfil
}
```

**Estructura**: Grafo no dirigido (NetworkX Graph)

---

## 📅 Eventos del Modelo

### Clasificación de Eventos

Los eventos se clasifican según su **origen** y **efecto**:

#### 1. Eventos de Arribo

**Descripción**: Eventos que marcan la llegada de un nuevo ciclista a la red.

**Tipos**:
- **Arribo a Nodo Origen**: Ciclista inicia su viaje desde un nodo
- **Arribo a Nodo Intermedio**: Ciclista llega a un nodo intermedio de su ruta
- **Arribo a Nodo Destino**: Ciclista completa su viaje

**Generación**:
```python
# Proceso: _generador_ciclistas_realista()

tiempo_arribo = distribucion.generar_tiempo_arribo(nodo_origen)
yield env.timeout(tiempo_arribo)  # Evento de arribo futuro

# Crear ciclista
ciclista = crear_ciclista(nodo_origen, destino, ruta)
```

**Distribuciones Usadas**:
- Exponencial: `lambda` (tasa de arribo)
- Normal: `media`, `desviacion`
- Log-Normal, Gamma, Weibull: configuradas por usuario

**Ejemplo**:
```
Tiempo: 5.2 segundos
Evento: Arribo de ciclista #15 al nodo A
Acción: Crear proceso _ciclista() para ciclista #15
```

#### 2. Eventos de Movimiento

**Descripción**: Eventos que marcan actualizaciones de posición de ciclistas.

**Tipos**:
- **Actualización de Posición**: Ciclista se mueve entre posiciones
- **Llegada a Nodo**: Ciclista completa un tramo de su ruta

**Generación**:
```python
# Proceso: _interpolar_movimiento()

for paso in range(pasos):
    yield env.timeout(0.5)  # Evento cada 0.5 segundos
    
    # Actualizar posición
    nueva_posicion = interpolar(origen, destino, progreso)
    coordenadas[ciclista_id] = nueva_posicion
```

**Frecuencia**: Cada 0.5 segundos (configurable)

**Ejemplo**:
```
Tiempo: 7.5 segundos
Evento: Actualización de posición de ciclista #10
Acción: Mover de posición (10.2, 5.3) a (10.5, 5.4)
```

#### 3. Eventos de Decisión

**Descripción**: Eventos donde se toman decisiones sobre rutas y destinos.

**Tipos**:
- **Selección de Perfil**: Decidir qué tipo de ciclista será
- **Selección de Destino**: Decidir a qué nodo va el ciclista
- **Cálculo de Ruta**: Decidir qué ruta seguir

**Generación**:
```python
# Proceso: _asignar_ruta_desde_nodo()

# Decisión 1: Seleccionar perfil
perfil = _seleccionar_perfil_ciclista()  # Basado en probabilidades

# Decisión 2: Seleccionar destino
destino = _seleccionar_destino(origen)  # Basado en matriz RUTAS

# Decisión 3: Calcular ruta óptima
ruta = RutasUtils.calcular_ruta_optima(grafo, origen, destino, perfil)
```

**Algoritmo de Decisión**: Ver sección [Mecánica de Decisión](#mecánica-de-decisión)

#### 4. Eventos de Finalización

**Descripción**: Eventos que marcan el fin de actividades o la simulación completa.

**Tipos**:
- **Finalización de Viaje**: Ciclista completa su ruta
- **Finalización de Simulación**: Se cumple el tiempo máximo

**Generación**:
```python
# Finalización de viaje (en _ciclista())
if ciclista_llego_a_destino:
    estado_ciclistas[id] = 'completado'
    calcular_tiempo_total_viaje()

# Finalización de simulación (en _detener_por_tiempo())
yield env.timeout(duracion_simulacion)
estado = "completada"
generar_resultados_excel()
```

---

## ⏰ Calendario de Eventos

### Gestión del Calendario

El calendario de eventos es gestionado automáticamente por **SimPy**. El entorno (`Environment`) mantiene una cola de eventos ordenada por tiempo.

### Estructura del Calendario

```
Calendario de Eventos (cola prioritaria ordenada por tiempo)

Tiempo | Tipo de Evento           | Proceso              | Descripción
-------|--------------------------|----------------------|-----------------------------
0.0    | Inicio                   | generador_ciclistas  | Inicia generación de ciclistas
0.0    | Inicio                   | detener_por_tiempo   | Inicia contador de tiempo
2.3    | Arribo                   | generador_ciclistas  | Arribo ciclista #1 a nodo A
2.3    | Inicio Viaje             | ciclista_1           | Ciclista #1 inicia viaje A→C
4.7    | Arribo                   | generador_ciclistas  | Arribo ciclista #2 a nodo B
5.1    | Movimiento               | ciclista_1           | Actualización posición #1
7.5    | Movimiento               | ciclista_1           | Actualización posición #1
10.2   | Llegada a Nodo           | ciclista_1           | Ciclista #1 llega a nodo B
10.2   | Inicio Tramo             | ciclista_1           | Ciclista #1 inicia tramo B→C
12.8   | Finalización Viaje       | ciclista_1           | Ciclista #1 completa viaje
15.3   | Arribo                   | generador_ciclistas  | Arribo ciclista #3 a nodo A
...
300.0  | Finalización             | detener_por_tiempo   | Simulación completa
```

### Ordenamiento Temporal

Los eventos se procesan en **orden cronológico estricto**:
1. SimPy ordena eventos por tiempo ascendente
2. Si múltiples eventos ocurren al mismo tiempo, se procesan en orden de creación
3. No hay procesamiento paralelo real (secuencial por diseño)

### Procesamiento de Eventos

```python
# SimPy procesa eventos así:

while calendario_no_vacio:
    evento = obtener_proximo_evento()  # Menor tiempo
    
    if evento.tipo == 'timeout':
        proceso = evento.proceso
        continuar_proceso(proceso)  # Ejecuta hasta siguiente yield
    
    tiempo_actual = evento.tiempo
```

---

## 🧠 Mecánica de Decisión

### 1. Selección de Nodo Origen

**Cuándo ocurre**: Antes de crear cada nuevo ciclista.

**Algoritmo**:
```python
def _seleccionar_nodo_origen():
    # 1. Obtener todas las distribuciones configuradas
    distribuciones = gestor_distribuciones.distribuciones
    
    # 2. Calcular tasas de arribo para cada nodo
    tasas = []
    for nodo, distribucion in distribuciones.items():
        tipo = distribucion.obtener_tipo()
        params = distribucion.obtener_parametros()
        
        if tipo == 'exponencial':
            tasa = params['lambda']
        elif tipo == 'normal':
            tasa = 1.0 / params['media']
        # ... otros tipos
        
        tasas.append(tasa)
    
    # 3. Normalizar tasas a probabilidades
    total_tasa = sum(tasas)
    probabilidades = [tasa / total_tasa for tasa in tasas]
    
    # 4. Seleccionar nodo usando distribución ponderada
    nodo_seleccionado = np.random.choice(nodos, p=probabilidades)
    
    return nodo_seleccionado
```

**Resultado**: Un nodo origen seleccionado basado en tasas de arribo relativas.

### 2. Selección de Perfil de Ciclista

**Cuándo ocurre**: Al crear un nuevo ciclista.

**Algoritmo**:
```python
def _seleccionar_perfil_ciclista():
    if perfiles_df is None:
        # Perfil por defecto: solo distancia
        return {'id': 0, 'pesos': {'distancia': 1.0}}
    
    # 1. Obtener probabilidades de la tabla PERFILES
    perfiles = perfiles_df['PERFILES'].values
    probabilidades = perfiles_df['PROBABILIDAD'].values
    
    # 2. Normalizar probabilidades
    suma = np.sum(probabilidades)
    if suma > 0:
        probabilidades_normalizadas = probabilidades / suma
    else:
        probabilidades_normalizadas = np.ones(len(perfiles)) / len(perfiles)
    
    # 3. Seleccionar perfil usando distribución
    perfil_id = np.random.choice(perfiles, p=probabilidades_normalizadas)
    
    # 4. Cargar pesos del perfil
    perfil_data = perfiles_df[perfiles_df['PERFILES'] == perfil_id].iloc[0]
    pesos = {}
    
    # Solo incluir atributos que existen en AMBOS (ARCOS y PERFILES)
    for atributo in atributos_comunes:
        pesos[atributo.lower()] = perfil_data[atributo]
    
    return {'id': int(perfil_id), 'pesos': pesos}
```

**Resultado**: Un perfil con pesos para cada atributo.

### 3. Selección de Destino

**Cuándo ocurre**: Después de seleccionar perfil, antes de calcular ruta.

**Algoritmo**:
```python
def _seleccionar_destino(nodo_origen):
    if rutas_df is None:
        # Selección aleatoria uniforme
        nodos_destino = [nodo for nodo in grafo.nodes() if nodo != nodo_origen]
        return np.random.choice(nodos_destino)
    
    # 1. Buscar fila correspondiente al nodo origen
    fila_origen = rutas_df[rutas_df['NODO'] == nodo_origen].iloc[0]
    
    # 2. Obtener probabilidades de destino
    nodos_destino = [col for col in rutas_df.columns if col != 'NODO']
    probabilidades = [fila_origen[nodo] for nodo in nodos_destino]
    
    # 3. Normalizar probabilidades
    suma = np.sum(probabilidades)
    if abs(suma - 1.0) > 0.01:
        probabilidades_normalizadas = np.array(probabilidades) / suma
    else:
        probabilidades_normalizadas = probabilidades
    
    # 4. Seleccionar destino
    destino = np.random.choice(nodos_destino, p=probabilidades_normalizadas)
    
    return destino
```

**Resultado**: Un nodo destino seleccionado basado en matriz de probabilidades.

### 4. Cálculo de Ruta Óptima

**Cuándo ocurre**: Después de seleccionar origen, destino y perfil.

**Algoritmo (Dijkstra con Pesos Compuestos)**:
```python
def calcular_ruta_optima(grafo, origen, destino, perfil, rangos_atributos):
    # 1. Calcular pesos compuestos para cada arco
    pesos_compuestos = {}
    
    for arco in grafo.edges():
        atributos = grafo[arco[0]][arco[1]]
        peso_compuesto = 0.0
        
        # Para cada atributo en el perfil
        for atributo, peso_perfil in perfil['pesos'].items():
            if atributo in atributos:
                valor = atributos[atributo]
                
                # Normalizar valor según rango (escala 1-10)
                min_val, max_val = rangos_atributos[atributo]
                if max_val > min_val:
                    valor_normalizado = 1 + ((valor - min_val) / (max_val - min_val)) * 9
                else:
                    valor_normalizado = 5.5
                
                # Invertir para atributos donde mayor = peor (ej: distancia)
                if atributo == 'distancia':
                    valor_normalizado = 11 - valor_normalizado
                
                # Contribución del atributo al peso compuesto
                peso_compuesto += peso_perfil * valor_normalizado
        
        pesos_compuestos[arco] = peso_compuesto
    
    # 2. Crear grafo temporal con pesos compuestos
    G_temp = grafo.copy()
    for arco, peso in pesos_compuestos.items():
        G_temp[arco[0]][arco[1]]['weight'] = peso
    
    # 3. Calcular ruta usando algoritmo Dijkstra
    ruta = nx.shortest_path(G_temp, origen, destino, weight='weight')
    
    return ruta
```

**Resultado**: Lista de nodos que forman la ruta óptima `[A, B, C, D]`.

### 5. Ajuste de Velocidad por Inclinación

**Cuándo ocurre**: Durante el movimiento en cada tramo.

**Algoritmo**:
```python
def calcular_velocidad_ajustada(velocidad_base, atributos_arco):
    inclinacion = atributos_arco.get('inclinacion', 0.0)
    
    if inclinacion > 0:  # Subida
        # Reducir velocidad (máximo 50% de reducción)
        porcentaje_reduccion = min(50, abs(inclinacion))
        factor = 1.0 - (porcentaje_reduccion / 100.0)
    elif inclinacion < 0:  # Bajada
        # Aumentar velocidad (máximo 30% de aumento)
        porcentaje_aumento = min(30, abs(inclinacion))
        factor = 1.0 + (porcentaje_aumento / 100.0)
    else:  # Plano
        factor = 1.0
    
    velocidad_ajustada = velocidad_base * factor
    
    # Limitar entre velocidad_min y velocidad_max
    return max(velocidad_min, min(velocidad_max, velocidad_ajustada))
```

**Efecto**: Velocidad se ajusta dinámicamente según inclinación del tramo.

### 6. Factor de Tiempo por Seguridad/Luminosidad

**Cuándo ocurre**: Durante el movimiento en cada tramo.

**Algoritmo**:
```python
def calcular_factor_tiempo_desplazamiento(atributos_arco):
    factor_seguridad = 1.0
    factor_luminosidad = 1.0
    
    # Seguridad afecta tiempo (menos seguridad = más tiempo)
    if 'seguridad' in atributos_arco:
        seguridad = atributos_arco['seguridad']  # Rango 5-9
        # Seguridad 5 → factor 1.3, Seguridad 9 → factor 0.8
        factor_seguridad = 1.3 - (seguridad - 5) * 0.125
    
    # Luminosidad afecta tiempo (menos luminosidad = más tiempo)
    if 'luminosidad' in atributos_arco:
        luminosidad = atributos_arco['luminosidad']  # Rango 4-8
        # Luminosidad 4 → factor 1.2, Luminosidad 8 → factor 0.9
        factor_luminosidad = 1.2 - (luminosidad - 4) * 0.075
    
    # Factor combinado (multiplicativo)
    factor_tiempo = factor_seguridad * factor_luminosidad
    
    # Limitar entre 0.5 y 2.0
    return max(0.5, min(2.0, factor_tiempo))
```

**Uso**:
```python
tiempo_base = distancia / velocidad_ajustada
tiempo_real = tiempo_base * factor_tiempo  # Aplicar factor
```

**Efecto**: El tiempo de desplazamiento se ajusta según seguridad e iluminación.

### 7. Sistema de Capacidad y Factor de Densidad de Tráfico

**Cuándo ocurre**: Durante el movimiento en cada tramo, considerando la densidad de tráfico en el sentido de circulación.

**⚠️ IMPORTANTE: Diferenciación por Sentido**

El sistema calcula la capacidad y el factor de densidad **de forma independiente para cada sentido de circulación**. Esto significa que un tramo bidireccional tiene dos capacidades separadas:

- **Sentido A→B**: Capacidad y factor calculados independientemente
- **Sentido B→A**: Capacidad y factor calculados independientemente

Cada sentido se trata como un arco completamente diferente, con su propia capacidad y su propio conteo de bicicletas.

#### 7.1. Cálculo de Capacidad por Sentido

**Fórmula de Capacidad**:

```python
capacidad_maxima = distancia_real / longitud_bicicleta
```

Donde:
- **`distancia_real`**: Distancia del arco en metros (obtenida del grafo)
- **`longitud_bicicleta`**: Longitud promedio de una bicicleta = **2.5 metros**

**Identificación de Arcos por Sentido**:

Cada arco se identifica con un formato que incluye la dirección:

```python
arco_str = f"{nodo_actual}->{nodo_siguiente}"
```

**Ejemplos**:
- Arco de A hacia B: `"A->B"`
- Arco de B hacia A: `"B->A"`

Estos son tratados como **arcos completamente diferentes**, incluso si conectan los mismos nodos.

**Ejemplo de Cálculo**:

Si un arco tiene una distancia de **100 metros**:
- Sentido A→B: `capacidad = 100 / 2.5 = 40 bicicletas` (identificador: `"A->B"`)
- Sentido B→A: `capacidad = 100 / 2.5 = 40 bicicletas` (identificador: `"B->A"`, calculada independientemente)

**Resultado**: Cada sentido puede tener hasta 40 bicicletas simultáneamente, para un total de 80 bicicletas en el tramo físico completo.

#### 7.2. Rastreo de Bicicletas por Sentido

El simulador mantiene un registro en tiempo real de qué bicicletas están en cada sentido:

```python
self.bicicletas_en_arco = {}  # Dict[arco_str, set(ciclista_id)]
```

**Cada sentido tiene su propio conjunto de bicicletas**:
- `self.bicicletas_en_arco["A->B"]` = bicicletas yendo de A a B
- `self.bicicletas_en_arco["B->A"]` = bicicletas yendo de B a A

**Flujo de Registro**:

1. **Entrada al arco**: La bicicleta se agrega al conjunto del sentido específico
2. **Durante el movimiento**: El sistema rastrea cuántas bicicletas hay en cada sentido
3. **Salida del arco**: La bicicleta se remueve del conjunto del sentido específico

#### 7.3. Cálculo del Factor de Densidad

**Algoritmo**:

```python
def _calcular_factor_densidad(self, arco_str: str) -> float:
    # 1. Obtener capacidad máxima del sentido específico
    capacidad_maxima = self.capacidad_arcos[arco_str]
    
    # 2. Contar bicicletas actuales en el sentido específico
    num_bicicletas = len(self.bicicletas_en_arco.get(arco_str, set()))
    
    # 3. Si no hay sobrecarga, no hay reducción
    if num_bicicletas <= capacidad_maxima:
        return 1.0  # Factor = 1.0 significa velocidad normal
    
    # 4. Si hay sobrecarga, calcular factor de reducción
    factor = capacidad_maxima / num_bicicletas
    
    # 5. Limitar reducción máxima al 90% (factor mínimo = 0.1)
    return max(0.1, factor)
```

**Lógica**:
- Si `bicicletas ≤ capacidad` → factor = 1.0 (sin reducción)
- Si `bicicletas > capacidad` → factor = `capacidad / bicicletas` (reducción proporcional)
- Factor mínimo = 0.1 (reducción máxima del 90%)

**Ejemplos Prácticos**:

**Ejemplo 1: Sin Congestión**
- Capacidad máxima: 40 bicicletas
- Bicicletas actuales: 30 bicicletas
- Factor: `1.0` (sin reducción de velocidad)

**Ejemplo 2: Congestión Moderada**
- Capacidad máxima: 40 bicicletas
- Bicicletas actuales: 50 bicicletas
- Factor: `40 / 50 = 0.8` (reducción del 20% de velocidad)

**Ejemplo 3: Congestión Severa**
- Capacidad máxima: 40 bicicletas
- Bicicletas actuales: 80 bicicletas
- Factor: `40 / 80 = 0.5` (reducción del 50% de velocidad)

**Ejemplo 4: Congestión Extrema**
- Capacidad máxima: 40 bicicletas
- Bicicletas actuales: 400 bicicletas
- Factor: `max(0.1, 40/400) = 0.1` (reducción máxima del 90%)

#### 7.4. Aplicación del Factor de Densidad a la Velocidad

**Cuándo ocurre**: Al entrar al arco y durante el movimiento (recalculo periódico).

**Algoritmo**:

```python
# Al entrar al arco
factor_densidad = self._calcular_factor_densidad(arco_str)
velocidad_con_densidad = velocidad * factor_densidad

# Durante el movimiento (recalculo periódico cada 25% del recorrido)
if i % pasos_entre_actualizaciones == 0:
    factor_densidad_actual = self._calcular_factor_densidad(arco_str)
    velocidad_actual = velocidad_base_sin_densidad * factor_densidad_actual
```

**Efecto**: La velocidad se multiplica por el factor de densidad. Si el factor es menor que 1.0, la velocidad se reduce.

**Ejemplo**:
- Velocidad base: 10 m/s
- Factor de densidad: 0.8 (reducción del 20%)
- Velocidad resultante: `10 * 0.8 = 8 m/s`

#### 7.5. Efecto en el Tiempo de Viaje

El factor de densidad afecta directamente el tiempo de viaje:

```python
tiempo_base = distancia / velocidad_con_densidad
tiempo_total = tiempo_base * factor_tiempo
```

Donde:
- **`velocidad_con_densidad`** = `velocidad_base * factor_densidad`
- Si hay congestión, la velocidad baja → el tiempo de viaje aumenta

**Ejemplo**:
- Distancia: 100 metros
- Velocidad sin congestión: 10 m/s → Tiempo = 10 segundos
- Velocidad con congestión (factor 0.8): 8 m/s → Tiempo = 12.5 segundos
- **Diferencia**: 2.5 segundos adicionales (25% más lento)

#### 7.6. Ejemplo Completo: Tramo Bidireccional con Congestión Asimétrica

**Escenario**: Tramo de 100 metros entre nodos A y B

**Estado**:
- Sentido A→B: 50 ciclistas
- Sentido B→A: 20 ciclistas

**Cálculos Independientes**:

**Sentido A→B**:
- Capacidad: `100 / 2.5 = 40 bicicletas`
- Bicicletas: 50
- Factor: `40 / 50 = 0.8` (reducción del 20%)
- Velocidad: `10 * 0.8 = 8 m/s`
- Tiempo: `100 / 8 = 12.5 segundos`

**Sentido B→A**:
- Capacidad: `100 / 2.5 = 40 bicicletas` (calculada independientemente)
- Bicicletas: 20
- Factor: `1.0` (20 ≤ 40, sin reducción)
- Velocidad: `10 * 1.0 = 10 m/s`
- Tiempo: `100 / 10 = 10 segundos`

**Resultado**:
- Los ciclistas yendo de A a B circulan a 8 m/s (20% más lento) y tardan 12.5 segundos
- Los ciclistas yendo de B a A circulan a 10 m/s (velocidad normal) y tardan 10 segundos
- Cada sentido se gestiona completamente de forma independiente

#### 7.7. Características Importantes

1. **Cálculo Dinámico**: El factor se recalcula periódicamente durante el movimiento (cada 25% del recorrido)
2. **Límite de Reducción**: Reducción máxima del 90% (factor mínimo = 0.1) para mantener realismo
3. **Sin Capacidad = Sin Restricción**: Si un arco no tiene capacidad calculada, el factor es `1.0` (sin reducción)
4. **Efecto Acumulativo**: El factor de densidad se combina con otros factores:
   - Factor de inclinación (subida/bajada)
   - Factor de tiempo (seguridad/luminosidad)
5. **Independencia por Sentido**: La congestión en un sentido no afecta directamente al sentido contrario

---

## ⏱️ Gestión del Tiempo

### Tiempo de Simulación

El tiempo de simulación es **discreto** y avanza mediante eventos.

**Características**:
- Tiempo se mide en **segundos**
- Tiempo inicial: `0.0`
- Tiempo final: `duracion_simulacion` (configurable, por defecto 300s)
- Avance: determinado por eventos

### Tipos de Tiempo

#### 1. Tiempo de Simulación Global

```python
env.now  # Tiempo actual del entorno SimPy
```

**Uso**: Marca el tiempo absoluto de la simulación.

#### 2. Tiempo de Arribo

```python
tiempo_arribo = distribucion.generar_tiempo_arribo(nodo)
yield env.timeout(tiempo_arribo)  # Espera tiempo_arribo segundos
```

**Generación**: Distribución probabilística configurada por nodo.

**Ejemplo**:
- Distribución exponencial con `lambda = 0.5`
- Tiempo promedio entre arribos: `1 / 0.5 = 2.0 segundos`

#### 3. Tiempo de Movimiento

```python
distancia = obtener_distancia_arco(origen, destino)
velocidad_ajustada = calcular_velocidad_ajustada(velocidad_base, atributos)
factor_tiempo = calcular_factor_tiempo_desplazamiento(atributos)
factor_densidad = calcular_factor_densidad(arco_str)  # Nuevo: factor de densidad

velocidad_con_densidad = velocidad_ajustada * factor_densidad
tiempo_base = distancia / velocidad_con_densidad
tiempo_total = tiempo_base * factor_tiempo
```

**Cálculo**:
- **Distancia**: Atributo del arco (metros)
- **Velocidad**: Configurada por usuario, ajustada por inclinación (m/s)
- **Factor de densidad**: Multiplicador por congestión de tráfico (nuevo)
- **Factor de tiempo**: Multiplicador por seguridad/luminosidad

**Ejemplo**:
```
Distancia: 50 metros
Velocidad ajustada: 12 m/s (reducida por inclinación)
Factor densidad: 0.8 (reducción del 20% por congestión)
Velocidad con densidad: 12 * 0.8 = 9.6 m/s
Factor tiempo: 1.2 (aumentado por baja seguridad)
Tiempo base: 50 / 9.6 = 5.21 segundos
Tiempo total: 5.21 * 1.2 = 6.25 segundos
```

#### 4. Tiempo de Viaje Total

```python
tiempo_inicio_viaje[id] = env.now  # Al iniciar viaje
# ... movimiento ...
tiempo_total_viaje = env.now - tiempo_inicio_viaje[id]  # Al completar
```

**Uso**: Estadísticas de duración de viajes.

---

## 📊 Estado del Sistema

### Variables de Estado

El estado del sistema se mantiene en:

```python
class SimuladorCiclorutas:
    # Estado de simulación
    estado: str                    # "detenido" | "ejecutando" | "pausado" | "completada"
    tiempo_actual: float           # Tiempo de simulación actual
    
    # Estado de ciclistas
    coordenadas: List[Tuple]       # Posiciones actuales
    rutas: List[str]               # Rutas asignadas
    colores: List[str]             # Colores de visualización
    velocidades: List[float]       # Velocidades actuales
    estado_ciclistas: Dict        # Estado por ciclista
    
    # Estado de rutas y arcos
    rutas_utilizadas: Dict         # Contador de rutas
    arcos_utilizados: Dict         # Contador de arcos
    
    # Estado de perfiles
    perfiles_ciclistas: Dict       # Perfil asignado por ciclista
    contador_perfiles: Dict        # Uso de perfiles
```

### Transiciones de Estado

```
INICIO
  ↓
"detenido"  →  (NUEVA)  →  "detenido" (nuevo)
  ↓ (INICIAR)
"ejecutando"  →  (PAUSAR)  →  "pausado"
  ↓                ↓
(REANUDAR)      "pausado"  →  (REANUDAR)  →  "ejecutando"
  ↓
(tiempo_termina)  →  "completada"
  ↓
(TERMINAR)  →  "detenido"
```

---

## 🔄 Flujo de Ejecución

### Flujo Completo de la Simulación

```
1. INICIALIZACIÓN
   ├─> Crear entorno SimPy (env = simpy.Environment())
   ├─> Crear proceso generador_ciclistas
   └─> Crear proceso detener_por_tiempo

2. EJECUCIÓN (bucle principal)
   │
   ├─> Procesar próximo evento del calendario
   │
   ├─> Si evento es ARRIBO:
   │   ├─> Seleccionar nodo origen (por tasas)
   │   ├─> Generar tiempo de arribo
   │   ├─> Esperar tiempo (yield env.timeout())
   │   ├─> Seleccionar perfil (por probabilidades)
   │   ├─> Seleccionar destino (por matriz RUTAS)
   │   ├─> Calcular ruta óptima (Dijkstra)
   │   └─> Crear proceso ciclista()
   │
   ├─> Si evento es MOVIMIENTO:
   │   ├─> Obtener ruta del ciclista
   │   ├─> Para cada tramo de la ruta:
   │   │   ├─> Calcular distancia
   │   │   ├─> Ajustar velocidad (por inclinación)
   │   │   ├─> Calcular factor tiempo (por seguridad/luminosidad)
   │   │   ├─> Calcular tiempo de movimiento
   │   │   └─> Interpolar posición (cada 0.5s)
   │   └─> Cuando completa: marcar como 'completado'
   │
   └─> Si evento es FINALIZACIÓN:
       ├─> Generar archivo Excel con resultados
       └─> Estado = "completada"

3. FINALIZACIÓN
   └─> Exportar estadísticas y resultados
```

### Ejemplo de Ejecución Paso a Paso

```
Tiempo: 0.0s
  Evento: Inicio generador_ciclistas
  Acción: Selecciona nodo A (tasa 0.5), genera tiempo_arribo = 2.3s
  Próximo evento: Arribo en t=2.3s

Tiempo: 2.3s
  Evento: Arribo de ciclista #1 al nodo A
  Acción: 
    - Selecciona perfil 1 (prob 0.4)
    - Selecciona destino C (prob 0.3)
    - Calcula ruta: A → B → C
    - Crea proceso ciclista_1()
  Próximo evento: Movimiento ciclista #1 en t=2.8s

Tiempo: 2.8s
  Evento: Movimiento ciclista #1
  Acción: Actualiza posición (A → B, progreso 10%)
  Próximo evento: Movimiento ciclista #1 en t=3.3s

Tiempo: 5.1s
  Evento: Arribo de ciclista #2 al nodo B
  Acción: Similar a ciclista #1
  Próximo evento: Movimiento ciclista #2 en t=5.6s

Tiempo: 10.2s
  Evento: Llegada ciclista #1 a nodo B
  Acción: Inicia tramo B → C
  Próximo evento: Movimiento ciclista #1 en t=10.7s

Tiempo: 15.8s
  Evento: Finalización viaje ciclista #1
  Acción: Ciclista #1 completa ruta, estado = 'completado'
  Próximo evento: Arribo ciclista #3 en t=18.3s

...

Tiempo: 300.0s
  Evento: Finalización de simulación
  Acción: Generar Excel con resultados, estado = "completada"
```

---

## 🚧 Limitaciones y Supuestos

### Supuestos del Modelo

1. **Movimiento Continuo**: Los ciclistas se mueven de forma continua entre nodos (interpolación lineal)
2. **Sin Colisiones**: Los ciclistas no interactúan entre sí
3. **Velocidad Constante por Tramo**: Velocidad se ajusta al inicio del tramo y se mantiene constante
4. **Rutas Fijas**: Una vez asignada una ruta, el ciclista no la cambia
5. **Sin Capacidad de Nodos**: Los nodos no tienen límite de capacidad
6. **Distribuciones Independientes**: Los arribos son independientes entre nodos

### Limitaciones Conocidas

1. **Escala Temporal**: Simulación optimizada para duraciones de minutos/horas, no días
2. **Número de Ciclistas**: Rendimiento óptimo con < 1000 ciclistas simultáneos
3. **Tamaño de Grafo**: Grafos muy grandes (> 100 nodos) pueden ser lentos
4. **Interpolación**: Movimiento usa interpolación lineal, no considera aceleración
5. **Tiempo de Procesamiento**: Cada evento toma tiempo real de procesamiento (no es tiempo real puro)

### Áreas de Mejora Futura

1. **Colisiones y Interacciones**: Modelar interacciones entre ciclistas
2. **Cambios de Ruta**: Permitir cambios dinámicos de ruta
3. **Semanáforos y Señales**: Agregar controles de tráfico
4. **Grupos de Ciclistas**: Modelar pelotones
5. **Condiciones Meteorológicas**: Afectar velocidad y decisión de ruta

---

## 📚 Referencias Técnicas

- **SimPy Documentation**: Framework de simulación de eventos discretos
- **NetworkX Algorithms**: Algoritmos de grafos (Dijkstra, shortest path)
- **Distribuciones Probabilísticas**: numpy.random para generación estocástica
- **Simulación de Eventos Discretos**: Teoría y práctica

---

Este documento describe el modelo de simulación en detalle. Para información sobre la arquitectura del sistema, consulte **README_ARQUITECTURA.md**. Para instalación y uso, consulte **README_INSTALACION.md**.

