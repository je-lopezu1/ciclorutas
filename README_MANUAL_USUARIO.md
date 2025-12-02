# Manual de Usuario - Simulador de Ciclorutas

## Tabla de Contenidos

- [Introducción](#introducción)
- [Preparación de Archivos Excel](#preparación-de-archivos-excel)
- [Formato de Archivos Excel](#formato-de-archivos-excel)
- [Inicio de la Aplicación](#inicio-de-la-aplicación)
- [Carga de Red de Ciclorutas](#carga-de-red-de-ciclorutas)
- [Configuración de Parámetros](#configuración-de-parámetros)
- [Configuración de Distribuciones](#configuración-de-distribuciones)
- [Control de Simulación](#control-de-simulación)
- [Interpretación de Resultados](#interpretación-de-resultados)
- [Exportación de Datos](#exportación-de-datos)
- [Interpretación del Excel de Estadísticas](#interpretación-del-excel-de-estadísticas)
- [Ejemplos Prácticos](#ejemplos-prácticos)
- [Preguntas Frecuentes](#preguntas-frecuentes)
- [Compartir Resultados y Uso Académico](#compartir-resultados-y-uso-académico)

---

## Introducción

Este manual proporciona una guía paso a paso para utilizar el Simulador de Ciclorutas. La herramienta permite simular el comportamiento de ciclistas en redes urbanas de ciclorutas, considerando múltiples factores como distancia, seguridad, luminosidad e inclinación.

### Objetivo del Manual

Este documento está dirigido a usuarios que desean:
- Preparar archivos Excel con datos de redes de ciclorutas
- Configurar y ejecutar simulaciones
- Interpretar resultados y estadísticas
- Utilizar la herramienta para análisis y planificación urbana

---

## Preparación de Archivos Excel

### Requisitos del Archivo

El sistema requiere archivos Excel en formato `.xlsx` o `.xls` con una estructura específica. El archivo debe contener al menos dos hojas obligatorias y puede incluir hojas opcionales para funcionalidades avanzadas.

### Estructura Mínima

Un archivo Excel válido debe contener:
1. **Hoja "NODOS"** (obligatoria): Define los puntos de acceso o intersecciones
2. **Hoja "ARCOS"** (obligatoria): Define las conexiones entre nodos con sus atributos

### Estructura Avanzada (Opcional)

Para simulaciones más realistas, se pueden agregar:
3. **Hoja "PERFILES"** (opcional): Define tipos de ciclistas con diferentes preferencias
4. **Hoja "RUTAS"** (opcional): Define probabilidades de destino por nodo origen

---

## Formato de Archivos Excel

### Hoja "NODOS" (Obligatoria)

Esta hoja define todos los nodos (intersecciones o puntos de acceso) de la red.

#### Columnas Requeridas

| Columna | Descripción | Tipo | Ejemplo |
|---------|-------------|------|---------|
| `NODO` | Identificador único del nodo | Texto | "A", "B", "Nodo1", "Centro" |

#### Columnas Opcionales

| Columna | Descripción | Tipo | Ejemplo |
|---------|-------------|------|---------|
| `ID` | ID numérico del nodo | Entero | 1, 2, 3 |
| `NOMBRE` | Nombre descriptivo | Texto | "Intersección Principal" |
| `LAT` | Latitud (coordenadas geográficas) | Decimal | 4.6097, -74.0817 |
| `LON` | Longitud (coordenadas geográficas) | Decimal | -74.0817 |

#### Ejemplo de Hoja NODOS

```
| NODO | ID | NOMBRE                | LAT      | LON       |
|------|----|-----------------------|----------|-----------|
| A    | 1  | Centro Comercial      | 4.6097   | -74.0817  |
| B    | 2  | Parque Principal      | 4.6100   | -74.0820  |
| C    | 3  | Estación Metro        | 4.6095   | -74.0815  |
| D    | 4  | Universidad           | 4.6105   | -74.0825  |
```

#### Notas Importantes

- **Identificador único**: Cada nodo debe tener un identificador único en la columna `NODO`
- **Coordenadas geográficas**: Si se incluyen `LAT` y `LON`, el sistema calculará automáticamente las distancias euclidianas usando la fórmula de Haversine
- **Sin coordenadas**: Si no se proporcionan coordenadas, el sistema generará posiciones automáticamente para visualización

---

### Hoja "ARCOS" (Obligatoria)

Esta hoja define todas las conexiones (segmentos de cicloruta) entre nodos.

#### Columnas Requeridas

| Columna | Descripción | Tipo | Ejemplo | Rango |
|---------|-------------|------|---------|-------|
| `ORIGEN` | Nodo de origen | Texto | "A", "B" | Debe existir en NODOS |
| `DESTINO` | Nodo de destino | Texto | "B", "C" | Debe existir en NODOS |
| `DISTANCIA` | Distancia en metros | Decimal | 50.0, 125.5 | > 0 |

**Nota**: Si la hoja NODOS incluye `LAT` y `LON`, la columna `DISTANCIA` será ignorada y se calculará automáticamente.

#### Columnas Opcionales (Atributos)

| Columna | Descripción | Tipo | Rango Recomendado | Efecto |
|---------|-------------|------|-------------------|--------|
| `INCLINACION` | Inclinación en porcentaje | Decimal | -50% a +50% | Afecta velocidad del ciclista |
| `SEGURIDAD` | Nivel de seguridad | Entero/Decimal | 1-10 | Afecta tiempo de desplazamiento |
| `LUMINOSIDAD` | Nivel de luminosidad | Entero/Decimal | 1-10 | Afecta tiempo de desplazamiento |

#### Ejemplo de Hoja ARCOS

```
| ORIGEN | DESTINO | DISTANCIA | SEGURIDAD | LUMINOSIDAD | INCLINACION |
|--------|---------|-----------|-----------|-------------|-------------|
| A      | B       | 50.0      | 8         | 7           | 1.5         |
| B      | C       | 30.0      | 6         | 5           | 2.0         |
| C      | A       | 40.0      | 9         | 8           | 0.5         |
| A      | D       | 75.0      | 7         | 6           | -1.0        |
| B      | D       | 60.0      | 8         | 7           | 0.0         |
```

#### Interpretación de Atributos

**DISTANCIA**:
- Distancia física real entre nodos en metros
- Se usa para calcular tiempo de desplazamiento base
- Si hay coordenadas LAT/LON, se calcula automáticamente

**INCLINACION**:
- Valores positivos: subida (reduce velocidad)
- Valores negativos: bajada (aumenta velocidad)
- Valor 0: terreno plano
- Rango típico: -50% a +50%
- **No afecta la selección de ruta**, solo la velocidad durante el movimiento

**SEGURIDAD**:
- Escala de 1 a 10 (mayor = más seguro)
- Valores más bajos aumentan el tiempo de desplazamiento
- Afecta el factor de tiempo multiplicativo
- Se usa en el cálculo de rutas óptimas

**LUMINOSIDAD**:
- Escala de 1 a 10 (mayor = más iluminado)
- Valores más bajos aumentan el tiempo de desplazamiento
- Afecta el factor de tiempo multiplicativo
- Se usa en el cálculo de rutas óptimas

#### Validación de ARCOS

El sistema validará que:
- Todos los nodos en `ORIGEN` y `DESTINO` existan en la hoja NODOS
- No haya valores negativos en `DISTANCIA`
- Los valores de atributos estén en rangos razonables

---

### Hoja "PERFILES" (Opcional)

Esta hoja define diferentes tipos de ciclistas con preferencias distintas sobre los atributos de los arcos.

#### Columnas Requeridas

| Columna | Descripción | Tipo | Restricción |
|---------|-------------|------|-------------|
| `PERFILES` | ID del perfil | Entero | 1, 2, 3, ... |
| `PROBABILIDAD` | Probabilidad de selección | Decimal | 0.0 a 1.0, suma debe ser 1.0 |

#### Columnas Opcionales (Pesos de Preferencia)

| Columna | Descripción | Tipo | Restricción |
|---------|-------------|------|-------------|
| `DISTANCIA` | Peso para distancia | Decimal | 0.0 a 1.0 |
| `SEGURIDAD` | Peso para seguridad | Decimal | 0.0 a 1.0 |
| `LUMINOSIDAD` | Peso para luminosidad | Decimal | 0.0 a 1.0 |
| `INCLINACION` | Peso para inclinación | Decimal | 0.0 a 1.0 |

**Importante**: Los nombres de las columnas de atributos deben coincidir exactamente con los nombres de las columnas en la hoja ARCOS (pueden ser en mayúsculas o minúsculas, el sistema los normaliza).

#### Ejemplo de Hoja PERFILES

```
| PERFILES | PROBABILIDAD | DISTANCIA | SEGURIDAD | LUMINOSIDAD | INCLINACION |
|----------|--------------|-----------|-----------|-------------|-------------|
| 1        | 0.4          | 0.4       | 0.3       | 0.2         | 0.1         |
| 2        | 0.3          | 0.2       | 0.5       | 0.2         | 0.1         |
| 3        | 0.3          | 0.3       | 0.2       | 0.3         | 0.2         |
```

#### Interpretación del Ejemplo

- **Perfil 1** (40% de ciclistas): Prioriza distancia corta (0.4), luego seguridad (0.3)
- **Perfil 2** (30% de ciclistas): Prioriza seguridad (0.5), menos importancia a distancia (0.2)
- **Perfil 3** (30% de ciclistas): Balance entre distancia (0.3) y luminosidad (0.3)

#### Validación de PERFILES

El sistema validará que:
- Las probabilidades sumen 1.0 (con tolerancia de 0.01)
- Los pesos de cada perfil sean valores entre 0.0 y 1.0
- Los atributos mencionados existan en la hoja ARCOS

#### Nota sobre Pesos

Los pesos no necesitan sumar 1.0 individualmente, pero representan la importancia relativa de cada atributo para ese perfil. El sistema normaliza internamente para el cálculo de rutas.

---

### Hoja "RUTAS" (Opcional)

Esta hoja define una matriz de probabilidades de destino por nodo origen. Esto permite modelar patrones de demanda específicos.

#### Estructura

- **Primera columna**: `NODO` (nodos origen)
- **Columnas siguientes**: Nombres de nodos destino (deben existir en la hoja NODOS)
- **Valores**: Probabilidades entre 0.0 y 1.0

#### Ejemplo de Hoja RUTAS

```
| NODO | A    | B    | C    | D    |
|------|------|------|------|------|
| A    | 0.0  | 0.4  | 0.3  | 0.3  |
| B    | 0.3  | 0.0  | 0.5  | 0.2  |
| C    | 0.4  | 0.3  | 0.0  | 0.3  |
| D    | 0.25 | 0.25 | 0.25 | 0.0  |
```

#### Interpretación

- **Fila A**: Desde el nodo A, 40% va a B, 30% a C, 30% a D
- **Fila B**: Desde el nodo B, 30% va a A, 50% a C, 20% a D
- **Diagonal**: Siempre 0.0 (un ciclista no puede ir al mismo nodo de origen)

#### Validación de RUTAS

El sistema validará que:
- Todos los nodos en la primera columna existan en la hoja NODOS
- Todas las columnas de destino existan en la hoja NODOS
- Cada fila sume aproximadamente 1.0 (el sistema normaliza si es necesario)
- Los valores estén entre 0.0 y 1.0

#### Comportamiento sin Hoja RUTAS

Si no se proporciona la hoja RUTAS, el sistema asignará destinos de manera uniforme entre todos los nodos disponibles (excepto el nodo origen).

---

## Inicio de la Aplicación

### Requisitos Previos

Antes de iniciar la aplicación, asegúrese de:
1. Tener Python 3.7 o superior instalado
2. Haber instalado todas las dependencias (ver `README_INSTALACION.md`)
3. Tener un archivo Excel preparado con el formato correcto

### Ejecución

1. Abra una terminal o línea de comandos
2. Navegue hasta la carpeta del proyecto
3. Ejecute el comando:
   ```bash
   python main.py
   ```

### Interfaz Gráfica

Al iniciar, se abrirá una ventana con cuatro paneles principales:

1. **Panel de Control** (izquierda superior): Parámetros y botones de control
2. **Panel de Visualización** (centro): Gráfico interactivo de la red
3. **Panel de Estadísticas** (derecha superior): Métricas en tiempo real
4. **Panel de Distribuciones** (inferior): Configuración de distribuciones y perfiles

---

## Carga de Red de Ciclorutas

### Paso 1: Preparar el Archivo Excel

Antes de cargar, verifique que su archivo Excel:
- Tiene las hojas "NODOS" y "ARCOS" con las columnas correctas
- Los nodos referenciados en ARCOS existen en NODOS
- Los valores numéricos son válidos (no negativos donde corresponde)

### Paso 2: Cargar el Archivo

1. En el **Panel de Control**, localice el botón **"Cargar Grafo"**
2. Haga clic en el botón
3. Se abrirá un diálogo de selección de archivos
4. Navegue hasta su archivo Excel y selecciónelo
5. Haga clic en "Abrir"

### Paso 3: Validación

El sistema realizará automáticamente:
- Verificación de existencia de hojas obligatorias
- Validación de columnas requeridas
- Verificación de coherencia entre NODOS y ARCOS
- Validación de probabilidades (si hay hoja PERFILES)
- Cálculo de distancias (si hay coordenadas LAT/LON)

### Mensajes de Éxito

Si la carga es exitosa, verá:
- Un mensaje de confirmación en la ventana
- El grafo aparecerá en el Panel de Visualización
- Las estadísticas del grafo se actualizarán en el Panel de Estadísticas

### Mensajes de Error

Si hay errores, el sistema mostrará un mensaje indicando:
- Qué hoja falta o tiene problemas
- Qué columnas son incorrectas
- Qué validaciones fallaron

**Acción recomendada**: Revise el formato del archivo Excel según las especificaciones de este manual.

---

## Configuración de Parámetros

### Panel de Control

En el Panel de Control encontrará los siguientes parámetros configurables:

#### Velocidad Mínima

- **Rango**: 1.0 a 20.0 m/s
- **Valor por defecto**: 10.0 m/s
- **Descripción**: Velocidad mínima que puede tener un ciclista
- **Uso**: Cada ciclista recibirá una velocidad aleatoria entre el mínimo y máximo

#### Velocidad Máxima

- **Rango**: 1.0 a 30.0 m/s
- **Valor por defecto**: 15.0 m/s
- **Descripción**: Velocidad máxima que puede tener un ciclista
- **Restricción**: Debe ser mayor que la velocidad mínima

#### Duración de Simulación

- **Rango**: 60 a 3600 segundos
- **Valor por defecto**: 300 segundos (5 minutos)
- **Descripción**: Tiempo total que durará la simulación
- **Nota**: La simulación se detendrá automáticamente al alcanzar este tiempo

### Cómo Configurar

1. Localice los campos de entrada en el Panel de Control
2. Haga clic en el campo que desea modificar
3. Ingrese el nuevo valor
4. Los cambios se aplicarán cuando cree una nueva simulación

### Validación Automática

El sistema validará automáticamente que:
- Los valores estén dentro de los rangos permitidos
- La velocidad máxima sea mayor que la mínima
- Los valores sean numéricos válidos

---

## Configuración de Distribuciones

### ¿Qué son las Distribuciones?

Las distribuciones de probabilidad determinan cuándo y con qué frecuencia llegan nuevos ciclistas a cada nodo. Esto modela la demanda de tráfico en diferentes puntos de la red.

### Panel de Distribuciones

El Panel de Distribuciones permite configurar:
- Distribución de arribo para cada nodo
- Parámetros específicos de cada distribución
- Visualización de la configuración actual

### Tipos de Distribuciones Disponibles

#### 1. Exponencial

**Uso**: Modela tiempos entre arribos aleatorios (común en sistemas de colas)

**Parámetros**:
- `lambda`: Tasa de arribo (ciclistas por segundo)
  - Valores típicos: 0.1 a 2.0
  - Mayor lambda = más ciclistas por segundo

**Ejemplo**: lambda = 0.5 significa aproximadamente 1 ciclista cada 2 segundos

#### 2. Normal (Gaussiana)

**Uso**: Modela arribos con variabilidad simétrica

**Parámetros**:
- `media`: Tiempo promedio entre arribos (segundos)
- `desviacion`: Desviación estándar (segundos)
  - Valores típicos: media 3.0-10.0, desviación 0.5-2.0

#### 3. Log-Normal

**Uso**: Modela arribos con distribución asimétrica (valores positivos)

**Parámetros**:
- `mu`: Parámetro de localización
- `sigma`: Parámetro de escala
  - Valores típicos: mu 0.0-2.0, sigma 0.5-1.5

#### 4. Gamma

**Uso**: Modela arribos con distribución flexible

**Parámetros**:
- `forma`: Parámetro de forma (alpha)
- `escala`: Parámetro de escala (beta)
  - Valores típicos: forma 1.0-5.0, escala 0.5-2.0

#### 5. Weibull

**Uso**: Modela arribos con diferentes formas de distribución

**Parámetros**:
- `forma`: Parámetro de forma (c)
- `escala`: Parámetro de escala (lambda)
  - Valores típicos: forma 1.0-3.0, escala 0.5-2.0

### Cómo Configurar una Distribución

1. En el **Panel de Distribuciones**, seleccione un nodo del menú desplegable
2. Seleccione el tipo de distribución deseada
3. Ingrese los parámetros según el tipo seleccionado
4. Haga clic en "Aplicar" o "Guardar"
5. La configuración se aplicará cuando inicie una nueva simulación

### Distribuciones por Defecto

Si no configura distribuciones manualmente, el sistema asignará automáticamente:
- Distribución exponencial para todos los nodos
- Tasas de arribo variadas según el nodo
- Parámetros razonables para comenzar

---

## Control de Simulación

### Botones de Control

El Panel de Control incluye los siguientes botones:

#### NUEVA

- **Función**: Crea una nueva simulación con los parámetros actuales
- **Cuándo usar**: Al cambiar parámetros o después de completar una simulación
- **Efecto**: Reinicia el estado de la simulación, limpia datos anteriores

#### INICIAR

- **Función**: Comienza la ejecución de la simulación
- **Cuándo usar**: Después de crear una nueva simulación o cargar un grafo
- **Efecto**: La simulación comienza a ejecutarse, los ciclistas aparecen en la visualización

#### PAUSAR / REANUDAR

- **Función**: Pausa o reanuda la simulación en curso
- **Cuándo usar**: Para detener temporalmente la simulación sin perder el estado
- **Efecto**: 
  - PAUSAR: Detiene la ejecución, mantiene el estado actual
  - REANUDAR: Continúa desde donde se pausó

#### TERMINAR

- **Función**: Finaliza la simulación inmediatamente
- **Cuándo usar**: Cuando desea detener la simulación antes de que termine naturalmente
- **Efecto**: Detiene la simulación, genera resultados si es posible

#### ADELANTAR

- **Función**: Avanza la simulación 10 pasos discretos
- **Cuándo usar**: Para análisis paso a paso o debugging
- **Efecto**: Ejecuta 10 eventos del calendario de simulación

#### REINICIAR

- **Función**: Reinicia la simulación actual desde el principio
- **Cuándo usar**: Para repetir la simulación con los mismos parámetros
- **Efecto**: Vuelve al tiempo 0, mantiene la configuración actual

### Flujo de Trabajo Recomendado

1. **Cargar Grafo**: Cargue su archivo Excel con la red
2. **Configurar Parámetros**: Ajuste velocidades y duración según necesidades
3. **Configurar Distribuciones**: (Opcional) Ajuste distribuciones por nodo
4. **NUEVA**: Cree una nueva simulación
5. **INICIAR**: Inicie la simulación
6. **Observar**: Monitoree la visualización y estadísticas
7. **PAUSAR/REANUDAR**: Si necesita detener temporalmente
8. **TERMINAR**: Cuando desee finalizar
9. **Exportar**: Guarde los resultados si es necesario

---

## Interpretación de Resultados

### Panel de Visualización

El Panel de Visualización muestra:

#### Elementos del Grafo

- **Nodos**: Representados como círculos con etiquetas
- **Arcos**: Representados como líneas conectando nodos
- **Ciclistas**: Representados como puntos de colores que se mueven

#### Colores de Ciclistas

Cada ciclista hereda el color del nodo de origen:
- Diferentes nodos tienen colores distintos
- Facilita identificar de dónde vienen los ciclistas
- Los colores se asignan automáticamente

#### Trayectorias

- Las líneas detrás de los ciclistas muestran sus trayectorias recientes
- Útil para ver patrones de movimiento
- Se actualiza en tiempo real

### Panel de Estadísticas

El Panel de Estadísticas muestra métricas actualizadas en tiempo real:

#### Estadísticas Básicas

- **Ciclistas Activos**: Número de ciclistas actualmente en movimiento
- **Ciclistas Completados**: Número de ciclistas que terminaron su viaje
- **Velocidad Promedio**: Velocidad promedio de todos los ciclistas activos (m/s)
- **Velocidad Mínima**: Velocidad más baja entre ciclistas activos
- **Velocidad Máxima**: Velocidad más alta entre ciclistas activos
- **Tiempo de Simulación**: Tiempo transcurrido desde el inicio (segundos)

#### Estadísticas del Grafo

- **Nodos del Grafo**: Número total de nodos en la red
- **Arcos del Grafo**: Número total de conexiones
- **Atributos Disponibles**: Número de atributos en los arcos

#### Estadísticas de Distribuciones

- **Distribuciones Configuradas**: Número de nodos con distribuciones personalizadas
- **Tasa de Arribo Promedio**: Tasa promedio de llegada de ciclistas
- **Duración**: Duración configurada de la simulación

#### Estadísticas de Rutas

- **Rutas Utilizadas**: Número de rutas diferentes utilizadas
- **Total de Viajes**: Número total de viajes completados
- **Ruta Más Usada**: Ruta con mayor frecuencia de uso
- **Nodo Más Activo**: Nodo que genera más ciclistas

### Interpretación de Métricas

#### Ciclistas Activos vs Completados

- **Alto número de activos**: Muchos ciclistas en movimiento simultáneo
- **Bajo número de activos**: Pocos ciclistas, posible baja demanda o simulación recién iniciada
- **Alto número de completados**: Muchos viajes terminados, red bien utilizada

#### Velocidades

- **Velocidad promedio alta**: Ciclistas se mueven rápidamente (buenas condiciones o bajas inclinaciones)
- **Velocidad promedio baja**: Ciclistas se mueven lentamente (condiciones adversas o altas inclinaciones)
- **Gran diferencia min/max**: Alta variabilidad en comportamiento de ciclistas

**Nota sobre Congestión**: El sistema modela automáticamente la congestión de tráfico. Cuando hay más ciclistas que la capacidad de un tramo (calculada como distancia/2.5m), la velocidad se reduce proporcionalmente. Cada sentido de circulación se evalúa independientemente, por lo que un sentido puede estar congestionado mientras el otro fluye normalmente. Esto puede explicar variaciones en velocidades promedio durante períodos de alta demanda.

#### Rutas Utilizadas

- **Muchas rutas diferentes**: Ciclistas distribuyen bien por la red
- **Pocas rutas**: Posible concentración en ciertos corredores
- **Ruta más usada**: Corredor principal o más atractivo según perfiles

---

## Exportación de Datos

### Generación Automática de Resultados

Al finalizar una simulación (por tiempo o manualmente), el sistema genera automáticamente un archivo Excel con resultados en la carpeta `resultados/`.

### Ubicación de Archivos

Los archivos se guardan en:
```
resultados/
├── nombre_grafo_YYYYMMDD_HHMMSS.xlsx
└── ...
```

Donde:
- `nombre_grafo`: Nombre del archivo Excel cargado (o "simulacion" por defecto)
- `YYYYMMDD_HHMMSS`: Fecha y hora de generación en formato año-mes-día hora-minuto-segundo

Ejemplo: `mi_red_20240115_143025.xlsx`

### Análisis de Resultados

Los archivos Excel generados pueden ser:
- Abiertos en Excel, Google Sheets, o cualquier herramienta de análisis
- Importados a herramientas de análisis de datos (Python, R, etc.)
- Usados para generar reportes y visualizaciones adicionales

---

## Interpretación del Excel de Estadísticas

Esta sección explica en detalle cómo leer e interpretar el archivo Excel generado al finalizar una simulación. El archivo contiene 4 hojas principales con información detallada de la simulación.

### Estructura General del Archivo

El archivo Excel generado contiene exactamente 4 hojas:

1. **Info Simulación**: Resumen general y estadísticas agregadas
2. **Tramos**: Información detallada de cada tramo/arco de la red
3. **Ciclistas**: Información detallada de cada ciclista individual
4. **Tiempos**: Estadísticas y detalles de tiempos de desplazamiento

---

### Hoja 1: Info Simulación

#### Propósito

Esta hoja contiene un resumen general de la simulación con estadísticas agregadas y parámetros de configuración. Está organizada en secciones con dos columnas: "Parámetro" y "Valor".

#### Secciones y Parámetros

**INFORMACIÓN GENERAL**

- **Fecha de simulación**: Fecha y hora exacta en que se ejecutó la simulación (formato: YYYY-MM-DD HH:MM:SS)
- **Duración de simulación**: Duración configurada para la simulación en segundos
- **Estado final**: Estado en que terminó la simulación
  - "completada": La simulación terminó normalmente al alcanzar el tiempo configurado
  - "detenido": La simulación fue detenida manualmente
  - "ejecutando": La simulación estaba en ejecución cuando se generó el reporte (raro)
- **Tiempo transcurrido**: Tiempo real que transcurrió durante la simulación en segundos (con 2 decimales)

**INFORMACIÓN DEL GRAFO**

- **Usando grafo real**: Indica si la simulación usó un grafo cargado desde Excel ("Sí" o "No")
- **Número de nodos**: Cantidad total de nodos en la red
- **Número de arcos**: Cantidad total de arcos/tramos en la red (cada sentido cuenta como un arco separado)
- **Grafo conectado**: Indica si todos los nodos están conectados entre sí ("Sí" o "No")
- **Distancia promedio arcos**: Distancia promedio de todos los arcos en la red en metros (con 2 decimales)

**ESTADÍSTICAS DE CICLISTAS**

- **Total de ciclistas creados**: Número total de ciclistas que fueron generados durante la simulación
- **Ciclistas activos**: Número de ciclistas que estaban en movimiento cuando terminó la simulación
  - Valor por defecto: 0 si todos completaron sus viajes
- **Ciclistas completados**: Número de ciclistas que terminaron exitosamente su viaje
- **Velocidad promedio**: Velocidad promedio de todos los ciclistas durante la simulación en km/h (con 2 decimales)
  - Nota: Esta velocidad ya refleja los efectos de inclinación y congestión
- **Velocidad mínima**: Velocidad más baja registrada entre todos los ciclistas en km/h
- **Velocidad máxima**: Velocidad más alta registrada entre todos los ciclistas en km/h

**ESTADÍSTICAS DE RUTAS**

- **Rutas únicas utilizadas**: Número de rutas diferentes que fueron utilizadas por los ciclistas
- **Total de viajes**: Número total de viajes completados
- **Ruta más usada**: La ruta que fue utilizada por más ciclistas (formato: "nodo1->nodo2->...->destino")
  - Valor por defecto: "Sin datos" si no hay rutas registradas
- **Tramo más concurrido**: El tramo que fue utilizado por más ciclistas (formato: "origen->destino")
  - Valor por defecto: "Sin datos" si no hay tramos registrados
  - Nota: Cada sentido se cuenta por separado

**ESTADÍSTICAS DE NODOS**

- **Nodo más activo**: El nodo que generó más ciclistas (más arribos)
  - Valor por defecto: "Sin datos" si no hay datos de nodos

**ESTADÍSTICAS DE PERFILES**

- **Total ciclistas con perfil**: Número de ciclistas a los que se les asignó un perfil de preferencias
  - Valor por defecto: 0 si no se usaron perfiles
- **Perfil más usado**: El perfil de preferencias que fue asignado a más ciclistas
  - Valor por defecto: "Sin datos" si no se usaron perfiles

---

### Hoja 2: Tramos

#### Propósito

Esta hoja contiene información detallada de cada tramo (arco) de la red, incluyendo sus atributos físicos y estadísticas de uso. Está ordenada por uso (más usado primero).

#### Columnas Fijas

**ID Tramo**
- Descripción: Identificador único del tramo
- Formato: "origen->destino"
- Ejemplo: "A->B", "Nodo1->Nodo2"
- Nota: Cada sentido de circulación tiene un ID diferente

**Nodo Origen**
- Descripción: Nodo de inicio del tramo
- Tipo: Identificador del nodo
- Ejemplo: "A", "Centro"

**Nodo Destino**
- Descripción: Nodo final del tramo
- Tipo: Identificador del nodo
- Ejemplo: "B", "Universidad"

**Distancia (m)**
- Descripción: Distancia física del tramo en metros
- Unidad: metros (con 1 decimal)
- Ejemplo: "125.5"
- Valor por defecto: 0 si no hay distancia definida

**Ciclistas que lo usaron**
- Descripción: Número de ciclistas que recorrieron este tramo durante la simulación
- Tipo: Entero
- Valor por defecto: 0 si ningún ciclista usó el tramo
- Nota: Cuenta cada vez que un ciclista pasa por el tramo

**Porcentaje de uso**
- Descripción: Porcentaje que representa este tramo del total de usos de todos los tramos
- Unidad: porcentaje (con 1 decimal)
- Ejemplo: "15.3%"
- Cálculo: (Ciclistas que lo usaron / Total de usos) * 100
- Valor por defecto: 0% si no hay usos

**Tiempo promedio (s)**
- Descripción: Tiempo promedio estimado para recorrer el tramo
- Unidad: segundos (con 1 decimal)
- Ejemplo: "10.5s"
- Cálculo: Basado en distancia y velocidad promedio de 12.5 km/h
- Nota: Es una estimación, no el tiempo real de la simulación

#### Columnas Dinámicas

Además de las columnas fijas, esta hoja puede incluir columnas adicionales según los atributos que tenga cada tramo en el grafo. Estas columnas aparecen con el nombre del atributo en formato título (primera letra mayúscula).

**Ejemplos de atributos comunes:**

- **Seguridad**: Nivel de seguridad del tramo (rango típico: 1-10 o 5-9). Valores más altos indican mayor seguridad. Valor por defecto: "N/A" si el atributo no está definido.

- **Luminosidad**: Nivel de iluminación del tramo (rango típico: 1-10 o 4-8). Valores más altos indican mejor iluminación. Valor por defecto: "N/A" si el atributo no está definido.

- **Inclinacion**: Inclinación del tramo en porcentaje (rango típico: -50% a +50%). Valores positivos son subidas, negativos son bajadas. Valor por defecto: "N/A" si el atributo no está definido.

- **Otros atributos**: Cualquier otro atributo definido en el archivo Excel de entrada aparecerá como columna adicional. Valor por defecto: "N/A" si el atributo no está presente en ese tramo específico.

---

### Hoja 3: Ciclistas

#### Propósito

Esta hoja contiene información detallada de cada ciclista individual que participó en la simulación, incluyendo su ruta, tiempos, velocidades y estado final. Está ordenada por ID de ciclista.

#### Columnas Fijas

**ID Ciclista**
- Descripción: Identificador único numérico del ciclista
- Tipo: Entero
- Ejemplo: 1, 2, 3, 100

**Origen**
- Descripción: Nodo donde el ciclista inició su viaje
- Tipo: Identificador del nodo
- Ejemplo: "A", "Centro", "Nodo1"
- Valor por defecto: "N/A" si no se pudo determinar el origen

**Destino**
- Descripción: Nodo donde el ciclista terminó o tenía como objetivo terminar su viaje
- Tipo: Identificador del nodo
- Ejemplo: "B", "Universidad", "Nodo5"
- Valor por defecto: "N/A" si no se pudo determinar el destino

**Ruta Simple**
- Descripción: Representación simplificada de la ruta mostrando solo origen y destino
- Formato: "origen->destino"
- Ejemplo: "A->B", "Centro->Universidad"
- Valor por defecto: "N/A" si no hay ruta registrada

**Ruta Detallada**
- Descripción: Secuencia completa de nodos por los que pasó el ciclista
- Formato: "nodo1->nodo2->nodo3->...->destino"
- Ejemplo: "A->B->C->D", "Centro->Nodo2->Nodo3->Universidad"
- Valor por defecto: "N/A" si no hay ruta detallada registrada
- Nota: Muestra el camino exacto que siguió el ciclista

**Perfil**
- Descripción: Perfil de preferencias asignado al ciclista
- Tipo: Nombre del perfil o identificador
- Ejemplo: "Seguridad", "Distancia", "Perfil 1"
- Valor por defecto: "Sin perfil" si no se asignó ningún perfil
- Nota: El perfil determina cómo el ciclista eligió su ruta

**Número de Tramos**
- Descripción: Cantidad de arcos/tramos que recorrió el ciclista
- Tipo: Entero
- Ejemplo: 3, 5, 10
- Cálculo: Número de elementos en la secuencia de la ruta detallada menos 1
- Valor por defecto: 0 si no hay ruta

**Distancia Total (m)**
- Descripción: Distancia total recorrida por el ciclista en metros
- Unidad: metros (con 1 decimal)
- Ejemplo: "250.5", "1000.0"
- Cálculo: Suma de las distancias de todos los tramos recorridos
- Valor por defecto: 0.0 si no hay datos de distancia

**Tiempo Total (s)**
- Descripción: Tiempo total que tardó el ciclista en completar su viaje
- Unidad: segundos (con 1 decimal)
- Ejemplo: "25.3", "100.5"
- Cálculo: Tiempo desde que inició el viaje hasta que lo completó
- Valor por defecto: 0.0 si el ciclista no completó su viaje
- Nota: Este tiempo incluye los efectos de:
  - Inclinación (subidas aumentan el tiempo)
  - Seguridad y luminosidad (afectan el tiempo de desplazamiento)
  - Congestión (factor de densidad reduce velocidad cuando hay sobrecarga)

**Tiempo Promedio por Tramo (s)**
- Descripción: Tiempo promedio que tardó el ciclista en cada tramo
- Unidad: segundos (con 1 decimal)
- Ejemplo: "8.4", "12.5"
- Cálculo: Tiempo Total / Número de Tramos
- Valor por defecto: 0.0 si no hay tiempo total o no hay tramos

**Velocidad Promedio (m/s)**
- Descripción: Velocidad promedio del ciclista durante todo el viaje
- Unidad: metros por segundo (con 2 decimales)
- Ejemplo: "9.89 m/s", "8.50 m/s"
- Cálculo: Distancia Total / Tiempo Total
- Valor por defecto: 0.00 m/s si no hay tiempo total
- Nota: Esta velocidad ya refleja los efectos de:
  - Inclinación (subidas reducen velocidad, bajadas la aumentan)
  - Congestión (factor de densidad reduce velocidad cuando hay sobrecarga)
  - Es la velocidad real observada en la simulación, no la velocidad configurada

**Tramos Utilizados**
- Descripción: Lista de los tramos (arcos) que utilizó el ciclista
- Formato: Lista separada por punto y coma (;)
- Ejemplo: "A->B; B->C; C->D"
- Limitación: Muestra máximo 5 tramos. Si hay más, muestra "(+X más)"
- Ejemplo con muchos tramos: "A->B; B->C; C->D; D->E; E->F (+3 más)"
- Valor por defecto: Vacío si no hay tramos registrados

**Estado**
- Descripción: Estado final del ciclista al terminar la simulación
- Valores posibles:
  - "completado": El ciclista terminó exitosamente su viaje
  - "activo": El ciclista estaba aún en movimiento cuando terminó la simulación
  - "Desconocido": No se pudo determinar el estado del ciclista
- Valor por defecto: "Desconocido" si no hay información de estado
- Nota: Si la simulación se detuvo antes de tiempo, puede haber ciclistas con estado "activo"

#### Columnas Dinámicas de Preferencias

Si los ciclistas tienen perfiles con preferencias definidas, pueden aparecer columnas adicionales:

**Pref. Seguridad**
- Descripción: Peso o preferencia del ciclista por la seguridad
- Tipo: Decimal (con 2 decimales)
- Rango típico: 0.0 a 1.0
- Ejemplo: "0.30", "0.50"
- Valor por defecto: "N/A" si el perfil no tiene esta preferencia
- Nota: Valores más altos indican mayor preferencia por rutas seguras

**Pref. Luminosidad**
- Descripción: Peso o preferencia del ciclista por la luminosidad
- Tipo: Decimal (con 2 decimales)
- Rango típico: 0.0 a 1.0
- Ejemplo: "0.20", "0.40"
- Valor por defecto: "N/A" si el perfil no tiene esta preferencia

**Pref. Distancia**
- Descripción: Peso o preferencia del ciclista por distancias cortas
- Tipo: Decimal (con 2 decimales)
- Rango típico: 0.0 a 1.0
- Ejemplo: "0.40", "0.60"
- Valor por defecto: "N/A" si el perfil no tiene esta preferencia
- Nota: Valores más altos indican mayor preferencia por rutas cortas

**Pref. Inclinacion**
- Descripción: Peso o preferencia del ciclista por la inclinación
- Tipo: Decimal (con 2 decimales)
- Rango típico: 0.0 a 1.0
- Ejemplo: "0.10", "0.30"
- Valor por defecto: "N/A" si el perfil no tiene esta preferencia

---

### Hoja 4: Tiempos

#### Propósito

Esta hoja contiene estadísticas agregadas y detalles individuales sobre los tiempos de desplazamiento de los ciclistas. Está dividida en dos secciones principales.

#### Sección 1: Estadísticas Generales de Tiempos

Esta sección aparece en las primeras filas y contiene métricas agregadas.

**Total de ciclistas con tiempo registrado**
- Descripción: Número de ciclistas para los que se registró tiempo de viaje
- Tipo: Entero
- Nota: Puede ser menor que el total de ciclistas si algunos no completaron su viaje

**Tiempo promedio de viaje**
- Descripción: Tiempo promedio de viaje entre todos los ciclistas
- Unidad: segundos (con 2 decimales)
- Ejemplo: "45.25 segundos"
- Cálculo: Suma de todos los tiempos / Número de ciclistas

**Tiempo mínimo de viaje**
- Descripción: El tiempo de viaje más corto registrado
- Unidad: segundos (con 2 decimales)
- Ejemplo: "15.30 segundos"

**Tiempo máximo de viaje**
- Descripción: El tiempo de viaje más largo registrado
- Unidad: segundos (con 2 decimales)
- Ejemplo: "120.50 segundos"

#### Sección 2: Detalles por Ciclista

Esta sección contiene una fila por cada ciclista con información detallada de sus tiempos.

**ID Ciclista**
- Descripción: Identificador del ciclista con información de origen y destino
- Formato: "Ciclista X (origen→destino)"
- Ejemplo: "Ciclista 1 (A→B)", "Ciclista 25 (Centro→Universidad)"

**Tiempo Total (s)**
- Descripción: Tiempo total del viaje del ciclista
- Unidad: segundos (con 2 decimales)
- Ejemplo: "25.30", "100.50"
- Nota: Mismo valor que en la hoja Ciclistas

**Número de Tramos**
- Descripción: Cantidad de tramos que recorrió el ciclista
- Tipo: Entero
- Ejemplo: 3, 5

**Tiempo Promedio por Tramo (s)**
- Descripción: Tiempo promedio en cada tramo
- Unidad: segundos (con 2 decimales)
- Ejemplo: "8.43", "12.50"
- Cálculo: Tiempo Total / Número de Tramos

**Tramos con Tiempo**
- Descripción: Lista de tiempos individuales por cada tramo
- Formato: Lista de tiempos separados por punto y coma
- Ejemplo: "10.5s; 8.3s; 12.1s"
- Limitación: Muestra máximo 5 tiempos. Si hay más, muestra "(+X más)"
- Ejemplo con muchos tramos: "10.5s; 8.3s; 12.1s; 9.2s; 11.0s (+3 más)"

**Ruta Completa**
- Descripción: Secuencia completa de nodos de la ruta del ciclista
- Formato: "nodo1->nodo2->nodo3->...->destino"
- Ejemplo: "A->B->C->D"
- Valor por defecto: "N/A" si no hay ruta registrada

---

### Valores por Defecto Comunes

Al interpretar el Excel, es importante entender qué significan los valores por defecto:

**"N/A" (No Disponible)**
- Significado: El dato no está disponible o no se pudo calcular
- Aparece cuando: Un atributo no está definido, una ruta no se registró, o falta información

**"Sin datos"**
- Significado: No hay datos para esa métrica agregada
- Aparece cuando: No se registró ninguna ocurrencia (ej: "Sin datos" en ruta más usada si no hay rutas)

**"Desconocido"**
- Significado: No se pudo determinar el estado o valor
- Aparece en: Estado de ciclista cuando no hay información registrada

**"Sin perfil"**
- Significado: Al ciclista no se le asignó ningún perfil de preferencias
- Aparece en: Columna Perfil cuando no hay perfiles configurados o asignados

**"activo" vs "completado"**
- "activo": El ciclista estaba aún en movimiento cuando terminó la simulación
- "completado": El ciclista terminó exitosamente su viaje
- Nota: Si la simulación se detuvo antes de tiempo, puede haber ciclistas con estado "activo"

---

### Notas Importantes sobre los Datos

**Diferenciación por Sentido**

Es importante entender que el sistema diferencia cada sentido de circulación:

- Un tramo físico entre nodos A y B tiene dos entradas separadas:
  - "A->B" (sentido de A hacia B)
  - "B->A" (sentido de B hacia A)

- Cada sentido tiene su propia capacidad y factor de densidad
- Los conteos de uso se hacen por sentido
- Esto permite analizar congestión asimétrica (un sentido congestionado, el otro no)

**Efectos en Tiempos y Velocidades**

Los tiempos y velocidades reportados ya incluyen todos los efectos del modelo:

1. **Inclinación**: Subidas reducen velocidad, bajadas la aumentan
2. **Seguridad y Luminosidad**: Afectan el tiempo de desplazamiento (valores bajos aumentan el tiempo)
3. **Congestión**: Cuando hay más ciclistas que la capacidad de un tramo, la velocidad se reduce proporcionalmente

Por lo tanto, la "Velocidad Promedio" y el "Tiempo Total" son valores reales observados, no valores teóricos o configurados.

**Interpretación de Estadísticas**

**Alta variabilidad en velocidades**
- Puede indicar diferentes condiciones en diferentes tramos (inclinaciones, congestión)
- Puede indicar diferentes perfiles de ciclistas con diferentes comportamientos

**Tiempos totales muy altos**
- Puede indicar rutas largas
- Puede indicar congestión en algunos tramos
- Puede indicar condiciones adversas (subidas, baja seguridad)

**Tramos con uso cero**
- Tramo no fue utilizado por ningún ciclista
- Puede indicar que no es parte de rutas óptimas según los perfiles
- Puede indicar que la demanda no requiere ese tramo

---

### Uso Recomendado del Excel

**Para análisis de rendimiento**
- Use la hoja "Ciclistas" para analizar tiempos y velocidades individuales
- Compare tiempos entre diferentes rutas
- Identifique ciclistas con tiempos anormalmente altos o bajos

**Para análisis de infraestructura**
- Use la hoja "Tramos" para identificar tramos más utilizados
- Identifique potenciales cuellos de botella (tramos con alto uso)
- Analice la distribución de uso por características (seguridad, luminosidad, etc.)

**Para resumen ejecutivo**
- Use la hoja "Info Simulación" para obtener un resumen rápido de la simulación
- Compare estadísticas entre diferentes simulaciones
- Valide que los parámetros de configuración se aplicaron correctamente

**Para análisis de tiempos**
- Use la hoja "Tiempos" para comparar tiempos entre ciclistas
- Analice variabilidad en tiempos de viaje
- Identifique rutas más eficientes según tiempos

---

## Ejemplos Prácticos

### Ejemplo 1: Red Básica de 3 Nodos

#### Archivo Excel

**Hoja NODOS**:
```
| NODO | ID | NOMBRE      |
|------|----|-------------|
| A    | 1  | Centro      |
| B    | 2  | Norte       |
| C    | 3  | Sur         |
```

**Hoja ARCOS**:
```
| ORIGEN | DESTINO | DISTANCIA | SEGURIDAD | LUMINOSIDAD | INCLINACION |
|--------|---------|-----------|-----------|-------------|-------------|
| A      | B       | 100       | 8         | 7           | 2.0         |
| A      | C       | 80        | 9         | 8           | 1.0         |
| B      | C       | 120       | 7         | 6           | 3.0         |
```

#### Pasos de Uso

1. Crear el archivo Excel con las dos hojas
2. Ejecutar la aplicación
3. Cargar el archivo Excel
4. Configurar velocidad mínima: 10 m/s, máxima: 15 m/s
5. Configurar duración: 300 segundos
6. Crear nueva simulación
7. Iniciar simulación
8. Observar el movimiento de ciclistas

### Ejemplo 2: Red con Perfiles y Rutas

#### Archivo Excel Completo

**Hoja NODOS**:
```
| NODO | ID | NOMBRE      | LAT      | LON       |
|------|----|-------------|----------|-----------|
| A    | 1  | Universidad | 4.6097   | -74.0817  |
| B    | 2  | Centro      | 4.6100   | -74.0820  |
| C    | 3  | Parque      | 4.6095   | -74.0815  |
```

**Hoja ARCOS**:
```
| ORIGEN | DESTINO | DISTANCIA | SEGURIDAD | LUMINOSIDAD | INCLINACION |
|--------|---------|-----------|-----------|-------------|-------------|
| A      | B       | 150       | 8         | 7           | 1.5         |
| B      | C       | 100       | 9         | 8           | 0.5         |
| C      | A       | 200       | 7         | 6           | 2.0         |
```

**Hoja PERFILES**:
```
| PERFILES | PROBABILIDAD | DISTANCIA | SEGURIDAD | LUMINOSIDAD | INCLINACION |
|----------|--------------|-----------|-----------|-------------|-------------|
| 1        | 0.5          | 0.5       | 0.3       | 0.1         | 0.1         |
| 2        | 0.3          | 0.2       | 0.5       | 0.2         | 0.1         |
| 3        | 0.2          | 0.3       | 0.2       | 0.3         | 0.2         |
```

**Hoja RUTAS**:
```
| NODO | A    | B    | C    |
|------|------|------|------|
| A    | 0.0  | 0.6  | 0.4  |
| B    | 0.4  | 0.0  | 0.6  |
| C    | 0.5  | 0.5  | 0.0  |
```

#### Interpretación

- **Perfil 1** (50%): Prioriza distancia corta
- **Perfil 2** (30%): Prioriza seguridad
- **Perfil 3** (20%): Balance entre atributos
- **Desde A**: 60% va a B, 40% a C
- **Desde B**: 40% va a A, 60% a C
- **Desde C**: 50% va a A, 50% a B

---

## Preguntas Frecuentes

### ¿Puedo usar coordenadas geográficas reales?

Sí, si incluye columnas `LAT` y `LON` en la hoja NODOS, el sistema calculará automáticamente las distancias usando la fórmula de Haversine, que es apropiada para distancias urbanas.

### ¿Qué pasa si las probabilidades en PERFILES no suman 1.0?

El sistema normalizará automáticamente las probabilidades para que sumen 1.0. Sin embargo, es recomendable que sumen 1.0 desde el inicio para mayor precisión.

### ¿Puedo agregar más atributos además de los mencionados?

Sí, puede agregar cualquier atributo numérico en la hoja ARCOS. Sin embargo, solo los atributos que también aparezcan en PERFILES serán considerados para el cálculo de rutas.

### ¿Cómo afecta la inclinación al comportamiento?

La inclinación **no afecta la selección de ruta**, solo la velocidad durante el movimiento:
- Inclinación positiva (subida): reduce velocidad
- Inclinación negativa (bajada): aumenta velocidad
- Inclinación cero: velocidad normal

### ¿Qué distribución debo usar para cada nodo?

- **Exponencial**: La más común, modela arribos aleatorios
- **Normal**: Si hay patrones de arribo más regulares
- **Otras**: Para casos específicos o experimentación

### ¿Puedo pausar y modificar parámetros durante la simulación?

Puede pausar la simulación, pero para aplicar cambios en parámetros debe crear una nueva simulación (botón NUEVA).

### ¿Los resultados se guardan automáticamente?

Sí, al finalizar una simulación se genera automáticamente un archivo Excel con resultados en la carpeta `resultados/`.

### ¿Puedo simular más de 1000 ciclistas simultáneos?

El sistema está configurado para un máximo de 1000 ciclistas simultáneos por defecto. Para más ciclistas, puede modificar el parámetro en `config.py`, pero esto puede afectar el rendimiento.

### ¿Qué formato de archivo Excel debo usar?

Se recomienda usar `.xlsx` (Excel 2007 o superior). El formato `.xls` también es soportado pero puede tener limitaciones.

### ¿Cómo interpreto que un arco tiene alta utilización?

En los resultados exportados, consulte la hoja "Arcos Utilizados". Los arcos con mayor frecuencia indican segmentos más transitados, lo cual puede indicar necesidad de infraestructura adicional o posibles cuellos de botella.

---

## Conclusión

Este manual proporciona una guía completa para utilizar el Simulador de Ciclorutas. Para información más detallada sobre:

- **Visión general del proyecto**: Consulte **[README.md](README.md)**
- **Instalación y configuración**: Consulte **[README_INSTALACION.md](README_INSTALACION.md)**
- **Arquitectura técnica**: Consulte **[README_ARQUITECTURA.md](README_ARQUITECTURA.md)**
- **Modelo de simulación**: Consulte **[README_MODELO_SIMULACION.md](README_MODELO_SIMULACION.md)**

Para soporte adicional o preguntas, consulte la documentación técnica o contacte a los desarrolladores.

---

## 📤 Compartir Resultados y Uso Académico

### Exportar y Compartir Resultados

Los archivos Excel generados pueden ser compartidos con:

- **Colegas investigadores**: Para análisis colaborativo
- **Supervisores académicos**: Para revisión y validación
- **Publicaciones**: Como datos suplementarios de investigación
- **Presentaciones**: Para visualización en conferencias

**Formato recomendado para compartir**:
- Incluye el archivo Excel completo con todas las hojas
- Proporciona contexto sobre los parámetros de simulación
- Menciona la versión del simulador utilizada
- Incluye información sobre el grafo utilizado

### Uso en Investigación Académica

Esta herramienta está diseñada para investigación académica. Al usar los resultados:

1. **Cita el simulador**: Incluye la cita apropiada (ver `README.md`)
2. **Documenta parámetros**: Registra todos los parámetros de simulación utilizados
3. **Valida resultados**: Compara con datos reales cuando sea posible
4. **Comparte metodología**: Describe cómo se utilizó la herramienta en tu investigación

### Análisis de Resultados para Publicación

**Para análisis cuantitativo**:
- Usa la hoja "Ciclistas" para análisis estadísticos
- La hoja "Tramos" proporciona datos de infraestructura
- La hoja "Tiempos" permite análisis de eficiencia

**Para visualizaciones**:
- Los datos pueden importarse a herramientas como R, Python (pandas), o Excel
- Las estadísticas agregadas están en "Info Simulación"
- Los datos individuales permiten análisis detallados

### Reproducibilidad

Para asegurar reproducibilidad de resultados:

1. **Guarda configuración**: Documenta todos los parámetros utilizados
2. **Guarda archivo Excel de entrada**: El grafo utilizado
3. **Registra versión**: Anota la versión del simulador (v2.0)
4. **Documenta distribuciones**: Si modificaste distribuciones, documenta los cambios

### Compartir Configuraciones

Si desarrollas configuraciones útiles:

- **Comparte archivos Excel**: Los archivos de entrada pueden ser reutilizados
- **Documenta parámetros**: Crea un documento con parámetros recomendados
- **Comparte resultados**: Los resultados pueden servir como casos de estudio

---

**Versión del Manual**: 2.0  
**Última actualización**: 2024

