#!/usr/bin/env python3
"""
📊 MÓDULO DE DISTRIBUCIONES - SIMULADOR DE CICLORUTAS 📊

Este módulo contiene las clases y funciones para manejar distribuciones
de probabilidad para las tasas de arribo de ciclistas.

Autor: Sistema de Simulación de Ciclorutas
Versión: 2.0 (Refactorizado)
"""

import numpy as np
from typing import Dict, List, Optional, Union
from enum import Enum


class TipoDistribucion(Enum):
    """Tipos de distribución soportados."""
    EXPONENCIAL = "exponencial"
    POISSON = "poisson"
    UNIFORME = "uniforme"
    NORMAL = "normal"
    GAMMA = "gamma"


class DistribucionNodo:
    """
    Clase para manejar distribuciones de probabilidad para tasas de arribo por nodo.
    
    Esta clase encapsula la lógica para generar tiempos de arribo basados en
    diferentes distribuciones de probabilidad.
    """
    
    def __init__(self, tipo: Union[str, TipoDistribucion] = 'exponencial', 
                 parametros: Optional[Dict] = None):
        """
        Inicializa una distribución de probabilidad.
        
        Args:
            tipo: Tipo de distribución (exponencial, poisson, uniforme, normal, gamma)
            parametros: Parámetros específicos de la distribución
        """
        self.tipo = TipoDistribucion(tipo.lower()) if isinstance(tipo, str) else tipo
        self.parametros = parametros or {}
        self._validar_y_ajustar_parametros()
    
    def _validar_y_ajustar_parametros(self):
        """Valida y ajusta los parámetros según el tipo de distribución."""
        if self.tipo == TipoDistribucion.EXPONENCIAL:
            self.parametros.setdefault('lambda', 0.5)
            if self.parametros['lambda'] <= 0:
                self.parametros['lambda'] = 0.5
                
        elif self.tipo == TipoDistribucion.POISSON:
            self.parametros.setdefault('lambda', 2.0)
            if self.parametros['lambda'] <= 0:
                self.parametros['lambda'] = 2.0
                
        elif self.tipo == TipoDistribucion.UNIFORME:
            self.parametros.setdefault('min', 1.0)
            self.parametros.setdefault('max', 5.0)
            if self.parametros['min'] >= self.parametros['max']:
                self.parametros['min'] = 1.0
                self.parametros['max'] = 5.0
                
        elif self.tipo == TipoDistribucion.NORMAL:
            self.parametros.setdefault('mu', 3.0)  # Media
            self.parametros.setdefault('sigma', 1.0)  # Desviación estándar
            if self.parametros['sigma'] <= 0:
                self.parametros['sigma'] = 1.0
                
        elif self.tipo == TipoDistribucion.GAMMA:
            self.parametros.setdefault('shape', 2.0)  # Forma
            self.parametros.setdefault('scale', 1.0)  # Escala
            if self.parametros['shape'] <= 0 or self.parametros['scale'] <= 0:
                self.parametros['shape'] = 2.0
                self.parametros['scale'] = 1.0
    
    def generar_tiempo_arribo(self) -> float:
        """
        Genera un tiempo de arribo basado en la distribución configurada.
        
        Returns:
            float: Tiempo de arribo en segundos
        """
        try:
            if self.tipo == TipoDistribucion.EXPONENCIAL:
                # Distribución exponencial: tiempo entre arribos
                return np.random.exponential(1.0 / self.parametros['lambda'])
                
            elif self.tipo == TipoDistribucion.POISSON:
                # Distribución de Poisson: número de eventos por unidad de tiempo
                eventos = np.random.poisson(self.parametros['lambda'])
                return max(0.1, eventos)  # Mínimo 0.1 segundos
                
            elif self.tipo == TipoDistribucion.UNIFORME:
                # Distribución uniforme: tiempo constante entre min y max
                return np.random.uniform(self.parametros['min'], self.parametros['max'])
                
            elif self.tipo == TipoDistribucion.NORMAL:
                # Distribución normal (truncada para valores positivos)
                tiempo = np.random.normal(self.parametros['mu'], self.parametros['sigma'])
                return max(0.1, abs(tiempo))  # Asegurar valor positivo
                
            elif self.tipo == TipoDistribucion.GAMMA:
                # Distribución gamma
                tiempo = np.random.gamma(self.parametros['shape'], self.parametros['scale'])
                return max(0.1, tiempo)  # Asegurar valor positivo
                
            else:
                return 1.0  # Fallback
                
        except Exception as e:
            print(f"⚠️ Error generando tiempo de arribo: {e}")
            return 1.0  # Fallback en caso de error
    
    def obtener_descripcion(self) -> str:
        """
        Retorna una descripción legible de la distribución.
        
        Returns:
            str: Descripción de la distribución y sus parámetros
        """
        if self.tipo == TipoDistribucion.EXPONENCIAL:
            return f"Exponencial (λ={self.parametros['lambda']:.3f})"
        elif self.tipo == TipoDistribucion.POISSON:
            return f"Poisson (λ={self.parametros['lambda']:.3f})"
        elif self.tipo == TipoDistribucion.UNIFORME:
            return f"Uniforme ({self.parametros['min']:.1f}-{self.parametros['max']:.1f}s)"
        elif self.tipo == TipoDistribucion.NORMAL:
            return f"Normal (μ={self.parametros['mu']:.1f}, σ={self.parametros['sigma']:.1f})"
        elif self.tipo == TipoDistribucion.GAMMA:
            return f"Gamma (α={self.parametros['shape']:.1f}, β={self.parametros['scale']:.1f})"
        else:
            return "Desconocida"
    
    def actualizar_parametros(self, nuevos_parametros: Dict):
        """
        Actualiza los parámetros de la distribución.
        
        Args:
            nuevos_parametros: Nuevos parámetros para la distribución
        """
        self.parametros.update(nuevos_parametros)
        self._validar_y_ajustar_parametros()
    
    def cambiar_tipo(self, nuevo_tipo: Union[str, TipoDistribucion]):
        """
        Cambia el tipo de distribución.
        
        Args:
            nuevo_tipo: Nuevo tipo de distribución
        """
        self.tipo = TipoDistribucion(nuevo_tipo.lower()) if isinstance(nuevo_tipo, str) else nuevo_tipo
        self.parametros = {}  # Resetear parámetros
        self._validar_y_ajustar_parametros()
    
    def obtener_estadisticas_muestra(self, tamaño_muestra: int = 1000) -> Dict[str, float]:
        """
        Calcula estadísticas de una muestra de la distribución.
        
        Args:
            tamaño_muestra: Tamaño de la muestra para calcular estadísticas
            
        Returns:
            Dict[str, float]: Estadísticas de la muestra
        """
        muestra = [self.generar_tiempo_arribo() for _ in range(tamaño_muestra)]
        
        return {
            'media': np.mean(muestra),
            'mediana': np.median(muestra),
            'desviacion_estandar': np.std(muestra),
            'minimo': np.min(muestra),
            'maximo': np.max(muestra),
            'percentil_25': np.percentile(muestra, 25),
            'percentil_75': np.percentile(muestra, 75)
        }
    
    def __str__(self) -> str:
        """Representación string de la distribución."""
        return f"DistribucionNodo(tipo={self.tipo.value}, {self.obtener_descripcion()})"
    
    def __repr__(self) -> str:
        """Representación detallada de la distribución."""
        return self.__str__()


class GestorDistribuciones:
    """
    Gestor para manejar múltiples distribuciones de nodos.
    
    Esta clase facilita la gestión de distribuciones para múltiples nodos
    y proporciona funcionalidades de análisis y comparación.
    """
    
    def __init__(self):
        """Inicializa el gestor de distribuciones."""
        self.distribuciones: Dict[str, DistribucionNodo] = {}
    
    def agregar_distribucion(self, nodo_id: str, distribucion: DistribucionNodo):
        """
        Agrega una distribución para un nodo específico.
        
        Args:
            nodo_id: Identificador del nodo
            distribucion: Distribución a asignar al nodo
        """
        self.distribuciones[nodo_id] = distribucion
    
    def obtener_distribucion(self, nodo_id: str) -> Optional[DistribucionNodo]:
        """
        Obtiene la distribución de un nodo.
        
        Args:
            nodo_id: Identificador del nodo
            
        Returns:
            DistribucionNodo o None si no existe
        """
        return self.distribuciones.get(nodo_id)
    
    def generar_tiempo_arribo_nodo(self, nodo_id: str) -> float:
        """
        Genera un tiempo de arribo para un nodo específico.
        
        Args:
            nodo_id: Identificador del nodo
            
        Returns:
            float: Tiempo de arribo en segundos
        """
        distribucion = self.obtener_distribucion(nodo_id)
        if distribucion:
            return distribucion.generar_tiempo_arribo()
        else:
            # Distribución por defecto si no está configurada
            return np.random.exponential(2.0)  # 0.5 arribos por segundo
    
    def obtener_todas_distribuciones(self) -> Dict[str, Dict]:
        """
        Retorna la configuración de todas las distribuciones.
        
        Returns:
            Dict[str, Dict]: Configuración de todas las distribuciones
        """
        resultado = {}
        for nodo_id, distribucion in self.distribuciones.items():
            resultado[nodo_id] = {
                'tipo': distribucion.tipo.value,
                'parametros': distribucion.parametros.copy(),
                'descripcion': distribucion.obtener_descripcion()
            }
        return resultado
    
    def actualizar_distribucion_nodo(self, nodo_id: str, tipo: str, parametros: Dict):
        """
        Actualiza la distribución de un nodo específico.
        
        Args:
            nodo_id: Identificador del nodo
            tipo: Tipo de distribución
            parametros: Parámetros de la distribución
        """
        self.distribuciones[nodo_id] = DistribucionNodo(tipo, parametros)
    
    def obtener_nodos_con_distribucion(self) -> List[str]:
        """
        Retorna la lista de nodos que tienen distribución configurada.
        
        Returns:
            List[str]: Lista de identificadores de nodos
        """
        return list(self.distribuciones.keys())
    
    def limpiar_distribuciones(self):
        """Limpia todas las distribuciones configuradas."""
        self.distribuciones.clear()
    
    def __len__(self) -> int:
        """Retorna el número de distribuciones configuradas."""
        return len(self.distribuciones)
    
    def __str__(self) -> str:
        """Representación string del gestor."""
        return f"GestorDistribuciones({len(self.distribuciones)} distribuciones)"


# Funciones de utilidad para crear distribuciones comunes
def crear_distribucion_exponencial(lambda_val: float) -> DistribucionNodo:
    """Crea una distribución exponencial con el parámetro lambda especificado."""
    return DistribucionNodo('exponencial', {'lambda': lambda_val})


def crear_distribucion_poisson(lambda_val: float) -> DistribucionNodo:
    """Crea una distribución de Poisson con el parámetro lambda especificado."""
    return DistribucionNodo('poisson', {'lambda': lambda_val})


def crear_distribucion_uniforme(min_val: float, max_val: float) -> DistribucionNodo:
    """Crea una distribución uniforme con los valores mínimo y máximo especificados."""
    return DistribucionNodo('uniforme', {'min': min_val, 'max': max_val})


def crear_distribucion_normal(mu: float, sigma: float) -> DistribucionNodo:
    """Crea una distribución normal con la media y desviación estándar especificadas."""
    return DistribucionNodo('normal', {'mu': mu, 'sigma': sigma})


def crear_distribucion_gamma(shape: float, scale: float) -> DistribucionNodo:
    """Crea una distribución gamma con los parámetros de forma y escala especificados."""
    return DistribucionNodo('gamma', {'shape': shape, 'scale': scale})
