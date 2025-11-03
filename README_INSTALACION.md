# 📦 Guía de Instalación y Configuración - Simulador de Ciclorutas

## 📋 Tabla de Contenidos

- [Requisitos del Sistema](#requisitos-del-sistema)
- [Descarga del Proyecto](#descarga-del-proyecto)
- [Preparación del Entorno](#preparación-del-entorno)
- [Instalación de Dependencias](#instalación-de-dependencias)
- [Verificación de la Instalación](#verificación-de-la-instalación)
- [Ejecución de la Aplicación](#ejecución-de-la-aplicación)
- [Primera Configuración](#primera-configuración)
- [Pruebas Básicas](#pruebas-básicas)
- [Solución de Problemas Comunes](#solución-de-problemas-comunes)

---

## 💻 Requisitos del Sistema

### Requisitos Mínimos

| Componente | Requisito |
|------------|-----------|
| **Sistema Operativo** | Windows 10/11, macOS 10.14+, Linux Ubuntu 18.04+ |
| **Python** | 3.7 o superior (recomendado 3.8+) |
| **RAM** | 4 GB mínimo (8 GB recomendado) |
| **Espacio en Disco** | 500 MB para instalación |
| **Procesador** | Dual-core 2.0 GHz o superior |

### Dependencias de Software

- Python 3.7+ con pip instalado
- Git (opcional, para clonar el repositorio)
- Navegador web moderno (para visualizar documentación)

---

## 📥 Descarga del Proyecto

### Opción 1: Clonar desde Git (Recomendado)

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd ciclorutas
```

### Opción 2: Descargar ZIP

1. Descargar el archivo ZIP del repositorio
2. Extraer el archivo en una carpeta de su elección
3. Abrir terminal/cmd en la carpeta extraída

```bash
# Navegar a la carpeta del proyecto
cd ciclorutas
```

---

## 🔧 Preparación del Entorno

### Paso 1: Verificar Python

Verificar que Python está instalado y es la versión correcta:

```bash
# Verificar versión de Python
python --version
# Debe mostrar Python 3.7 o superior

# En algunos sistemas puede ser python3
python3 --version
```

Si Python no está instalado:
- **Windows**: Descargar desde [python.org](https://www.python.org/downloads/)
- **macOS**: `brew install python3` o descargar desde python.org
- **Linux**: `sudo apt-get install python3 python3-pip`

### Paso 2: Crear Entorno Virtual (Recomendado)

Crear un entorno virtual aísla las dependencias del proyecto:

**Windows:**
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate
```

**macOS/Linux:**
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate
```

**Indicador de éxito**: El prompt mostrará `(venv)` al inicio.

### Paso 3: Actualizar pip

Actualizar pip a la versión más reciente:

```bash
# Windows/macOS/Linux
python -m pip install --upgrade pip
```

---

## 📦 Instalación de Dependencias

### Método 1: Instalación Automática (Recomendada)

Instalar todas las dependencias desde `requirements.txt`:

```bash
# Asegurarse de estar en la carpeta del proyecto
pip install -r requirements.txt
```

Este comando instalará:
- `simpy>=4.0.0` - Simulación de eventos discretos
- `matplotlib>=3.5.0` - Visualización y gráficos
- `numpy>=1.20.0` - Computación numérica
- `pandas>=1.5.0` - Análisis de datos
- `networkx>=3.0` - Análisis de redes y grafos
- `scipy>=1.9.0` - Computación científica
- `openpyxl>=3.0.0` - Manejo de archivos Excel

### Método 2: Instalación Manual

Si tiene problemas con el método automático, instalar dependencias individualmente:

```bash
pip install simpy>=4.0.0
pip install matplotlib>=3.5.0
pip install numpy>=1.20.0
pip install pandas>=1.5.0
pip install networkx>=3.0
pip install scipy>=1.9.0
pip install openpyxl>=3.0.0
```

### Método 3: Instalación con Conda

Si usa Anaconda o Miniconda:

```bash
conda install simpy matplotlib numpy pandas networkx scipy openpyxl
```

### Nota sobre tkinter

`tkinter` viene incluido con Python en la mayoría de instalaciones. Si tiene problemas:

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**CentOS/RHEL:**
```bash
sudo yum install tkinter
```

**macOS:** tkinter debería estar incluido por defecto

---

## ✅ Verificación de la Instalación

Verificar que todas las dependencias están correctamente instaladas:

```bash
# Verificar todas las dependencias en un comando
python -c "import simpy, matplotlib, numpy, pandas, networkx, scipy, openpyxl, tkinter; print('✅ Todas las dependencias están instaladas correctamente')"
```

Si algún módulo falta, instalarlo manualmente:

```bash
# Ejemplo: si falta matplotlib
pip install matplotlib
```

### Verificar Estructura del Proyecto

Verificar que la estructura de carpetas es correcta:

```
ciclorutas/
├── main.py
├── config.py
├── requirements.txt
├── Simulador/
│   ├── __init__.py
│   ├── core/
│   ├── models/
│   ├── distributions/
│   └── utils/
├── Interfaz/
│   ├── __init__.py
│   ├── components/
│   ├── panels/
│   └── utils/
└── Libro2.xlsx (archivo de ejemplo)
```

---

## 🚀 Ejecución de la Aplicación

### Método 1: Ejecución Directa (Recomendada)

Desde la carpeta del proyecto, ejecutar:

```bash
python main.py
```

El sistema:
1. Verificará automáticamente las dependencias
2. Mostrará un mensaje de bienvenida
3. Abrirá la interfaz gráfica en unos segundos

### Método 2: Ejecución con Verificación Explícita

El archivo `main.py` ya incluye verificación de dependencias, pero puede verificar manualmente:

```bash
# Verificar dependencias
python main.py --check-dependencies

# Ejecutar aplicación
python main.py
```

### Método 3: Ejecución en Modo Debug

Para ver mensajes detallados de depuración:

```bash
python -u main.py
```

### Método 4: Ejecución desde Código Python

Desde el intérprete de Python:

```python
from Interfaz import InterfazSimulacion
import tkinter as tk

root = tk.Tk()
app = InterfazSimulacion(root)
root.mainloop()
```

---

## ⚙️ Primera Configuración

### 1. Cargar un Grafo de Prueba

Al abrir la aplicación por primera vez:

1. Hacer clic en **"Cargar Grafo"** en el panel de control
2. Seleccionar uno de los archivos de ejemplo:
   - `Libro2.xlsx`
   - `Libro2_actualizado.xlsx`

### 2. Verificar Configuración de Parámetros

En el panel de control, verificar:
- **Velocidad mínima**: 1.0-20.0 m/s (por defecto: 10.0)
- **Velocidad máxima**: 1.0-30.0 m/s (por defecto: 15.0)
- **Duración**: 60-3600 segundos (por defecto: 300)

### 3. Configurar Distribuciones (Opcional)

En el panel de distribuciones:
- Configurar distribuciones de arribo por nodo
- Ajustar parámetros según necesidades

---

## 🧪 Pruebas Básicas

### Prueba 1: Carga de Grafo

1. Ejecutar `python main.py`
2. Clic en "Cargar Grafo"
3. Seleccionar `Libro2.xlsx`
4. Verificar que aparece mensaje de éxito

**Resultado esperado**: Mensaje "✅ Grafo cargado exitosamente" con estadísticas

### Prueba 2: Inicialización de Simulación

1. Con un grafo cargado
2. Clic en "NUEVA" para crear simulación
3. Clic en "INICIAR"

**Resultado esperado**: 
- La simulación comienza
- Los ciclistas aparecen en la visualización
- Las estadísticas se actualizan

### Prueba 3: Controles de Simulación

1. Iniciar simulación
2. Clic en "PAUSAR"
3. Verificar que se pausa
4. Clic en "REANUDAR"
5. Verificar que continúa

**Resultado esperado**: La simulación pausa y reanuda correctamente

### Prueba 4: Visualización

1. Con simulación ejecutándose
2. Verificar panel de visualización
3. Observar movimiento de ciclistas

**Resultado esperado**: 
- Gráfico muestra la red de ciclorutas
- Los ciclistas se mueven en tiempo real
- Los colores reflejan el nodo de origen

---

## 🔍 Solución de Problemas Comunes

### Problema 1: Error de Dependencias

**Síntoma:**
```
❌ ERROR: Faltan las siguientes dependencias: simpy
```

**Solución:**
```bash
# Instalar dependencias faltantes
pip install -r requirements.txt

# O instalar manualmente
pip install simpy matplotlib numpy pandas networkx scipy openpyxl
```

### Problema 2: Ventana no se Abre

**Síntoma:**
```
❌ ERROR: No se pudo importar la interfaz
```

**Soluciones:**

1. Verificar tkinter:
```bash
python -c "import tkinter; print('✅ tkinter OK')"
```

2. Si falta tkinter:
   - **Ubuntu/Debian**: `sudo apt-get install python3-tk`
   - **CentOS/RHEL**: `sudo yum install tkinter`

3. Verificar estructura de archivos:
```bash
ls Interfaz/
ls Simulador/
```

### Problema 3: Error al Cargar Archivo Excel

**Síntoma:**
```
❌ ERROR: No se pudo cargar el archivo
```

**Soluciones:**

1. Verificar formato del archivo:
   - Debe ser `.xlsx` o `.xls`
   - Debe tener hojas "NODOS" y "ARCOS"
   - Las columnas deben tener los nombres correctos

2. Verificar estructura:
```bash
# Abrir el Excel y verificar:
# - Hoja "NODOS" con columnas: NODO, ID, NOMBRE (y opcionalmente LAT, LON)
# - Hoja "ARCOS" con columnas: ORIGEN, DESTINO, DISTANCIA (y otros atributos)
```

3. Usar archivo de ejemplo para verificar:
   - Cargar `Libro2.xlsx` que viene con el proyecto

### Problema 4: Simulación Muy Lenta

**Síntoma:** La simulación se ejecuta muy lenta

**Soluciones:**

1. Reducir parámetros:
   - Disminuir duración de simulación
   - Reducir velocidad de simulación
   - Usar grafos más pequeños

2. Cerrar otras aplicaciones:
   - Liberar memoria RAM
   - Cerrar navegadores con muchas pestañas

3. Verificar configuración:
```python
# En config.py, reducir límites:
MAX_CICLISTAS_SIMULTANEOS = 100  # Reducir de 1000
```

### Problema 5: Problemas de Memoria

**Síntoma:** Aplicación se cuelga o consume mucha memoria

**Soluciones:**

1. Reducir duración de simulación
2. Reducir número máximo de ciclistas
3. Limpiar cache:
```python
# En la interfaz, usar opción "Limpiar Cache" si está disponible
```

### Problema 6: Error de Importación

**Síntoma:**
```
ModuleNotFoundError: No module named 'Interfaz'
```

**Solución:**

1. Verificar que está en la carpeta correcta:
```bash
pwd  # Linux/macOS
cd   # Windows
```

2. Verificar estructura:
```bash
ls Interfaz/
ls Simulador/
```

3. Ejecutar desde la carpeta raíz del proyecto

### Problema 7: Python No Reconocido

**Síntoma:**
```
'python' no se reconoce como un comando...
```

**Soluciones:**

1. Verificar que Python está en PATH
2. Usar `python3` en lugar de `python`
3. **Windows**: Usar la ruta completa:
```bash
C:\Python39\python.exe main.py
```

---

## 📞 Soporte Adicional

### Comandos de Diagnóstico

Ejecutar estos comandos para diagnosticar problemas:

```bash
# Verificar versión de Python
python --version

# Verificar dependencias instaladas
pip list

# Verificar importaciones
python -c "import simpy, matplotlib, numpy, pandas, networkx, scipy, openpyxl, tkinter; print('✅ OK')"

# Verificar estructura del proyecto
python -c "import os; print(os.listdir('.'))"

# Verificar módulos del proyecto
python -c "import sys; sys.path.append('.'); from Interfaz import InterfazSimulacion; print('✅ OK')"
```

### Logs y Debugging

El sistema genera logs automáticamente. Para activar modo debug:

1. Editar `config.py`
2. Cambiar nivel de logging:
```python
LOGGING_CONFIG = {
    'nivel': 'DEBUG',  # Cambiar de 'INFO' a 'DEBUG'
    'formato': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'archivo': 'simulador.log'
}
```

3. Ejecutar aplicación:
```bash
python main.py
```

4. Revisar archivo `simulador.log` para detalles

---

## ✅ Checklist de Instalación

Marque cada paso cuando esté completo:

- [ ] Python 3.7+ instalado y verificado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas desde requirements.txt
- [ ] Todas las dependencias verificadas
- [ ] Estructura del proyecto verificada
- [ ] Aplicación ejecuta sin errores
- [ ] Grafo de ejemplo carga correctamente
- [ ] Simulación básica funciona
- [ ] Visualización muestra resultados
- [ ] Controles funcionan (pausar, reanudar, detener)

---

## 🎉 Siguiente Paso

Una vez completada la instalación, consulte:

- **README_ARQUITECTURA.md** - Para entender la arquitectura y diseño
- **README_MODELO_SIMULACION.md** - Para entender el modelo de simulación

¡Listo para usar el Simulador de Ciclorutas! 🚴‍♂️🚴‍♀️

