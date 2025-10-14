# 🚴 Simulador de Ciclorutas v2.0

Sistema completo de simulación de redes de ciclorutas con interfaz gráfica modular y control avanzado.

## 🎯 Características Principales

- **Simulación en tiempo real** de ciclistas en redes complejas de ciclorutas
- **Interfaz gráfica modular** con componentes reutilizables y mantenibles
- **Carga de grafos desde Excel** con soporte para múltiples atributos
- **Sistema de distribuciones de probabilidad** para modelar arribos realistas
- **Perfiles de ciclistas personalizables** con preferencias de ruta
- **Visualización dinámica** con matplotlib mostrando movimiento en tiempo real
- **Estadísticas detalladas** actualizadas en tiempo real
- **Arquitectura escalable** con separación clara de responsabilidades

## 🏗️ Arquitectura del Sistema

### Estructura Modular

```
ciclorutas/
├── main.py                          # Punto de entrada del sistema
├── config.py                        # Configuración centralizada
├── requirements.txt                 # Dependencias del proyecto
├── README.md                        # Documentación del proyecto
├── Simulador/                       # Módulo del motor de simulación
│   ├── __init__.py
│   ├── core/                        # Componentes principales
│   │   ├── __init__.py
│   │   ├── simulador.py            # Motor principal de simulación
│   │   └── configuracion.py        # Configuración de simulación
│   ├── models/                      # Modelos de datos
│   │   ├── __init__.py
│   │   └── ciclista.py             # Modelo de ciclista y pool
│   ├── distributions/               # Distribuciones de probabilidad
│   │   ├── __init__.py
│   │   └── distribucion_nodo.py    # Distribuciones por nodo
│   └── utils/                       # Utilidades del simulador
│       ├── __init__.py
│       └── grafo_utils.py          # Utilidades para grafos NetworkX
└── Interfaz/                        # Módulo de la interfaz gráfica
    ├── __init__.py
    ├── components/                  # Componentes principales
    │   ├── __init__.py
    │   └── app_principal.py        # Aplicación principal
    ├── panels/                      # Paneles de la interfaz
    │   ├── __init__.py
    │   ├── panel_control.py        # Panel de control
    │   ├── panel_visualizacion.py  # Panel de visualización
    │   ├── panel_estadisticas.py   # Panel de estadísticas
    │   └── panel_distribuciones.py # Panel de distribuciones
    └── utils/                       # Utilidades de la interfaz
        ├── __init__.py
        ├── estilo_utils.py         # Utilidades de estilo
        └── archivo_utils.py        # Utilidades de archivos
```

### Componentes Principales

#### 🎮 Simulador (Paquete Simulador)
- **`SimuladorCiclorutas`**: Motor principal de simulación con SimPy
- **`ConfiguracionSimulacion`**: Gestión centralizada de configuración
- **`Ciclista`**: Modelo optimizado de ciclista individual
- **`PoolCiclistas`**: Sistema de reutilización de objetos para eficiencia
- **`DistribucionNodo`**: Sistema de distribuciones de probabilidad por nodo
- **`GrafoUtils`**: Utilidades para manejo de grafos NetworkX

#### 🖥️ Interfaz (Paquete Interfaz)
- **`InterfazSimulacion`**: Aplicación principal de la interfaz
- **`PanelControl`**: Control de parámetros y botones de simulación
- **`PanelVisualizacion`**: Visualización en tiempo real con matplotlib
- **`PanelEstadisticas`**: Estadísticas detalladas en tiempo real
- **`PanelDistribuciones`**: Configuración de distribuciones y perfiles
- **`EstiloUtils`**: Utilidades de estilo y tema
- **`ArchivoUtils`**: Utilidades para carga y validación de archivos

## 🚀 Instalación y Uso

### Requisitos del Sistema

- Python 3.7 o superior
- Dependencias: simpy, matplotlib, numpy, pandas, networkx, scipy, tkinter

### Instalación de Dependencias

   ```bash
pip install simpy matplotlib numpy pandas networkx scipy
   ```

### Ejecución

```bash
python main.py
```

## 📁 Formato de Archivos Excel

### Estructura Requerida

El sistema soporta archivos Excel con las siguientes hojas:

#### Hoja "NODOS" (Obligatoria)
| NODO | ID | NOMBRE |
|------|----|---------|
| A    | 1  | Nodo A  |
| B    | 2  | Nodo B  |

#### Hoja "ARCOS" (Obligatoria)
| ORIGEN | DESTINO | DISTANCIA | SEGURIDAD | LUMINOSIDAD | INCLINACION |
|--------|---------|-----------|-----------|-------------|-------------|
| A      | B       | 50        | 8         | 7           | 1.5         |
| B      | C       | 30        | 6         | 5           | 2.0         |

#### Hoja "PERFILES" (Opcional)
| PERFILES | DISTANCIA | SEGURIDAD | LUMINOSIDAD | INCLINACION |
|----------|-----------|-----------|-------------|-------------|
| 1        | 0.4       | 0.3       | 0.2         | 0.1         |
| 2        | 0.2       | 0.5       | 0.2         | 0.1         |

#### Hoja "RUTAS" (Opcional)
| NODO | A    | B    | C    |
|------|------|------|------|
| A    | 0.0  | 0.6  | 0.4  |
| B    | 0.3  | 0.0  | 0.7  |

## 🎮 Controles Disponibles

### Parámetros de Simulación
- **Velocidad mínima**: 1.0-20.0 m/s
- **Velocidad máxima**: 1.0-30.0 m/s
- **Duración de simulación**: 60-3600 segundos
- **Distribuciones de probabilidad** por nodo
- **Perfiles de ciclistas** personalizables

### Controles de Simulación
- **NUEVA**: Crear nueva simulación con parámetros actuales
- **INICIAR**: Iniciar la simulación
- **PAUSAR/REANUDAR**: Pausar o reanudar la simulación
- **TERMINAR**: Terminar la simulación llevándola al final
- **ADELANTAR**: Adelantar la simulación 10 pasos
- **REINICIAR**: Reiniciar la simulación actual

### Controles de Visualización
- **Cargar Grafo**: Cargar red de ciclorutas desde Excel
- **Seleccionar Atributo**: Visualizar diferentes atributos del grafo
- **Aplicar Visualización**: Actualizar la visualización

## 📊 Estadísticas en Tiempo Real

### Estadísticas Básicas
- **Ciclistas Activos**: Número de ciclistas actualmente en movimiento
- **Velocidad Promedio**: Velocidad promedio de todos los ciclistas
- **Velocidad Mínima/Máxima**: Rango de velocidades actual
- **Tiempo de Simulación**: Tiempo transcurrido desde el inicio

### Estadísticas del Grafo
- **Nodos del Grafo**: Número total de nodos en la red
- **Arcos del Grafo**: Número total de conexiones
- **Modo de Simulación**: Grafo real vs. sistema original
- **Atributos Disponibles**: Número de atributos en el grafo

### Estadísticas de Distribuciones
- **Distribuciones Configuradas**: Número de nodos con distribuciones
- **Tasa de Arribo Promedio**: Tasa promedio de llegada de ciclistas
- **Duración**: Duración configurada de la simulación

### Estadísticas de Rutas
- **Rutas Utilizadas**: Número de rutas diferentes utilizadas
- **Total de Viajes**: Número total de viajes completados
- **Ruta Más Usada**: Ruta con mayor frecuencia de uso
- **Nodo Más Activo**: Nodo que genera más ciclistas

## 🔧 Configuración Avanzada

### Configuración Centralizada

El archivo `config.py` contiene toda la configuración del sistema:

```python
# Parámetros de simulación
SIMULACION_DEFAULTS = {
    'velocidad_minima': 10.0,
    'velocidad_maxima': 15.0,
    'duracion_simulacion': 300.0,
    'max_ciclistas_simultaneos': 1000
}

# Configuración de visualización
MATPLOTLIB_CONFIG = {
    'figsize': (10, 6),
    'tamano_ciclista': 120,
    'alpha_ciclista': 0.95
}
```

### Personalización de Distribuciones

```python
# Configurar distribución exponencial para un nodo
simulador.actualizar_distribucion_nodo('A', 'exponencial', {'lambda': 0.5})

# Configurar distribución uniforme para otro nodo
simulador.actualizar_distribucion_nodo('B', 'uniforme', {'min': 1.0, 'max': 5.0})
```

### Personalización de Perfiles

```python
# Crear perfil personalizado
perfil = {
    'distancia': 0.4,
    'seguridad': 0.3,
    'luminosidad': 0.2,
    'inclinacion': 0.1
}
```

## 📈 Rendimiento y Optimización

### Características de Rendimiento

- **Sistema de Pool de Objetos**: Reutilización eficiente de ciclistas
- **Gestión de Memoria Inteligente**: Limpieza automática de ciclistas antiguos
- **Cache de Datos**: Actualización optimizada de la interfaz
- **Límites Adaptativos**: Configuración automática según el tamaño del grafo
- **Control de Frecuencia**: Actualización de interfaz cada 50ms

### Límites del Sistema

- **Máximo de ciclistas**: 5000 ciclistas simultáneos
- **Duración máxima**: 3600 segundos (1 hora)
- **Tamaño de grafo**: Sin límite práctico
- **Frecuencia de actualización**: 20 FPS para visualización suave

## 🐛 Solución de Problemas

### Problemas Comunes

1. **Error de dependencias**: Instala todas las dependencias con `pip install -r requirements.txt`
2. **Ventana no se abre**: Verifica que tkinter esté instalado correctamente
3. **Simulación lenta**: Reduce el número de ciclistas o ajusta los límites
4. **Error de carga de archivo**: Verifica el formato del archivo Excel

### Logs y Debugging

El sistema incluye logging detallado para debugging. Revisa la consola para mensajes informativos.

## 🤝 Contribuciones

Este es un proyecto de simulación académica. Las contribuciones son bienvenidas para:

- Mejoras en la interfaz gráfica
- Optimizaciones de rendimiento
- Nuevas características de simulación
- Documentación y ejemplos
- Nuevos tipos de distribuciones
- Mejoras en la visualización

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver el archivo LICENSE para más detalles.

## 👨‍💻 Autor

Sistema de Simulación de Ciclorutas - Proyecto Académico v2.0

---

**¡Disfruta simulando redes de ciclorutas! 🚴‍♂️🚴‍♀️**