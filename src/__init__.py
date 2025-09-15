#!/usr/bin/env python3
"""
🚴 SIMULADOR DE CICLORUTAS - PAQUETE PRINCIPAL 🚴

Este es el paquete principal del simulador de ciclorutas.
Contiene todos los módulos necesarios para la simulación.

Autor: Sistema de Simulación de Ciclorutas
Versión: 2.0 (Refactorizado)
"""

__version__ = "2.0.0"
__author__ = "Sistema de Simulación de Ciclorutas"
__description__ = "Simulador avanzado de ciclorutas con interfaz gráfica"

# Importar clases principales para facilitar el acceso
from .core.simulador import SimuladorCiclorutas
from .config.configuracion import ConfiguracionSimulacion, ConfiguracionesPredefinidas

# Exportar las clases principales
__all__ = [
    'SimuladorCiclorutas',
    'ConfiguracionSimulacion',
    'ConfiguracionesPredefinidas'
]
