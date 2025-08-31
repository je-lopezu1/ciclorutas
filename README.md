# 🚴 SIMULADOR DE CICLORUTAS - SISTEMA COMPLETO 🚴

Un simulador avanzado de ciclorutas con interfaz gráfica moderna, que permite simular el movimiento de ciclistas en una red de carreteras en forma de Y.

## 🎯 Características Principales

- **Simulación en Tiempo Real**: Visualización en vivo del movimiento de ciclistas
- **Interfaz Gráfica Moderna**: UI intuitiva con tkinter y matplotlib
- **Control Completo**: Iniciar, pausar, detener y adelantar simulación
- **Parámetros Configurables**: Número de ciclistas, velocidades y distancias
- **Estadísticas en Vivo**: Métricas actualizadas en tiempo real
- **Arquitectura Modular**: Lógica de simulación separada de la interfaz

## 🏗️ Arquitectura del Sistema

```
ciclorutas/
├── main.py                      # 🚀 Archivo principal de ejecución
├── simulacion_ciclorutas.py    # ⚙️ Lógica de simulación (SimPy)
├── interfaz_simulacion.py      # 🖥️ Interfaz gráfica (tkinter)
├── Sim inicial.py              # 📊 Simulación original (referencia)
├── requirements.txt            # 📦 Dependencias del proyecto
└── README.md                  # 📖 Este archivo
```

## 🚀 Instalación y Configuración

### Requisitos Previos
- **Python 3.7 o superior**
- **pip** (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   # Si tienes git:
   git clone <url-del-repositorio>
   cd ciclorutas
   
   # O simplemente descarga los archivos en una carpeta
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verificar instalación**
   ```bash
   python main.py
   ```

## 🎮 Uso del Sistema

### Ejecución Principal
```bash
python main.py
```

### Flujo de Trabajo Típico

1. **Configurar Parámetros**
   - Número de ciclistas (5-100)
   - Velocidad mínima y máxima (1.0-30.0 m/s)
   - Distancias A, B y C (15.0-100.0 m)

2. **Crear Nueva Simulación**
   - Hacer clic en "🔄 NUEVA SIMULACIÓN"
   - Los parámetros se aplican automáticamente

3. **Controlar la Simulación**
   - **▶️ INICIAR**: Comienza la simulación
   - **⏸️ PAUSAR**: Pausa temporalmente
   - **⏹️ DETENER**: Detiene completamente
   - **⏭️ ADELANTAR**: Avanza 10 pasos rápidamente

4. **Repetir el Proceso**
   - Modificar parámetros según sea necesario
   - Crear nuevas simulaciones
   - Comparar resultados

## 🔧 Parámetros Configurables

| Parámetro | Rango | Descripción |
|-----------|-------|-------------|
| **Número de Ciclistas** | 5-100 | Cantidad de entidades en la simulación |
| **Velocidad Mínima** | 1.0-20.0 m/s | Velocidad más baja de los ciclistas |
| **Velocidad Máxima** | 1.0-30.0 m/s | Velocidad más alta de los ciclistas |
| **Distancia A** | 20.0-100.0 m | Longitud del tramo principal A→X |
| **Distancia B** | 15.0-80.0 m | Longitud del tramo X→B |
| **Distancia C** | 15.0-80.0 m | Longitud del tramo X→C |

## 📊 Visualización

### Geometría de la Red
- **Tramo A→X**: Camino principal horizontal (gris)
- **Tramo X→B**: Bifurcación hacia arriba (azul)
- **Tramo X→C**: Bifurcación hacia abajo (magenta)

### Colores de Ciclistas
- **A→B**: Naranja brillante (#FF6B35) - Muy llamativo y energético
- **A→C**: Rojo vibrante (#FF1744) - Intenso y dinámico
- **B→A**: Verde neón (#00E676) - Brillante y fresco
- **C→A**: Azul eléctrico (#2979FF) - Intenso y moderno

## 🎨 Características de la Interfaz

- **Panel de Control**: Configuración de parámetros y botones de control
- **Visualización en Tiempo Real**: Gráfico matplotlib integrado
- **Panel de Estadísticas**: Métricas actualizadas dinámicamente
- **Diseño Responsivo**: Se adapta a diferentes tamaños de ventana
- **Colores Modernos**: Paleta de colores profesional y atractiva

## 🔍 Solución de Problemas

### Error de Dependencias
```bash
# Si aparece error de módulos faltantes:
pip install simpy matplotlib numpy
```

### Error de tkinter
```bash
# En sistemas Linux, puede necesitar:
sudo apt-get install python3-tk

# En macOS con Homebrew:
brew install python-tk
```

### Error de Matplotlib (zorder en leyenda)
```bash
# Si aparece error: "Legend.__init__() got an unexpected keyword argument 'zorder'"
# El código ya está corregido, pero si persiste:
pip install --upgrade matplotlib
```

### Error de Fuentes (Emojis no soportados)
```bash
# Si aparecen warnings sobre glifos faltantes:
# El sistema automáticamente usa texto simple en lugar de emojis
# No afecta la funcionalidad del simulador
```

### Rendimiento Lento
- Reducir el número de ciclistas
- Aumentar el intervalo de actualización
- Cerrar otras aplicaciones pesadas

### Verificar Instalación
```bash
# Ejecutar archivo de pruebas:
python test_simulador.py

# Si todas las pruebas pasan, el sistema está listo
```

## 🚧 Limitaciones Actuales

- Simulación limitada a geometría en forma de Y
- No incluye colisiones entre ciclistas
- Velocidades constantes durante el trayecto
- No incluye factores externos (clima, tráfico)

## 🔮 Mejoras Futuras

- [ ] Múltiples geometrías de red
- [ ] Sistema de colisiones y congestión
- [ ] Factores ambientales y de tráfico
- [ ] Exportación de datos y reportes
- [ ] Simulación en 3D
- [ ] Análisis de patrones de tráfico

## 📝 Licencia

Este proyecto está desarrollado con fines educativos y de investigación.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📞 Soporte

Para soporte técnico o preguntas:
- Revisa la documentación
- Abre un issue en el repositorio
- Contacta al equipo de desarrollo

---

**🚴 ¡Disfruta simulando ciclorutas! 🚴**
