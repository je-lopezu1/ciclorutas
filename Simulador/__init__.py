"""
🚴 SIMULADOR DE CICLORUTAS - MÓDULO PRINCIPAL 🚴

Este paquete contiene toda la lógica de simulación del sistema de ciclorutas.
Incluye modelos, distribuciones, utilidades y el motor de simulación principal.

Desarrollado como herramienta para tesis de pregrado en Ingeniería de Sistemas y Computación
de la Universidad de los Andes, Colombia (2025).

Autor: Sistema de Simulación de Ciclorutas
Versión: 2.0.0 (Refactorizado)
Versión inicial: 1.0.0 (Tesis de Pregrado, Universidad de los Andes, Colombia, 2025)
"""

from .core.simulador import SimuladorCiclorutas
from .core.configuracion import ConfiguracionSimulacion
from .models.ciclista import Ciclista, PoolCiclistas
from .distributions.distribucion_nodo import DistribucionNodo

__version__ = "2.0.0"
__version_inicial__ = "1.0.0"
__author__ = "Sistema de Simulación de Ciclorutas"
__institucion__ = "Universidad de los Andes, Colombia"
__contexto__ = "Tesis de Pregrado en Ingeniería de Sistemas y Computación (2025)"

# Exportar clases principales para facilitar el uso
__all__ = [
    'SimuladorCiclorutas',
    'ConfiguracionSimulacion', 
    'Ciclista',
    'PoolCiclistas',
    'DistribucionNodo'
]
