# Simulador de Ciclorutas v2.0

Sistema completo de simulación de redes de ciclorutas con interfaz gráfica modular y control avanzado.

## ¿Qué es esta Herramienta?

El **Simulador de Ciclorutas** es una herramienta de simulación discreta desarrollada como parte de una investigación académica para **representar y analizar redes de desplazamiento de ciclistas en contextos urbanos**. Esta herramienta fue creada en el marco de una tesis de pregrado en Ingeniería de Sistemas y Computación de la Universidad de los Andes, con el objetivo de evaluar la aplicabilidad de modelos analíticos (redes de colas de Jackson) mediante comparación con enfoques de simulación basados en eventos discretos.

La herramienta permite modelar, analizar y visualizar el comportamiento de ciclistas en redes urbanas de ciclorutas, considerando múltiples factores como:

- **Redes de infraestructura**: Modelado de nodos (puntos de acceso) y arcos (tramos de cicloruta)
- **Características físicas**: Distancia, inclinación, seguridad, luminosidad de los tramos
- **Comportamiento de ciclistas**: Diferentes perfiles de preferencias y decisiones de ruta
- **Distribuciones probabilísticas**: Modelado realista de arribos y patrones de movimiento
- **Visualización en tiempo real**: Representación dinámica del movimiento de ciclistas
- **Modelado de congestión**: Sistema de capacidad por sentido de circulación con reducción dinámica de velocidad

### Contexto de Investigación

Esta herramienta es el resultado de la investigación académica titulada **"Simulating Urban Bicycle Lanes with SimPy: Assessing the Applicability of Jackson Queueing Networks"** (Tesis de Pregrado en Ingeniería de Sistemas y Computación, Universidad de los Andes). El trabajo busca cerrar la brecha entre modelos analíticos matemáticamente elegantes (como las redes de Jackson basadas en teoría de colas) y métodos de simulación flexibles basados en eventos discretos.

La investigación contribuye al campo de modelado de tráfico ciclista mediante:
- **Comparación metodológica**: Validación de modelos analíticos contra simulaciones discretas
- **Modelado de comportamiento heterogéneo**: Incorporación de perfiles de ciclistas con preferencias diversas
- **Análisis de congestión**: Evaluación de dinámicas de tráfico en redes de ciclorutas urbanas
- **Herramienta de código abierto**: Framework extensible para investigación y planificación urbana

### Objetivos de la Herramienta

- **Validación académica**: Comparar resultados de simulación con modelos analíticos de teoría de colas
- **Análisis de redes de ciclorutas**: Evaluar la eficiencia y uso de infraestructura ciclista
- **Investigación de comportamiento**: Estudiar patrones de desplazamiento y decisiones de ruta de ciclistas
- **Simulación de escenarios**: Probar diferentes configuraciones de infraestructura y parámetros de demanda
- **Planificación urbana**: Proporcionar datos cuantitativos para la toma de decisiones en diseño de ciclorutas

## Documentación Disponible

Este proyecto incluye documentación completa organizada en cuatro documentos especializados:

### 1. **README_INSTALACION.md** - Guía de Instalación y Configuración

Guía paso a paso para descargar, instalar y poner en funcionamiento la herramienta.

**Contenido incluido**:
- Requisitos del sistema (hardware y software)
- Instrucciones de descarga del proyecto
- Preparación del entorno (Python, entorno virtual)
- Instalación de dependencias (métodos automático, manual y Conda)
- Verificación de la instalación
- Ejecución de la aplicación (múltiples métodos)
- Primera configuración y pruebas básicas
- Solución de problemas comunes con soluciones detalladas
- Comandos de diagnóstico y debugging

**Ideal para**: Usuarios nuevos que quieren comenzar a usar la herramienta rápidamente.

### 2. **README_ARQUITECTURA.md** - Arquitectura y Diseño del Sistema

Documentación técnica completa sobre la arquitectura, diseño y funcionamiento interno de todos los componentes.

**Contenido incluido**:
- Visión general y principios de diseño (separación de responsabilidades, modularidad, escalabilidad)
- Estructura completa del proyecto y organización de directorios
- Descripción detallada de cada componente:
  - **Módulo Simulador**: Motor de simulación, modelos, distribuciones, utilidades
  - **Módulo Interfaz**: Paneles, componentes, utilidades de archivos
- Flujos de datos entre componentes (inicialización, carga de grafo, simulación, visualización)
- **Carga de archivos Excel**: Formato requerido, validación, procesamiento, ejemplos
- **Sistema de visualización**: Tecnologías, proceso de renderizado, actualización en tiempo real
- **Generación de simulaciones**: Inicialización, generación de ciclistas, asignación de rutas
- **Sistema de eventos y calendario**: Cómo se definen y gestionan los eventos
- Patrones de diseño utilizados (MVC, Observer, Factory, Singleton, Pool)
- Guía de extensibilidad para agregar nuevas funcionalidades

**Ideal para**: Desarrolladores e investigadores que necesitan entender o modificar el código.

### 3. **README_MODELO_SIMULACION.md** - Modelo de Simulación

Documentación exclusiva y detallada sobre el modelo de simulación, sus entidades, eventos y mecánicas.

**Contenido incluido**:
- Visión general del modelo (simulación de eventos discretos con SimPy)
- Tipo de simulación y comparación con otros enfoques
- **Entidades del modelo**:
  - Ciclista (atributos, estados, ciclo de vida)
  - Nodo (puntos de acceso)
  - Arco/Tramo (conexiones con atributos físicos)
  - Perfil de Ciclista (preferencias y pesos)
  - Red/Grafo (estructura completa)
- **Eventos del modelo**: Clasificación, generación y procesamiento
  - Eventos de arribo
  - Eventos de movimiento
  - Eventos de decisión
  - Eventos de finalización
- **Calendario de eventos**: Gestión, ordenamiento temporal, procesamiento
- **Mecánica de decisión**: Algoritmos detallados para:
  - Selección de nodo origen (basado en tasas de arribo)
  - Selección de perfil de ciclista (basado en probabilidades)
  - Selección de destino (usando matriz de probabilidades)
  - Cálculo de ruta óptima (Dijkstra con pesos compuestos)
  - Ajuste de velocidad por inclinación
  - Factor de tiempo por seguridad/luminosidad
- Gestión del tiempo (tiempos de simulación, arribo, movimiento, viaje)
- Estado del sistema y transiciones
- Flujo de ejecución paso a paso con ejemplos
- Limitaciones y supuestos del modelo

**Ideal para**: Investigadores que estudian el modelo de simulación, estudiantes de modelado, y personas que necesitan entender las decisiones y eventos del sistema.

### 4. **README_MANUAL_USUARIO.md** - Manual de Usuario

Guía práctica paso a paso para utilizar la herramienta desde la perspectiva del usuario final.

**Contenido incluido**:
- Preparación de archivos Excel: formato detallado de cada hoja (NODOS, ARCOS, PERFILES, RUTAS)
- Requisitos y validaciones de cada columna
- Inicio de la aplicación y navegación de la interfaz
- Carga de redes de ciclorutas desde Excel
- Configuración de parámetros (velocidades, duración)
- Configuración de distribuciones de probabilidad por nodo
- Control de simulación (botones, flujo de trabajo)
- Interpretación de resultados y estadísticas
- Exportación y análisis de datos
- Ejemplos prácticos completos
- Preguntas frecuentes y solución de problemas comunes

**Ideal para**: Usuarios finales que necesitan preparar datos y utilizar la herramienta para análisis y planificación.

### Cómo Usar Esta Documentación

- **¿Eres nuevo?** → Comienza con `README_INSTALACION.md` para instalar y ejecutar la herramienta
- **¿Quieres usar la herramienta?** → Consulta `README_MANUAL_USUARIO.md` para preparar archivos Excel y usar la interfaz
- **¿Quieres entender el código?** → Consulta `README_ARQUITECTURA.md` para ver cómo funciona internamente
- **¿Estudias el modelo de simulación?** → Revisa `README_MODELO_SIMULACION.md` para detalles del modelo matemático y lógico
- **¿Necesitas referencia rápida?** → Este `README.md` proporciona un resumen y guía de inicio rápido

---

## Tabla de Contenidos

- [¿Qué es esta Herramienta?](#qué-es-esta-herramienta)
- [Documentación Disponible](#documentación-disponible)
- [Características Principales](#características-principales)
- [Inicio Rápido](#inicio-rápido)
- [Autores y Contexto](#autores-y-contexto)
- [Documentación Adicional](#documentación-adicional)

## Características Principales

### Simulación y Modelado
- **Simulación de eventos discretos** usando SimPy para modelar ciclistas como entidades individuales
- **Modelado de redes urbanas** mediante grafos no dirigidos (NetworkX) representando infraestructura ciclista
- **Distribuciones probabilísticas configurables** (exponencial, Poisson, normal, log-normal, gamma, Weibull) para arribos por nodo
- **Perfiles heterogéneos de ciclistas** con preferencias multi-atributo (distancia, seguridad, luminosidad, inclinación)
- **Algoritmo de ruta óptima** basado en Dijkstra con pesos compuestos según preferencias del ciclista
- **Sistema de capacidad y congestión**: Modelado de capacidad por sentido de circulación con reducción dinámica de velocidad cuando se excede la capacidad
- **Factor de densidad de tráfico**: Cálculo independiente por sentido que reduce la velocidad proporcionalmente cuando hay sobrecarga

### Interfaz y Visualización
- **Interfaz gráfica modular** (Tkinter) con paneles de control, visualización, estadísticas y distribuciones
- **Visualización en tiempo real** con matplotlib mostrando movimiento de ciclistas y trayectorias
- **Carga de datos desde Excel** con validación automática de estructura y atributos
- **Estadísticas detalladas** en tiempo real: ciclistas activos, velocidades, rutas utilizadas, utilización de segmentos

### Arquitectura y Extensibilidad
- **Arquitectura modular** con separación clara entre motor de simulación e interfaz gráfica
- **Configuración centralizada** mediante archivos Excel y parámetros de usuario
- **Sistema de cache inteligente** para optimización de rutas y gestión de memoria
- **Diseño extensible** que permite agregar nuevos tipos de distribuciones, atributos y comportamientos

## Inicio Rápido

### Requisitos

- Python 3.7 o superior
- Dependencias: simpy, matplotlib, numpy, pandas, networkx, scipy, openpyxl, tkinter

### Instalación Rápida

```bash
# Clonar repositorio
git clone <url-del-repositorio>
cd ciclorutas

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python main.py
```

### Uso Básico

1. **Cargar grafo**: Clic en "Cargar Grafo" y seleccione un archivo Excel con formato correcto
2. **Configurar parámetros**: Ajuste velocidades y duración en el Panel de Control
3. **Crear simulación**: Clic en "NUEVA"
4. **Iniciar**: Clic en "INICIAR"
5. **Observar**: Visualice el movimiento de ciclistas y estadísticas en tiempo real

Para información detallada sobre formato de Excel y uso de la herramienta, consulte **[README_MANUAL_USUARIO.md](README_MANUAL_USUARIO.md)**.

Para instrucciones completas de instalación, consulte **[README_INSTALACION.md](README_INSTALACION.md)**.

## Autores y Contexto

**Desarrollado por:**
- Jerónimo Vargas Rendón (202113305)
- Juan Esteban López Ulloa (202021417)

**Universidad de los Andes**  
**Departamento de Ingeniería de Sistemas y Computación**  
**Tesis de Pregrado: "Simulating Urban Bicycle Lanes with SimPy: Assessing the Applicability of Jackson Queueing Networks"**

Este proyecto es parte de una investigación académica que busca evaluar la aplicabilidad de modelos analíticos de teoría de colas (redes de Jackson) mediante comparación con simulaciones de eventos discretos. La herramienta está diseñada para ser extensible y servir como base para futuras investigaciones en modelado de tráfico ciclista urbano.

## Documentación Adicional

Este README proporciona una visión general del sistema. Para información más detallada, consulta:

- **[README_INSTALACION.md](README_INSTALACION.md)** - Guía completa de instalación, configuración y primeros pasos
- **[README_MANUAL_USUARIO.md](README_MANUAL_USUARIO.md)** - Manual de usuario con formato de Excel y guía de uso de la interfaz
- **[README_ARQUITECTURA.md](README_ARQUITECTURA.md)** - Documentación técnica de arquitectura, componentes y diseño
- **[README_MODELO_SIMULACION.md](README_MODELO_SIMULACION.md)** - Documentación detallada del modelo de simulación, entidades, eventos y decisiones

Cada documento está diseñado para diferentes niveles de profundidad según tus necesidades.