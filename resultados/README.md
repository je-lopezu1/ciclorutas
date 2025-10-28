# 📊 Generación de Resultados Excel

Este directorio contiene los archivos Excel generados automáticamente al finalizar las simulaciones.

## 🎯 Características

### Generación Automática
- Los archivos Excel se generan automáticamente cuando:
  - La simulación termina naturalmente (por tiempo)
  - Se termina manualmente la simulación
  - Se completa una simulación

### Estructura del Archivo Excel

Cada archivo Excel contiene **4 hojas principales**:

#### 1. 📋 Hoja "Info Simulación"
Contiene información general y estadísticas de la simulación:
- **Información General**: Fecha, duración, estado final
- **Información del Grafo**: Nodos, arcos, conectividad
- **Estadísticas de Ciclistas**: Total creados, activos, completados, velocidades
- **Estadísticas de Rutas**: Rutas utilizadas, viajes totales, ruta más usada
- **Estadísticas de Nodos**: Nodo más activo
- **Estadísticas de Perfiles**: Distribución de perfiles de ciclistas

#### 2. 🛣️ Hoja "Tramos" (OPTIMIZADA)
Información detallada de cada tramo/arco de la red:
- **ID del Tramo**: Identificador único (origen->destino)
- **Nodos**: Origen y destino del tramo
- **Distancia**: Distancia real del tramo en metros
- **Estadísticas de Uso**: Número de ciclistas que lo usaron, porcentaje de uso
- **Tiempo Promedio**: Tiempo promedio de desplazamiento por el tramo
- **Atributos Importantes**: Solo seguridad, luminosidad e inclinación (si están disponibles)
- **Ordenamiento**: Los tramos se ordenan por uso (más usado primero)

#### 3. 🚴 Hoja "Ciclistas" (OPTIMIZADA)
Información detallada de cada ciclista y su viaje:
- **ID del Ciclista**: Identificador único
- **Ruta**: Origen, destino, ruta simple
- **Perfil**: Tipo de perfil y preferencias principales
- **Estadísticas del Viaje**: Número de tramos, distancia total, **tiempo total real**
- **Tramos Utilizados**: Lista resumida de tramos (máximo 5, con indicador de más)
- **Estado**: Estado final del ciclista
- **Preferencias**: Solo seguridad y luminosidad (las más importantes)

#### 4. ⏱️ Hoja "Tiempos" (NUEVA)
Estadísticas detalladas de tiempos de desplazamiento:
- **Estadísticas Generales**: Tiempo promedio, mínimo y máximo de viajes
- **Detalles por Ciclista**: Tiempo total, número de tramos, tiempo promedio por tramo
- **Tiempos por Tramo**: Lista de tiempos reales de cada tramo recorrido
- **Análisis de Eficiencia**: Comparación de tiempos entre diferentes rutas

## 📁 Nomenclatura de Archivos

Los archivos se nombran automáticamente con el formato:
```
{nombre_grafo}_{timestamp}.xlsx
```

Donde:
- `nombre_grafo`: Nombre del archivo Excel cargado (sin extensión)
- `timestamp`: Fecha y hora en formato YYYYMMDD_HHMMSS

Ejemplo: `red_ciclorutas_20241013_102345.xlsx`

## 🔧 Configuración

### Carpeta de Resultados
- Los archivos se guardan en la carpeta `resultados/`
- La carpeta se crea automáticamente si no existe
- Los archivos se acumulan para mantener un historial

### Atributos Dinámicos
El sistema detecta automáticamente los atributos disponibles en los datos:
- **Atributos Reales**: Solo se incluyen los atributos que existen en el grafo
- **Sin N/A**: Se evitan valores "N/A" reemplazándolos por "Sin datos"
- **Columnas Dinámicas**: Las columnas se crean según los atributos disponibles
- **Atributos Comunes**: Seguridad, Luminosidad, Inclinación (según disponibilidad)

### Personalización
El sistema permite personalizar:
- Nombre del grafo (se toma del archivo Excel cargado)
- Carpeta de destino (configurable en el código)
- Formato de las hojas (estructura fija pero extensible)

## 📈 Análisis de Resultados

### Para Análisis de Red
- Use la hoja "Tramos" para identificar:
  - Tramo más concurrido
  - Tramo menos utilizado
  - Distribución de uso por características

### Para Análisis de Comportamiento
- Use la hoja "Ciclistas" para analizar:
  - Patrones de rutas
  - Preferencias por perfil
  - Eficiencia de viajes

### Para Análisis General
- Use la hoja "Info Simulación" para:
  - Resumen ejecutivo
  - Validación de parámetros
  - Comparación entre simulaciones

## 🚀 Uso

1. **Ejecutar Simulación**: Inicia una simulación normal
2. **Esperar Finalización**: La simulación termina automáticamente o manualmente
3. **Archivo Generado**: Se crea automáticamente en `resultados/`
4. **Notificación**: Se muestra la ruta del archivo generado
5. **Análisis**: Abrir el archivo Excel para análisis detallado

## ⚠️ Notas Importantes

- Los archivos se generan solo si la simulación tiene datos válidos
- Si hay errores, se muestra un mensaje de advertencia
- Los archivos se pueden abrir con Excel, LibreOffice Calc, o Google Sheets
- Se recomienda hacer backup de archivos importantes antes de nuevas simulaciones
