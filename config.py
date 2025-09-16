"""
Configuración centralizada del sistema de simulación de ciclorutas.

Este módulo contiene todas las configuraciones del sistema,
incluyendo parámetros por defecto, rutas de archivos, y configuraciones
de la interfaz gráfica.
"""

import os
from typing import Dict, Any, List

# =============================================================================
# CONFIGURACIÓN GENERAL DEL SISTEMA
# =============================================================================

# Información del sistema
SISTEMA_INFO = {
    'nombre': 'Simulador de Ciclorutas',
    'version': '2.0.0',
    'autor': 'Sistema de Simulación de Ciclorutas',
    'descripcion': 'Sistema completo de simulación de redes de ciclorutas'
}

# Configuración de la aplicación
APP_CONFIG = {
    'titulo_ventana': '🚴 Simulador de Ciclorutas - Control Avanzado',
    'tamaño_ventana': (1400, 900),
    'tamaño_minimo': (800, 600),
    'centrar_ventana': True,
    'resizable': True
}

# =============================================================================
# CONFIGURACIÓN DE SIMULACIÓN
# =============================================================================

# Parámetros por defecto de la simulación
SIMULACION_DEFAULTS = {
    'velocidad_minima': 10.0,
    'velocidad_maxima': 15.0,
    'duracion_simulacion': 300.0,  # segundos
    'max_ciclistas_simultaneos': 1000,
    'max_trayectoria_puntos': 50,
    'max_tiempo_inactivo': 300.0,  # 5 minutos
    'intervalo_actualizacion': 0.1,  # 100ms
    'frecuencia_visualizacion': 0.05  # 50ms
}

# Límites de parámetros
PARAMETROS_LIMITES = {
    'velocidad': {
        'min': 1.0,
        'max': 30.0,
        'incremento': 0.5
    },
    'duracion': {
        'min': 60.0,
        'max': 3600.0,
        'incremento': 30.0
    },
    'ciclistas': {
        'min': 1,
        'max': 5000,
        'incremento': 1
    }
}

# =============================================================================
# CONFIGURACIÓN DE VISUALIZACIÓN
# =============================================================================

# Configuración de matplotlib
MATPLOTLIB_CONFIG = {
    'figsize': (10, 6),
    'dpi': 100,
    'style': 'default',
    'facecolor': '#f8f9fa',
    'tamano_ciclista': 120,
    'alpha_ciclista': 0.95,
    'grosor_borde': 2,
    'zorder_ciclista': 10,
    'zorder_grafo': 5
}

# Colores del sistema
COLORES_SISTEMA = {
    'primario': '#2E86AB',
    'secundario': '#A23B72',
    'exito': '#28a745',
    'advertencia': '#ffc107',
    'peligro': '#dc3545',
    'info': '#17a2b8',
    'gris_claro': '#f8f9fa',
    'gris_medio': '#6c757d',
    'gris_oscuro': '#343a40',
    'blanco': '#ffffff',
    'negro': '#000000'
}

# Colores para nodos del grafo
COLORES_NODOS = [
    '#CC0000', '#006666', '#003366', '#006600', '#CC6600',
    '#660066', '#006633', '#CC9900', '#663399', '#003399',
    '#CC3300', '#006600', '#990000', '#4B0082', '#2F4F2F',
    '#8B4513', '#800080', '#191970', '#2E8B57', '#8B0000'
]

# =============================================================================
# CONFIGURACIÓN DE ARCHIVOS
# =============================================================================

# Extensiones de archivos soportadas
EXTENSIONES_ARCHIVOS = {
    'excel': ['.xlsx', '.xls'],
    'imagen': ['.png', '.jpg', '.jpeg', '.gif'],
    'datos': ['.csv', '.json', '.txt']
}

# Configuración de archivos Excel
EXCEL_CONFIG = {
    'hojas_obligatorias': ['NODOS', 'ARCOS'],
    'hojas_opcionales': ['PERFILES', 'RUTAS'],
    'columnas_nodos': ['NODO', 'ID', 'NOMBRE'],
    'columnas_arcos': ['ORIGEN', 'DESTINO', 'DISTANCIA'],
    'atributos_opcionales': ['SEGURIDAD', 'LUMINOSIDAD', 'INCLINACION', 'PESO_COMPUESTO'],
    'columnas_perfiles': ['PERFILES', 'DISTANCIA', 'SEGURIDAD', 'LUMINOSIDAD', 'INCLINACION'],
    'columnas_rutas': ['NODO']  # Las demás columnas son nodos de destino
}

# =============================================================================
# CONFIGURACIÓN DE DISTRIBUCIONES
# =============================================================================

# Tipos de distribuciones soportadas
TIPOS_DISTRIBUCION = {
    'exponencial': {
        'parametros': ['lambda'],
        'descripcion': 'Distribución exponencial para tiempos entre arribos',
        'parametros_por_defecto': {'lambda': 0.5}
    },
    'poisson': {
        'parametros': ['lambda'],
        'descripcion': 'Distribución de Poisson para número de eventos',
        'parametros_por_defecto': {'lambda': 2.0}
    },
    'uniforme': {
        'parametros': ['min', 'max'],
        'descripcion': 'Distribución uniforme para tiempos constantes',
        'parametros_por_defecto': {'min': 1.0, 'max': 5.0}
    }
}

# Unidades de tiempo soportadas
UNIDADES_TIEMPO = {
    'segundos': 1.0,
    'minutos': 60.0,
    'horas': 3600.0
}

# =============================================================================
# CONFIGURACIÓN DE PERFILES DE CICLISTAS
# =============================================================================

# Atributos de perfiles de ciclistas
ATRIBUTOS_PERFILES = {
    'distancia': {
        'peso_por_defecto': 0.4,
        'descripcion': 'Importancia de la distancia en la ruta',
        'rango': (0.0, 1.0)
    },
    'seguridad': {
        'peso_por_defecto': 0.3,
        'descripcion': 'Importancia de la seguridad en la ruta',
        'rango': (0.0, 1.0)
    },
    'luminosidad': {
        'peso_por_defecto': 0.2,
        'descripcion': 'Importancia de la luminosidad en la ruta',
        'rango': (0.0, 1.0)
    },
    'inclinacion': {
        'peso_por_defecto': 0.1,
        'descripcion': 'Importancia de la inclinación en la ruta',
        'rango': (0.0, 1.0)
    }
}

# =============================================================================
# CONFIGURACIÓN DE RENDIMIENTO
# =============================================================================

# Configuración de cache y optimizaciones
RENDIMIENTO_CONFIG = {
    'max_rutas_por_perfil': 100,
    'max_rutas_total': 500,
    'intervalo_actualizacion_cache': 0.1,  # 100ms
    'max_trayectoria_puntos': 50,
    'max_tiempo_inactivo': 300.0,  # 5 minutos
    'tamaño_pool_ciclistas': 100,
    'tamaño_maximo_pool': 1000
}

# Configuración de límites adaptativos según el tamaño del grafo
LIMITES_ADAPTATIVOS = {
    'pequeno': {  # <= 10 nodos
        'max_rutas_por_perfil': 50,
        'max_rutas_total': 200,
        'max_ciclistas_simultaneos': 50
    },
    'mediano': {  # 11-20 nodos
        'max_rutas_por_perfil': 100,
        'max_rutas_total': 500,
        'max_ciclistas_simultaneos': 100
    },
    'grande': {  # > 20 nodos
        'max_rutas_por_perfil': 200,
        'max_rutas_total': 1000,
        'max_ciclistas_simultaneos': 500
    }
}

# =============================================================================
# CONFIGURACIÓN DE LOGGING
# =============================================================================

# Configuración de logging
LOGGING_CONFIG = {
    'nivel': 'INFO',
    'formato': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'archivo': 'simulador.log',
    'max_tamaño': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# =============================================================================
# CONFIGURACIÓN DE LA INTERFAZ GRÁFICA
# =============================================================================

# Configuración de fuentes
FUENTES_CONFIG = {
    'titulo': ('Segoe UI', 14, 'bold'),
    'subtitulo': ('Segoe UI', 12, 'bold'),
    'normal': ('Segoe UI', 10),
    'pequeno': ('Segoe UI', 9),
    'muy_pequeno': ('Segoe UI', 8)
}

# Configuración de padding
PADDING_CONFIG = {
    'pequeno': 5,
    'medio': 10,
    'grande': 15,
    'muy_grande': 20
}

# Configuración de estilos de widgets
ESTILOS_WIDGETS = {
    'frame_principal': 'TFrame',
    'frame_header': 'Header.TFrame',
    'frame_control': 'Control.TFrame',
    'label_titulo': 'Header.TLabel',
    'label_subtitulo': 'Subheader.TLabel',
    'label_info': 'Info.TLabel',
    'label_exito': 'Success.TLabel',
    'label_advertencia': 'Warning.TLabel',
    'label_peligro': 'Danger.TLabel',
    'button_principal': 'Accent.TButton',
    'button_exito': 'Success.TButton',
    'button_advertencia': 'Warning.TButton',
    'button_peligro': 'Danger.TButton'
}

# =============================================================================
# CONFIGURACIÓN DE VALIDACIÓN
# =============================================================================

# Reglas de validación
VALIDACION_REGLAS = {
    'velocidad_minima': {
        'min': 1.0,
        'max': 20.0,
        'mensaje_error': 'La velocidad mínima debe estar entre 1.0 y 20.0 m/s'
    },
    'velocidad_maxima': {
        'min': 1.0,
        'max': 30.0,
        'mensaje_error': 'La velocidad máxima debe estar entre 1.0 y 30.0 m/s'
    },
    'duracion_simulacion': {
        'min': 60.0,
        'max': 3600.0,
        'mensaje_error': 'La duración debe estar entre 60 y 3600 segundos'
    },
    'suma_pesos_perfil': {
        'valor_objetivo': 1.0,
        'tolerancia': 0.01,
        'mensaje_error': 'La suma de los pesos del perfil debe ser 1.0'
    }
}

# =============================================================================
# CONFIGURACIÓN DE MENSAJES
# =============================================================================

# Mensajes del sistema
MENSAJES_SISTEMA = {
    'bienvenida': {
        'titulo': '🚴 Simulador de Ciclorutas v2.0',
        'mensaje': 'Sistema completo de simulación de redes de ciclorutas'
    },
    'error_carga_archivo': {
        'titulo': 'Error de Carga',
        'mensaje': 'No se pudo cargar el archivo seleccionado'
    },
    'simulacion_completada': {
        'titulo': 'Simulación Completada',
        'mensaje': 'La simulación ha terminado exitosamente'
    },
    'configuracion_aplicada': {
        'titulo': 'Configuración Aplicada',
        'mensaje': 'Los cambios se han aplicado correctamente'
    }
}

# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def obtener_configuracion_completa() -> Dict[str, Any]:
    """Retorna toda la configuración del sistema"""
    return {
        'sistema': SISTEMA_INFO,
        'aplicacion': APP_CONFIG,
        'simulacion': SIMULACION_DEFAULTS,
        'parametros_limites': PARAMETROS_LIMITES,
        'matplotlib': MATPLOTLIB_CONFIG,
        'colores': COLORES_SISTEMA,
        'archivos': EXCEL_CONFIG,
        'distribuciones': TIPOS_DISTRIBUCION,
        'perfiles': ATRIBUTOS_PERFILES,
        'rendimiento': RENDIMIENTO_CONFIG,
        'logging': LOGGING_CONFIG,
        'interfaz': {
            'fuentes': FUENTES_CONFIG,
            'padding': PADDING_CONFIG,
            'estilos': ESTILOS_WIDGETS
        },
        'validacion': VALIDACION_REGLAS,
        'mensajes': MENSAJES_SISTEMA
    }

def obtener_configuracion_por_modulo(modulo: str) -> Dict[str, Any]:
    """Retorna la configuración para un módulo específico"""
    configuraciones = {
        'simulador': {
            'simulacion': SIMULACION_DEFAULTS,
            'parametros_limites': PARAMETROS_LIMITES,
            'rendimiento': RENDIMIENTO_CONFIG,
            'limites_adaptativos': LIMITES_ADAPTATIVOS
        },
        'interfaz': {
            'aplicacion': APP_CONFIG,
            'matplotlib': MATPLOTLIB_CONFIG,
            'colores': COLORES_SISTEMA,
            'fuentes': FUENTES_CONFIG,
            'padding': PADDING_CONFIG,
            'estilos': ESTILOS_WIDGETS
        },
        'archivos': {
            'excel': EXCEL_CONFIG,
            'extensiones': EXTENSIONES_ARCHIVOS
        },
        'distribuciones': {
            'tipos': TIPOS_DISTRIBUCION,
            'unidades_tiempo': UNIDADES_TIEMPO
        },
        'perfiles': {
            'atributos': ATRIBUTOS_PERFILES
        }
    }
    
    return configuraciones.get(modulo, {})

def validar_configuracion(config: Dict[str, Any]) -> List[str]:
    """Valida una configuración y retorna lista de errores"""
    errores = []
    
    # Validar velocidades
    vel_min = config.get('velocidad_minima', 0)
    vel_max = config.get('velocidad_maxima', 0)
    
    if vel_min >= vel_max:
        errores.append("La velocidad mínima debe ser menor que la máxima")
    
    if vel_min < PARAMETROS_LIMITES['velocidad']['min']:
        errores.append(f"La velocidad mínima debe ser al menos {PARAMETROS_LIMITES['velocidad']['min']} m/s")
    
    if vel_max > PARAMETROS_LIMITES['velocidad']['max']:
        errores.append(f"La velocidad máxima no puede exceder {PARAMETROS_LIMITES['velocidad']['max']} m/s")
    
    # Validar duración
    duracion = config.get('duracion_simulacion', 0)
    if duracion < PARAMETROS_LIMITES['duracion']['min']:
        errores.append(f"La duración debe ser al menos {PARAMETROS_LIMITES['duracion']['min']} segundos")
    
    if duracion > PARAMETROS_LIMITES['duracion']['max']:
        errores.append(f"La duración no puede exceder {PARAMETROS_LIMITES['duracion']['max']} segundos")
    
    return errores

def aplicar_configuracion_por_defecto() -> Dict[str, Any]:
    """Retorna la configuración por defecto del sistema"""
    return SIMULACION_DEFAULTS.copy()
