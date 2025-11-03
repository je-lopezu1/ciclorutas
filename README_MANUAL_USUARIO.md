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
- [Ejemplos Prácticos](#ejemplos-prácticos)
- [Preguntas Frecuentes](#preguntas-frecuentes)

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

#### Rutas Utilizadas

- **Muchas rutas diferentes**: Ciclistas distribuyen bien por la red
- **Pocas rutas**: Posible concentración en ciertos corredores
- **Ruta más usada**: Corredor principal o más atractivo según perfiles

---

## Exportación de Datos

### Generación Automática de Resultados

Al finalizar una simulación (por tiempo o manualmente), el sistema genera automáticamente un archivo Excel con resultados en la carpeta `resultados/`.

### Contenido del Archivo de Resultados

El archivo Excel generado contiene varias hojas:

#### Hoja "Resumen General"

- Estadísticas agregadas de la simulación
- Total de ciclistas generados
- Total de viajes completados
- Tiempo total de simulación
- Métricas de velocidad

#### Hoja "Rutas Utilizadas"

- Lista de todas las rutas utilizadas
- Frecuencia de uso de cada ruta
- Porcentaje del total

#### Hoja "Arcos Utilizados"

- Lista de todos los arcos/tramos utilizados
- Frecuencia de uso de cada arco
- Utilización por segmento

#### Hoja "Ciclistas por Nodo"

- Número de ciclistas generados por cada nodo
- Actividad de cada nodo como origen

#### Hoja "Perfiles Utilizados"

- Distribución de perfiles asignados
- Porcentaje de cada perfil

#### Hoja "Tiempos de Viaje"

- Tiempo promedio de viaje por ruta
- Tiempo total de viaje por ciclista
- Tiempos por tramo

### Ubicación de Archivos

Los archivos se guardan en:
```
resultados/
├── resultados_simulacion_YYYYMMDD_HHMMSS.xlsx
└── ...
```

Donde `YYYYMMDD_HHMMSS` es la fecha y hora de generación.

### Análisis de Resultados

Los archivos Excel generados pueden ser:
- Abiertos en Excel, Google Sheets, o cualquier herramienta de análisis
- Importados a herramientas de análisis de datos (Python, R, etc.)
- Usados para generar reportes y visualizaciones adicionales

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

- **Instalación y configuración**: Consulte `README_INSTALACION.md`
- **Arquitectura técnica**: Consulte `README_ARQUITECTURA.md`
- **Modelo de simulación**: Consulte `README_MODELO_SIMULACION.md`

Para soporte adicional o preguntas, consulte la documentación técnica o contacte a los desarrolladores.

---

**Versión del Manual**: 1.0  
**Última actualización**: 2024

