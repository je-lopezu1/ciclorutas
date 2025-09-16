"""
🖥️ INTERFAZ DE SIMULACIÓN - MÓDULO PRINCIPAL 🖥️

Este paquete contiene todos los componentes de la interfaz gráfica del simulador.
Incluye paneles, componentes UI, utilidades y la aplicación principal.

Autor: Sistema de Simulación de Ciclorutas
Versión: 2.0 (Refactorizado)
"""

from .components.app_principal import InterfazSimulacion
from .panels.panel_control import PanelControl
from .panels.panel_visualizacion import PanelVisualizacion
from .panels.panel_estadisticas import PanelEstadisticas
from .panels.panel_distribuciones import PanelDistribuciones

__version__ = "2.0.0"
__author__ = "Sistema de Simulación de Ciclorutas"

# Exportar clases principales para facilitar el uso
__all__ = [
    'InterfazSimulacion',
    'PanelControl',
    'PanelVisualizacion', 
    'PanelEstadisticas',
    'PanelDistribuciones'
]
