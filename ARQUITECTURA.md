# 🏗️ Arquitectura del Sistema - Simulador de Ciclorutas v2.0

## 📋 Resumen Ejecutivo

El Simulador de Ciclorutas v2.0 ha sido completamente refactorizado siguiendo principios de **arquitectura modular**, **separación de responsabilidades** y **escalabilidad**. La nueva estructura permite un mantenimiento más fácil, mayor reutilización de código y mejor organización.

## 🎯 Principios de Diseño

### 1. **Separación de Responsabilidades**
- **Simulador**: Lógica de simulación pura
- **Interfaz**: Presentación y control de usuario
- **Configuración**: Parámetros centralizados

### 2. **Modularidad**
- Cada módulo tiene una responsabilidad específica
- Interfaces claras entre componentes
- Bajo acoplamiento, alta cohesión

### 3. **Escalabilidad**
- Fácil agregar nuevas funcionalidades
- Soporte para diferentes tipos de grafos
- Configuración flexible

## 🏛️ Estructura de Directorios

```
ciclorutas/
├── 📁 Simulador/                    # Motor de simulación
│   ├── 📁 core/                     # Componentes principales
│   │   ├── simulador.py            # Motor principal
│   │   └── configuracion.py        # Gestión de configuración
│   ├── 📁 models/                   # Modelos de datos
│   │   └── ciclista.py             # Modelo de ciclista
│   ├── 📁 distributions/            # Distribuciones de probabilidad
│   │   └── distribucion_nodo.py    # Distribuciones por nodo
│   └── 📁 utils/                    # Utilidades del simulador
│       └── grafo_utils.py          # Utilidades para grafos
├── 📁 Interfaz/                     # Interfaz gráfica
│   ├── 📁 components/               # Componentes principales
│   │   └── app_principal.py        # Aplicación principal
│   ├── 📁 panels/                   # Paneles de la interfaz
│   │   ├── panel_control.py        # Control de simulación
│   │   ├── panel_visualizacion.py  # Visualización
│   │   ├── panel_estadisticas.py   # Estadísticas
│   │   └── panel_distribuciones.py # Distribuciones
│   └── 📁 utils/                    # Utilidades de interfaz
│       ├── estilo_utils.py         # Estilos y temas
│       └── archivo_utils.py        # Manejo de archivos
├── main.py                          # Punto de entrada
├── config.py                        # Configuración centralizada
└── requirements.txt                 # Dependencias
```

## 🔧 Componentes Principales

### 🎮 Módulo Simulador

#### **Core (Núcleo)**
- **`SimuladorCiclorutas`**: Motor principal de simulación
  - Orquesta toda la simulación
  - Maneja el entorno SimPy
  - Coordina todos los componentes
  - Gestiona el estado de la simulación

- **`ConfiguracionSimulacion`**: Gestión de configuración
  - Parámetros de simulación centralizados
  - Validación de configuración
  - Configuraciones predefinidas
  - Persistencia de configuración

#### **Models (Modelos)**
- **`Ciclista`**: Modelo de ciclista individual
  - Estado del ciclista
  - Posición y trayectoria
  - Gestión de memoria optimizada
  - Métodos de actualización

- **`PoolCiclistas`**: Sistema de pool de objetos
  - Reutilización de ciclistas
  - Gestión de memoria eficiente
  - Estadísticas de rendimiento
  - Limpieza automática

#### **Distributions (Distribuciones)**
- **`DistribucionNodo`**: Distribuciones por nodo
  - Distribución exponencial
  - Distribución de Poisson
  - Distribución uniforme
  - Configuración flexible

- **`GestorDistribuciones`**: Gestión centralizada
  - Configuración de múltiples nodos
  - Validación de parámetros
  - Estadísticas de uso

#### **Utils (Utilidades)**
- **`GrafoUtils`**: Utilidades para grafos
  - Validación de grafos
  - Cálculo de posiciones
  - Obtención de distancias
  - Optimización de rutas

### 🖥️ Módulo Interfaz

#### **Components (Componentes)**
- **`InterfazSimulacion`**: Aplicación principal
  - Orquestación de la interfaz
  - Gestión de eventos
  - Comunicación entre paneles
  - Control del ciclo de vida

#### **Panels (Paneles)**
- **`PanelControl`**: Control de simulación
  - Parámetros configurables
  - Botones de control
  - Estado de la simulación
  - Validación de entrada

- **`PanelVisualizacion`**: Visualización
  - Gráfico matplotlib integrado
  - Visualización en tiempo real
  - Controles de visualización
  - Interacción con el grafo

- **`PanelEstadisticas`**: Estadísticas
  - Métricas en tiempo real
  - Actualización automática
  - Formateo de datos
  - Exportación de datos

- **`PanelDistribuciones`**: Distribuciones
  - Configuración de nodos
  - Perfiles de ciclistas
  - Validación de parámetros
  - Interfaz de edición

#### **Utils (Utilidades)**
- **`EstiloUtils`**: Gestión de estilos
  - Paleta de colores
  - Configuración de fuentes
  - Estilos de widgets
  - Temas personalizables

- **`ArchivoUtils`**: Manejo de archivos
  - Carga de archivos Excel
  - Validación de formato
  - Procesamiento de datos
  - Manejo de errores

## 🔄 Flujo de Datos

### 1. **Inicialización**
```
main.py → InterfazSimulacion → SimuladorCiclorutas → ConfiguracionSimulacion
```

### 2. **Carga de Grafo**
```
ArchivoUtils → InterfazSimulacion → SimuladorCiclorutas → GrafoUtils
```

### 3. **Simulación**
```
PanelControl → InterfazSimulacion → SimuladorCiclorutas → Ciclista
```

### 4. **Visualización**
```
SimuladorCiclorutas → InterfazSimulacion → PanelVisualizacion → matplotlib
```

### 5. **Estadísticas**
```
SimuladorCiclorutas → InterfazSimulacion → PanelEstadisticas
```

## 🎨 Patrones de Diseño Utilizados

### 1. **MVC (Model-View-Controller)**
- **Model**: SimuladorCiclorutas, Ciclista, etc.
- **View**: Paneles de la interfaz
- **Controller**: InterfazSimulacion

### 2. **Observer Pattern**
- Paneles observan cambios en el simulador
- Actualización automática de la interfaz

### 3. **Factory Pattern**
- Creación de distribuciones
- Creación de perfiles de ciclistas

### 4. **Singleton Pattern**
- Configuración centralizada
- Gestión de recursos compartidos

### 5. **Pool Pattern**
- Reutilización de objetos Ciclista
- Gestión eficiente de memoria

## 📊 Ventajas de la Nueva Arquitectura

### ✅ **Mantenibilidad**
- Código organizado en módulos lógicos
- Responsabilidades claramente definidas
- Fácil localización de funcionalidades

### ✅ **Escalabilidad**
- Fácil agregar nuevos tipos de distribuciones
- Soporte para diferentes tipos de grafos
- Extensibilidad de la interfaz

### ✅ **Reutilización**
- Componentes independientes
- Utilidades compartidas
- Configuración centralizada

### ✅ **Testabilidad**
- Componentes aislados
- Interfaces bien definidas
- Fácil mockeo de dependencias

### ✅ **Rendimiento**
- Pool de objetos para eficiencia
- Cache de datos optimizado
- Gestión inteligente de memoria

## 🔧 Configuración y Personalización

### **Configuración Centralizada**
- Archivo `config.py` con todas las configuraciones
- Parámetros por defecto
- Validación automática
- Configuraciones predefinidas

### **Extensibilidad**
- Nuevos tipos de distribuciones
- Nuevos atributos de grafos
- Nuevos perfiles de ciclistas
- Nuevos paneles de interfaz

## 🚀 Mejoras Futuras

### **Corto Plazo**
- [ ] Tests unitarios para cada módulo
- [ ] Documentación de API
- [ ] Logging mejorado
- [ ] Manejo de errores robusto

### **Mediano Plazo**
- [ ] Simulación en 3D
- [ ] Análisis de patrones de tráfico
- [ ] Exportación de reportes
- [ ] Simulación distribuida

### **Largo Plazo**
- [ ] Interfaz web
- [ ] Base de datos de grafos
- [ ] Machine learning para optimización
- [ ] Simulación en tiempo real

## 📝 Conclusión

La nueva arquitectura del Simulador de Ciclorutas v2.0 representa una mejora significativa en términos de:

- **Organización**: Código bien estructurado y modular
- **Mantenibilidad**: Fácil de mantener y extender
- **Escalabilidad**: Preparado para futuras funcionalidades
- **Rendimiento**: Optimizado para simulaciones complejas
- **Usabilidad**: Interfaz más intuitiva y funcional

Esta arquitectura sienta las bases para un sistema robusto, escalable y mantenible que puede evolucionar con las necesidades del proyecto.
