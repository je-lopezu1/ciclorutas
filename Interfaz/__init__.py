"""
🖥️ INTERFAZ DE SIMULACIÓN - MÓDULO PRINCIPAL 🖥️

Este paquete contiene todos los componentes de la interfaz gráfica del simulador.
Incluye paneles, componentes UI, utilidades y la aplicación principal.

Desarrollado como herramienta para tesis de pregrado en Ingeniería de Sistemas y Computación
de la Universidad de los Andes, Colombia (2025).

Autor: Sistema de Simulación de Ciclorutas
Versión: 2.0.0 (Refactorizado)
Versión inicial: 1.0.0 (Tesis de Pregrado, Universidad de los Andes, Colombia, 2025)
"""

from .components.app_principal import InterfazSimulacion
from .panels.panel_control import PanelControl
from .panels.panel_visualizacion import PanelVisualizacion
from .panels.panel_estadisticas import PanelEstadisticas
from .panels.panel_distribuciones import PanelDistribuciones

__version__ = "2.0.0"
__version_inicial__ = "1.0.0"
__author__ = "Sistema de Simulación de Ciclorutas"
__institucion__ = "Universidad de los Andes, Colombia"
__contexto__ = "Tesis de Pregrado en Ingeniería de Sistemas y Computación (2025)"

# Exportar clases principales para facilitar el uso
__all__ = [
    'InterfazSimulacion',
    'PanelControl',
    'PanelVisualizacion', 
    'PanelEstadisticas',
    'PanelDistribuciones'
]
