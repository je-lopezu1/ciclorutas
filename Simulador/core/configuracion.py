"""
Configuración centralizada del simulador de ciclorutas.

Este módulo contiene todas las configuraciones y constantes del sistema.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class ConfiguracionSimulacion:
    """Clase para almacenar la configuración de la simulación"""
    
    # Configuración de velocidades
    velocidad_min: float = 10.0
    velocidad_max: float = 15.0
    
    # Configuración de tiempo
    duracion_simulacion: float = 300.0  # Duración en segundos
    
    # Configuración de memoria y rendimiento
    max_ciclistas_simultaneos: int = 1000
    max_trayectoria_puntos: int = 50
    max_tiempo_inactivo: float = 300.0  # 5 minutos
    
    # Configuración de cache
    max_rutas_por_perfil: int = 100
    max_rutas_total: int = 500
    intervalo_actualizacion_cache: float = 0.1  # 100ms
    
    # Configuración de visualización
    tamano_ciclista: int = 120
    alpha_ciclista: float = 0.95
    grosor_borde: int = 2
    
    def __post_init__(self):
        """Validar configuración después de la inicialización"""
        self._validar_configuracion()
    
    def _validar_configuracion(self):
        """Valida que la configuración sea correcta"""
        if self.velocidad_min >= self.velocidad_max:
            raise ValueError("La velocidad mínima debe ser menor que la máxima")
        
        if self.velocidad_min < 0 or self.velocidad_max < 0:
            raise ValueError("Las velocidades no pueden ser negativas")
        
        if self.duracion_simulacion <= 0:
            raise ValueError("La duración de simulación debe ser positiva")
        
        if self.max_ciclistas_simultaneos <= 0:
            raise ValueError("El máximo de ciclistas debe ser positivo")
    
    def actualizar_velocidades(self, vel_min: float, vel_max: float):
        """Actualiza las velocidades y valida la configuración"""
        self.velocidad_min = vel_min
        self.velocidad_max = vel_max
        self._validar_configuracion()
    
    def actualizar_duracion(self, duracion: float):
        """Actualiza la duración de simulación"""
        if duracion <= 0:
            raise ValueError("La duración debe ser positiva")
        self.duracion_simulacion = duracion
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la configuración a diccionario"""
        return {
            'velocidad_min': self.velocidad_min,
            'velocidad_max': self.velocidad_max,
            'duracion_simulacion': self.duracion_simulacion,
            'max_ciclistas_simultaneos': self.max_ciclistas_simultaneos,
            'max_trayectoria_puntos': self.max_trayectoria_puntos,
            'max_tiempo_inactivo': self.max_tiempo_inactivo,
            'max_rutas_por_perfil': self.max_rutas_por_perfil,
            'max_rutas_total': self.max_rutas_total,
            'intervalo_actualizacion_cache': self.intervalo_actualizacion_cache,
            'tamano_ciclista': self.tamano_ciclista,
            'alpha_ciclista': self.alpha_ciclista,
            'grosor_borde': self.grosor_borde
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ConfiguracionSimulacion':
        """Crea una configuración desde un diccionario"""
        return cls(**config_dict)


# Configuraciones por defecto para diferentes escenarios
CONFIGURACIONES_PREDEFINIDAS = {
    'basica': ConfiguracionSimulacion(
        velocidad_min=8.0,
        velocidad_max=12.0,
        duracion_simulacion=180.0,
        max_ciclistas_simultaneos=50
    ),
    
    'intermedia': ConfiguracionSimulacion(
        velocidad_min=10.0,
        velocidad_max=15.0,
        duracion_simulacion=300.0,
        max_ciclistas_simultaneos=100
    ),
    
    'avanzada': ConfiguracionSimulacion(
        velocidad_min=12.0,
        velocidad_max=20.0,
        duracion_simulacion=600.0,
        max_ciclistas_simultaneos=500,
        max_rutas_por_perfil=200,
        max_rutas_total=1000
    ),
    
    'rendimiento': ConfiguracionSimulacion(
        velocidad_min=15.0,
        velocidad_max=25.0,
        duracion_simulacion=1200.0,
        max_ciclistas_simultaneos=1000,
        max_rutas_por_perfil=500,
        max_rutas_total=2000,
        intervalo_actualizacion_cache=0.05  # 50ms para mayor responsividad
    )
}


def obtener_configuracion(nombre: str = 'intermedia') -> ConfiguracionSimulacion:
    """Obtiene una configuración predefinida por nombre"""
    if nombre not in CONFIGURACIONES_PREDEFINIDAS:
        raise ValueError(f"Configuración '{nombre}' no encontrada. "
                        f"Disponibles: {list(CONFIGURACIONES_PREDEFINIDAS.keys())}")
    
    return CONFIGURACIONES_PREDEFINIDAS[nombre]
