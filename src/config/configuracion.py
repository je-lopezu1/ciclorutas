


#!/usr/bin/env python3
"""
🔧 MÓDULO DE CONFIGURACIÓN - SIMULADOR DE CICLORUTAS 🔧

Este módulo contiene las clases y estructuras de datos para la configuración
de la simulación de ciclorutas.

Autor: Sistema de Simulación de Ciclorutas
Versión: 2.0 (Refactorizado)
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class ConfiguracionSimulacion:
    """
    Clase para almacenar la configuración de la simulación.
    
    Esta clase centraliza todos los parámetros configurables del simulador,
    facilitando la gestión y validación de la configuración.
    """
    
    # Parámetros de velocidad
    velocidad_min: float = 10.0
    velocidad_max: float = 15.0
    
    # Duración de la simulación
    duracion_simulacion: float = 300.0  # Duración en segundos
    
    # Parámetros de generación de ciclistas
    max_ciclistas_simultaneos: int = 100
    
    # Parámetros de visualización
    intervalo_actualizacion: float = 0.05  # Intervalo entre actualizaciones en segundos
    max_trayectorias_por_ciclista: int = 1000  # Límite de puntos de trayectoria
    
    # Parámetros de red
    distancia_por_defecto: float = 50.0  # Distancia por defecto para arcos sin peso
    
    def validar_configuracion(self) -> bool:
        """
        Valida que la configuración sea correcta.
        
        Returns:
            bool: True si la configuración es válida, False en caso contrario
        """
        if self.velocidad_min <= 0:
            return False
        if self.velocidad_max <= 0:
            return False
        if self.velocidad_min >= self.velocidad_max:
            return False
        if self.duracion_simulacion <= 0:
            return False
        if self.max_ciclistas_simultaneos <= 0:
            return False
        if self.intervalo_actualizacion <= 0:
            return False
        if self.max_trayectorias_por_ciclista <= 0:
            return False
        if self.distancia_por_defecto <= 0:
            return False
        
        return True
    
    def obtener_resumen(self) -> Dict[str, Any]:
        """
        Retorna un resumen de la configuración actual.
        
        Returns:
            Dict[str, Any]: Diccionario con los parámetros de configuración
        """
        return {
            'velocidad_min': self.velocidad_min,
            'velocidad_max': self.velocidad_max,
            'duracion_simulacion': self.duracion_simulacion,
            'max_ciclistas_simultaneos': self.max_ciclistas_simultaneos,
            'intervalo_actualizacion': self.intervalo_actualizacion,
            'max_trayectorias_por_ciclista': self.max_trayectorias_por_ciclista,
            'distancia_por_defecto': self.distancia_por_defecto,
            'valida': self.validar_configuracion()
        }
    
    def actualizar_parametros(self, **kwargs) -> bool:
        """
        Actualiza parámetros de configuración.
        
        Args:
            **kwargs: Parámetros a actualizar
            
        Returns:
            bool: True si la actualización fue exitosa, False en caso contrario
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
                else:
                    print(f"⚠️ Advertencia: Parámetro '{key}' no existe en la configuración")
                    return False
            
            # Validar la nueva configuración
            if not self.validar_configuracion():
                print("❌ Error: La nueva configuración no es válida")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error actualizando configuración: {e}")
            return False
    
    def __str__(self) -> str:
        """Representación string de la configuración."""
        return (f"ConfiguracionSimulacion("
                f"velocidad_min={self.velocidad_min}, "
                f"velocidad_max={self.velocidad_max}, "
                f"duracion={self.duracion_simulacion}s, "
                f"max_ciclistas={self.max_ciclistas_simultaneos})")
    
    def __repr__(self) -> str:
        """Representación detallada de la configuración."""
        return self.__str__()


# Configuraciones predefinidas para casos comunes
class ConfiguracionesPredefinidas:
    """Configuraciones predefinidas para diferentes escenarios de simulación."""
    
    @staticmethod
    def simulacion_rapida() -> ConfiguracionSimulacion:
        """Configuración para simulación rápida (testing)."""
        return ConfiguracionSimulacion(
            velocidad_min=15.0,
            velocidad_max=25.0,
            duracion_simulacion=60.0,
            max_ciclistas_simultaneos=20,
            intervalo_actualizacion=0.1
        )
    
    @staticmethod
    def simulacion_realista() -> ConfiguracionSimulacion:
        """Configuración para simulación realista."""
        return ConfiguracionSimulacion(
            velocidad_min=8.0,
            velocidad_max=18.0,
            duracion_simulacion=600.0,
            max_ciclistas_simultaneos=50,
            intervalo_actualizacion=0.05
        )
    
    @staticmethod
    def simulacion_intensiva() -> ConfiguracionSimulacion:
        """Configuración para simulación intensiva (muchos ciclistas)."""
        return ConfiguracionSimulacion(
            velocidad_min=5.0,
            velocidad_max=20.0,
            duracion_simulacion=1200.0,
            max_ciclistas_simultaneos=200,
            intervalo_actualizacion=0.02
        )
