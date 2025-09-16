"""
🚴 SIMULADOR DE CICLORUTAS - MÓDULO PRINCIPAL 🚴

Este paquete contiene toda la lógica de simulación del sistema de ciclorutas.
Incluye modelos, distribuciones, utilidades y el motor de simulación principal.

Autor: Sistema de Simulación de Ciclorutas
Versión: 2.0 (Refactorizado)
"""

from .core.simulador import SimuladorCiclorutas
from .core.configuracion import ConfiguracionSimulacion
from .models.ciclista import Ciclista, PoolCiclistas
from .distributions.distribucion_nodo import DistribucionNodo

__version__ = "2.0.0"
__author__ = "Sistema de Simulación de Ciclorutas"

# Exportar clases principales para facilitar el uso
__all__ = [
    'SimuladorCiclorutas',
    'ConfiguracionSimulacion', 
    'Ciclista',
    'PoolCiclistas',
    'DistribucionNodo'
]
