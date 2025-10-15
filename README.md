# 🚴 Simulador de Ciclorutas v2.0

Sistema completo de simulación de redes de ciclorutas con interfaz gráfica modular y control avanzado.

## 📋 Tabla de Contenidos

- [Características Principales](#-características-principales)
- [Requisitos del Sistema](#-requisitos-del-sistema)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Ejecución](#-ejecución)
- [Uso del Sistema](#-uso-del-sistema)
- [Formato de Archivos](#-formato-de-archivos)
- [Arquitectura](#-arquitectura)
- [Solución de Problemas](#-solución-de-problemas)
- [Contribuciones](#-contribuciones)

## 🎯 Características Principales

- **Simulación en tiempo real** de ciclistas en redes complejas de ciclorutas
- **Interfaz gráfica modular** con componentes reutilizables y mantenibles
- **Carga de grafos desde Excel** con soporte para múltiples atributos
- **Sistema de distribuciones de probabilidad** para modelar arribos realistas
- **Perfiles de ciclistas personalizables** con preferencias de ruta
- **Visualización dinámica** con matplotlib mostrando movimiento en tiempo real
- **Estadísticas detalladas** actualizadas en tiempo real
- **Arquitectura escalable** con separación clara de responsabilidades

## 💻 Requisitos del Sistema

### Requisitos Mínimos
- **Python**: 3.7 o superior
- **Sistema Operativo**: Windows 10/11, macOS 10.14+, Linux Ubuntu 18.04+
- **RAM**: 4 GB mínimo, 8 GB recomendado
- **Espacio en disco**: 500 MB para instalación

### Dependencias Principales
- `simpy` >= 4.0.0 - Simulación de eventos discretos
- `matplotlib` >= 3.5.0 - Visualización y gráficos
- `numpy` >= 1.20.0 - Computación numérica
- `pandas` >= 1.5.0 - Análisis de datos
- `networkx` >= 3.0 - Análisis de redes y grafos
- `scipy` >= 1.9.0 - Computación científica
- `openpyxl` >= 3.0.0 - Manejo de archivos Excel
- `tkinter` - Interfaz gráfica (incluida con Python)

## 🚀 Instalación

### 1. Clonar o Descargar el Proyecto

```bash
# Si tienes Git instalado
git clone <url-del-repositorio>
cd ciclorutas

# O descarga y extrae el archivo ZIP en una carpeta
```

### 2. Verificar Python

```bash
# Verificar versión de Python
python --version
# Debe mostrar Python 3.7 o superior

# O usar python3 en algunos sistemas
python3 --version
```

### 3. Crear Entorno Virtual (Recomendado)

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate

# En macOS/Linux:
source venv/bin/activate
```

### 4. Instalar Dependencias

#### Opción A: Instalación Automática (Recomendada)
```bash
# Instalar todas las dependencias desde requirements.txt
pip install -r requirements.txt
```

#### Opción B: Instalación Manual
```bash
# Instalar dependencias una por una
pip install simpy>=4.0.0
pip install matplotlib>=3.5.0
pip install numpy>=1.20.0
pip install pandas>=1.5.0
pip install networkx>=3.0
pip install scipy>=1.9.0
pip install openpyxl>=3.0.0
```

#### Opción C: Instalación con Conda
```bash
# Si usas Anaconda/Miniconda
conda install simpy matplotlib numpy pandas networkx scipy openpyxl
```

### 5. Verificar Instalación

```bash
# Verificar que todas las dependencias estén instaladas
python -c "import simpy, matplotlib, numpy, pandas, networkx, scipy, openpyxl, tkinter; print('✅ Todas las dependencias están instaladas correctamente')"
```

## ⚙️ Configuración

### Configuración Básica

El sistema viene preconfigurado con valores por defecto. Puedes modificar la configuración editando el archivo `config.py`:

```python
# Parámetros de simulación por defecto
SIMULACION_DEFAULTS = {
    'velocidad_minima': 10.0,      # m/s
    'velocidad_maxima': 15.0,      # m/s
    'duracion_simulacion': 300.0,  # segundos (5 minutos)
    'max_ciclistas_simultaneos': 1000
}
```

### Configuración de la Interfaz

```python
# Configuración de la ventana principal
APP_CONFIG = {
    'titulo_ventana': '🚴 Simulador de Ciclorutas - Control Avanzado',
    'tamaño_ventana': (1400, 900),
    'tamaño_minimo': (800, 600),
    'centrar_ventana': True,
    'resizable': True
}
```

## ▶️ Ejecución

### Método 1: Ejecución Directa (Recomendada)

```bash
# Desde la carpeta del proyecto
python main.py
```

### Método 2: Ejecución con Verificación de Dependencias

```bash
# El sistema verificará automáticamente las dependencias
python main.py
```

### Método 3: Ejecución en Modo Debug

```bash
# Para ver mensajes detallados de depuración
python -u main.py
```

### Método 4: Ejecución desde Código

```python
# Desde Python
from Interfaz import InterfazSimulacion
import tkinter as tk

root = tk.Tk()
app = InterfazSimulacion(root)
root.mainloop()
```

## 🎮 Uso del Sistema

### 1. Inicio del Sistema

Al ejecutar `python main.py`, se abrirá la interfaz gráfica con:

- **Panel de Control**: Configuración de parámetros y controles de simulación
- **Panel de Visualización**: Gráfico en tiempo real de la red de ciclorutas
- **Panel de Estadísticas**: Estadísticas detalladas en tiempo real
- **Panel de Distribuciones**: Configuración de distribuciones y perfiles

### 2. Cargar Red de Ciclorutas

1. Haz clic en **"Cargar Grafo"** en el panel de control
2. Selecciona un archivo Excel con el formato correcto
3. El sistema validará y cargará la red automáticamente

### 3. Configurar Parámetros

- **Velocidad mínima**: 1.0-20.0 m/s
- **Velocidad máxima**: 1.0-30.0 m/s  
- **Duración**: 60-3600 segundos
- **Distribuciones**: Configurar por nodo en el panel correspondiente

### 4. Iniciar Simulación

1. Configura los parámetros deseados
2. Haz clic en **"NUEVA"** para crear una nueva simulación
3. Haz clic en **"INICIAR"** para comenzar la simulación
4. Observa la visualización en tiempo real y las estadísticas

### 5. Controles de Simulación

- **NUEVA**: Crear nueva simulación
- **INICIAR**: Iniciar la simulación
- **PAUSAR/REANUDAR**: Pausar o reanudar
- **TERMINAR**: Terminar llevando al final
- **ADELANTAR**: Adelantar 10 pasos
- **REINICIAR**: Reiniciar la simulación actual

## 📁 Formato de Archivos

### Archivos Excel Soportados

El sistema requiere archivos Excel (.xlsx o .xls) con las siguientes hojas:

#### Hoja "NODOS" (Obligatoria)
| NODO | ID | NOMBRE |
|------|----|---------| 
| A    | 1  | Nodo A  |
| B    | 2  | Nodo B  |
| C    | 3  | Nodo C  |

#### Hoja "ARCOS" (Obligatoria)
| ORIGEN | DESTINO | DISTANCIA | SEGURIDAD | LUMINOSIDAD | INCLINACION |
|--------|---------|-----------|-----------|-------------|-------------|
| A      | B       | 50        | 8         | 7           | 1.5         |
| B      | C       | 30        | 6         | 5           | 2.0         |
| C      | A       | 40        | 9         | 8           | 0.5         |

#### Hoja "PERFILES" (Opcional)
| PERFILES | DISTANCIA | SEGURIDAD | LUMINOSIDAD | INCLINACION |
|----------|-----------|-----------|-------------|-------------|
| 1        | 0.4       | 0.3       | 0.2         | 0.1         |
| 2        | 0.2       | 0.5       | 0.2         | 0.1         |
| 3        | 0.3       | 0.2       | 0.3         | 0.2         |

#### Hoja "RUTAS" (Opcional)
| NODO | A    | B    | C    |
|------|------|------|------|
| A    | 0.0  | 0.6  | 0.4  |
| B    | 0.3  | 0.0  | 0.7  |
| C    | 0.5  | 0.5  | 0.0  |

### Archivos de Ejemplo

El proyecto incluye archivos de ejemplo:
- `Libro2.xlsx` - Red de ejemplo básica
- `Libro2_actualizado.xlsx` - Red de ejemplo con atributos adicionales

## 🏗️ Arquitectura

### Estructura del Proyecto

```
ciclorutas/
├── main.py                          # Punto de entrada del sistema
├── config.py                        # Configuración centralizada
├── requirements.txt                 # Dependencias del proyecto
├── README.md                        # Este archivo
├── ARQUITECTURA.md                  # Documentación de arquitectura
├── Libro2.xlsx                      # Archivo de ejemplo
├── Libro2_actualizado.xlsx          # Archivo de ejemplo actualizado
├── Simulador/                       # Módulo del motor de simulación
│   ├── __init__.py
│   ├── core/                        # Componentes principales
│   │   ├── simulador.py            # Motor principal de simulación
│   │   └── configuracion.py        # Configuración de simulación
│   ├── models/                      # Modelos de datos
│   │   └── ciclista.py             # Modelo de ciclista y pool
│   ├── distributions/               # Distribuciones de probabilidad
│   │   └── distribucion_nodo.py    # Distribuciones por nodo
│   └── utils/                       # Utilidades del simulador
│       ├── estadisticas_utils.py   # Utilidades de estadísticas
│       ├── generador_excel.py      # Generador de archivos Excel
│       ├── grafo_utils.py          # Utilidades para grafos NetworkX
│       └── rutas_utils.py          # Utilidades de rutas
└── Interfaz/                        # Módulo de la interfaz gráfica
    ├── __init__.py
    ├── components/                  # Componentes principales
    │   └── app_principal.py        # Aplicación principal
    ├── panels/                      # Paneles de la interfaz
    │   ├── panel_control.py        # Panel de control
    │   ├── panel_visualizacion.py  # Panel de visualización
    │   ├── panel_estadisticas.py   # Panel de estadísticas
    │   └── panel_distribuciones.py # Panel de distribuciones
    └── utils/                       # Utilidades de la interfaz
        ├── archivo_utils.py        # Utilidades de archivos
        ├── cache_utils.py          # Utilidades de caché
        └── estilo_utils.py         # Utilidades de estilo
```

### Componentes Principales

#### 🎮 Simulador (Paquete Simulador)
- **`SimuladorCiclorutas`**: Motor principal de simulación con SimPy
- **`ConfiguracionSimulacion`**: Gestión centralizada de configuración
- **`Ciclista`**: Modelo optimizado de ciclista individual
- **`PoolCiclistas`**: Sistema de reutilización de objetos para eficiencia
- **`DistribucionNodo`**: Sistema de distribuciones de probabilidad por nodo

#### 🖥️ Interfaz (Paquete Interfaz)
- **`InterfazSimulacion`**: Aplicación principal de la interfaz
- **`PanelControl`**: Control de parámetros y botones de simulación
- **`PanelVisualizacion`**: Visualización en tiempo real con matplotlib
- **`PanelEstadisticas`**: Estadísticas detalladas en tiempo real
- **`PanelDistribuciones`**: Configuración de distribuciones y perfiles

## 🐛 Solución de Problemas

### Problemas Comunes y Soluciones

#### 1. Error de Dependencias
```
❌ ERROR: Faltan las siguientes dependencias: simpy
```

**Solución:**
```bash
pip install simpy matplotlib numpy pandas networkx scipy openpyxl
```

#### 2. Ventana no se Abre
```
❌ ERROR: No se pudo importar la interfaz
```

**Soluciones:**
- Verificar que tkinter esté instalado: `python -c "import tkinter"`
- En Ubuntu/Debian: `sudo apt-get install python3-tk`
- En CentOS/RHEL: `sudo yum install tkinter`

#### 3. Simulación Muy Lenta
**Soluciones:**
- Reducir el número máximo de ciclistas
- Aumentar la velocidad de simulación
- Usar grafos más pequeños para pruebas

#### 4. Error de Carga de Archivo Excel
```
❌ ERROR: No se pudo cargar el archivo
```

**Soluciones:**
- Verificar que el archivo tenga las hojas "NODOS" y "ARCOS"
- Verificar que las columnas tengan los nombres correctos
- Usar archivos .xlsx en lugar de .xls si es posible

#### 5. Problemas de Memoria
**Soluciones:**
- Reducir la duración de la simulación
- Reducir el número máximo de ciclistas
- Cerrar otras aplicaciones que consuman memoria

### Comandos de Diagnóstico

```bash
# Verificar versión de Python
python --version

# Verificar dependencias instaladas
pip list

# Verificar importaciones
python -c "import simpy, matplotlib, numpy, pandas, networkx, scipy, openpyxl, tkinter; print('✅ OK')"

# Ejecutar en modo verbose
python -v main.py

# Verificar estructura del proyecto
python -c "import os; print(os.listdir('.'))"
```

### Logs y Debugging

El sistema incluye logging detallado. Para activar el modo debug:

```python
# En config.py, cambiar el nivel de logging
LOGGING_CONFIG = {
    'nivel': 'DEBUG',  # Cambiar de 'INFO' a 'DEBUG'
    'formato': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'archivo': 'simulador.log'
}
```

## 📊 Estadísticas y Métricas

### Estadísticas en Tiempo Real

El sistema proporciona las siguientes estadísticas:

#### Estadísticas Básicas
- **Ciclistas Activos**: Número de ciclistas actualmente en movimiento
- **Velocidad Promedio**: Velocidad promedio de todos los ciclistas
- **Velocidad Mínima/Máxima**: Rango de velocidades actual
- **Tiempo de Simulación**: Tiempo transcurrido desde el inicio

#### Estadísticas del Grafo
- **Nodos del Grafo**: Número total de nodos en la red
- **Arcos del Grafo**: Número total de conexiones
- **Modo de Simulación**: Grafo real vs. sistema original
- **Atributos Disponibles**: Número de atributos en el grafo

#### Estadísticas de Distribuciones
- **Distribuciones Configuradas**: Número de nodos con distribuciones
- **Tasa de Arribo Promedio**: Tasa promedio de llegada de ciclistas
- **Duración**: Duración configurada de la simulación

#### Estadísticas de Rutas
- **Rutas Utilizadas**: Número de rutas diferentes utilizadas
- **Total de Viajes**: Número total de viajes completados
- **Ruta Más Usada**: Ruta con mayor frecuencia de uso
- **Nodo Más Activo**: Nodo que genera más ciclistas

## 🔧 Configuración Avanzada

### Personalización de Distribuciones

```python
# Configurar distribución exponencial para un nodo
simulador.actualizar_distribucion_nodo('A', 'exponencial', {'lambda': 0.5})

# Configurar distribución uniforme para otro nodo
simulador.actualizar_distribucion_nodo('B', 'uniforme', {'min': 1.0, 'max': 5.0})

# Configurar distribución de Poisson
simulador.actualizar_distribucion_nodo('C', 'poisson', {'lambda': 2.0})
```

### Personalización de Perfiles

```python
# Crear perfil personalizado
perfil = {
    'distancia': 0.4,      # 40% de importancia
    'seguridad': 0.3,      # 30% de importancia
    'luminosidad': 0.2,    # 20% de importancia
    'inclinacion': 0.1     # 10% de importancia
}
```

### Configuración de Rendimiento

```python
# En config.py
RENDIMIENTO_CONFIG = {
    'max_rutas_por_perfil': 100,
    'max_rutas_total': 500,
    'intervalo_actualizacion_cache': 0.1,  # 100ms
    'max_trayectoria_puntos': 50,
    'max_tiempo_inactivo': 300.0,  # 5 minutos
    'tamaño_pool_ciclistas': 100,
    'tamaño_maximo_pool': 1000
}
```

## 🤝 Contribuciones

Este es un proyecto de simulación académica. Las contribuciones son bienvenidas para:

### Áreas de Mejora
- **Interfaz gráfica**: Mejoras en la usabilidad y diseño
- **Rendimiento**: Optimizaciones de velocidad y memoria
- **Nuevas características**: Funcionalidades adicionales de simulación
- **Documentación**: Mejoras en la documentación y ejemplos
- **Nuevos tipos de distribuciones**: Implementación de distribuciones adicionales
- **Visualización**: Mejoras en la visualización y gráficos

### Cómo Contribuir

1. **Fork** del repositorio
2. **Crear** una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. **Commit** de tus cambios (`git commit -am 'Agregar nueva característica'`)
4. **Push** a la rama (`git push origin feature/nueva-caracteristica`)
5. **Crear** un Pull Request

### Estándares de Código

- Usar **PEP 8** para estilo de código Python
- Incluir **docstrings** para todas las funciones y clases
- Agregar **comentarios** explicativos para lógica compleja
- Incluir **tests** para nuevas funcionalidades
- Actualizar **documentación** cuando sea necesario

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver el archivo LICENSE para más detalles.

## 👨‍💻 Autor

**Sistema de Simulación de Ciclorutas** - Proyecto Académico v2.0

---

## 🚀 Comandos Rápidos de Instalación

### Instalación Completa en una Línea

```bash
# Clonar, instalar dependencias y ejecutar
git clone <url> && cd ciclorutas && pip install -r requirements.txt && python main.py
```

### Verificación Rápida

```bash
# Verificar que todo esté funcionando
python -c "import simpy, matplotlib, numpy, pandas, networkx, scipy, openpyxl, tkinter; print('✅ Sistema listo para usar')"
```

### Ejecución con Logs

```bash
# Ejecutar con logs detallados
python -u main.py 2>&1 | tee simulador.log
```

---

**¡Disfruta simulando redes de ciclorutas! 🚴‍♂️🚴‍♀️**

Para más información detallada sobre la arquitectura del sistema, consulta el archivo `ARQUITECTURA.md`.