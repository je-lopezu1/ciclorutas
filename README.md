# 📚 Documentación del Simulador de Ciclorutas

## 🎯 Descripción General

El Simulador de Ciclorutas es una herramienta avanzada para simular el comportamiento de ciclistas en redes de carreteras. Utiliza técnicas de simulación de eventos discretos y distribuciones de probabilidad para modelar de manera realista el flujo de tráfico ciclístico.

## 🏗️ Arquitectura del Sistema

### Estructura de Carpetas

```
ciclorutas/
├── src/                          # Código fuente principal
│   ├── core/                     # Lógica central del negocio
│   │   ├── simulador.py          # Orquestador principal
│   │   ├── ciclista.py           # Lógica de ciclistas
│   │   └── generador.py          # Generación de ciclistas
│   ├── data/                     # Manejo de datos
│   │   ├── grafo.py              # Operaciones con grafos
│   │   ├── distribuciones.py     # Distribuciones de probabilidad
│   │   └── estadisticas.py       # Cálculo de estadísticas
│   ├── ui/                       # Interfaz de usuario
│   │   └── interfaz_simulacion.py
│   ├── utils/                    # Utilidades y helpers
│   │   └── validadores.py        # Validaciones comunes
│   └── config/                   # Configuración
│       └── configuracion.py
├── tests/                        # Pruebas
├── examples/                     # Ejemplos de uso
└── main.py                       # Punto de entrada
```

### Principios de Diseño

- **Separación de Responsabilidades**: Cada módulo tiene una responsabilidad específica
- **Modularidad**: Los componentes pueden ser reutilizados independientemente
- **Extensibilidad**: Fácil agregar nuevas funcionalidades
- **Mantenibilidad**: Código organizado y bien documentado

## 🚀 Instalación

### Requisitos Previos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Instalación desde Código Fuente

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/usuario/ciclorutas.git
   cd ciclorutas
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Instalar el paquete en modo desarrollo**
   ```bash
   pip install -e .
   ```

### Instalación con pip

```bash
pip install simulador-ciclorutas
```

## 🎮 Uso Básico

### Interfaz Gráfica

```bash
python main.py
```

### Uso Programático

```python
from src.core import SimuladorCiclorutas, crear_simulador_rapido
from src.config import ConfiguracionSimulacion

# Crear simulador
simulador = crear_simulador_rapido()

# Crear grafo de ejemplo
simulador.crear_grafo_ejemplo()

# Inicializar simulación
simulador.inicializar_simulacion()

# Ejecutar simulación
simulador.estado = "ejecutando"
while simulador.ejecutar_paso():
    pass

# Obtener estadísticas
stats = simulador.obtener_estadisticas()
print(f"Ciclistas activos: {stats['ciclistas_activos']}")
```

## 📊 Características Principales

### Simulación en Tiempo Real
- Visualización en vivo del movimiento de ciclistas
- Control de velocidad de simulación
- Pausa y reanudación

### Distribuciones de Probabilidad
- Exponencial
- Poisson
- Uniforme
- Normal
- Gamma

### Gestión de Grafos
- Carga desde archivos Excel
- Validación automática
- Cálculo de rutas dinámicas

### Estadísticas Avanzadas
- Métricas en tiempo real
- Análisis de patrones de tráfico
- Reportes detallados

## 🔧 Configuración

### Parámetros Principales

- **Velocidad mínima/máxima**: Rango de velocidades de ciclistas
- **Duración de simulación**: Tiempo total de la simulación
- **Máximo de ciclistas**: Límite de ciclistas simultáneos
- **Distribuciones**: Configuración de tasas de arribo por nodo

### Archivos de Configuración

El sistema utiliza archivos Excel para definir grafos de red:

- **Hoja "NODOS"**: Lista de nodos de la red
- **Hoja "ARCOS"**: Conexiones entre nodos con distancias

## 🧪 Pruebas

### Ejecutar Pruebas

```bash
# Pruebas básicas
python tests/test_simulador.py

# Pruebas con pytest
pytest tests/

# Pruebas con cobertura
pytest --cov=src tests/
```

### Ejemplos

```bash
# Ejemplo básico
python examples/ejemplo_basico.py
```

## 📈 API Reference

### Clases Principales

#### SimuladorCiclorutas
Orquestador principal del sistema.

```python
simulador = SimuladorCiclorutas(config)
simulador.configurar_grafo(grafo, posiciones)
simulador.inicializar_simulacion()
simulador.ejecutar_paso()
```

#### ConfiguracionSimulacion
Configuración de parámetros de simulación.

```python
config = ConfiguracionSimulacion(
    velocidad_min=10.0,
    velocidad_max=20.0,
    duracion_simulacion=300.0
)
```

#### GestorDistribuciones
Manejo de distribuciones de probabilidad.

```python
gestor = GestorDistribuciones()
gestor.agregar_distribucion(nodo_id, distribucion)
tiempo = gestor.generar_tiempo_arribo_nodo(nodo_id)
```

## 🤝 Contribución

### Cómo Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

### Estándares de Código

- Usar Black para formateo de código
- Seguir PEP 8 para estilo de código
- Escribir docstrings para todas las funciones
- Incluir pruebas para nuevas funcionalidades

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 📞 Soporte

Para soporte técnico o preguntas:

- Abre un issue en el repositorio
- Contacta al equipo de desarrollo
- Revisa la documentación completa

## 🔮 Roadmap

### Versión 2.1
- [ ] Simulación en 3D
- [ ] Análisis de congestión
- [ ] Exportación de datos

### Versión 2.2
- [ ] Múltiples tipos de vehículos
- [ ] Factores ambientales
- [ ] Integración con APIs externas

---

**🚴 ¡Disfruta simulando ciclorutas! 🚴**
