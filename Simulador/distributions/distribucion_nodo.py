"""
Distribuciones de probabilidad para tasas de arribo por nodo.

Este módulo maneja diferentes tipos de distribuciones estadísticas
para modelar la llegada de ciclistas a cada nodo de la red.
"""

import numpy as np
from typing import Dict, List, Optional
from abc import ABC, abstractmethod


class DistribucionBase(ABC):
    """Clase base abstracta para distribuciones de probabilidad"""
    
    def __init__(self, parametros: Dict):
        self.parametros = parametros
        self._validar_parametros()
    
    @abstractmethod
    def _validar_parametros(self):
        """Valida los parámetros específicos de la distribución"""
        pass
    
    @abstractmethod
    def generar_tiempo_arribo(self) -> float:
        """Genera un tiempo de arribo basado en la distribución"""
        pass
    
    @abstractmethod
    def obtener_descripcion(self) -> str:
        """Retorna una descripción legible de la distribución"""
        pass


class DistribucionExponencial(DistribucionBase):
    """Distribución exponencial para tiempos entre arribos"""
    
    def _validar_parametros(self):
        """Valida parámetros para distribución exponencial"""
        self.parametros.setdefault('lambda', 0.5)
        if self.parametros['lambda'] <= 0:
            self.parametros['lambda'] = 0.5
    
    def generar_tiempo_arribo(self) -> float:
        """Genera tiempo de arribo usando distribución exponencial"""
        try:
            return np.random.exponential(1.0 / self.parametros['lambda'])
        except Exception:
            return 1.0  # Fallback
    
    def obtener_descripcion(self) -> str:
        """Retorna descripción de la distribución exponencial"""
        return f"Exponencial (λ={self.parametros['lambda']:.2f})"


class DistribucionPoisson(DistribucionBase):
    """Distribución de Poisson para número de eventos por unidad de tiempo"""
    
    def _validar_parametros(self):
        """Valida parámetros para distribución de Poisson"""
        self.parametros.setdefault('lambda', 2.0)
        if self.parametros['lambda'] <= 0:
            self.parametros['lambda'] = 2.0
    
    def generar_tiempo_arribo(self) -> float:
        """Genera tiempo de arribo usando distribución de Poisson"""
        try:
            eventos = np.random.poisson(self.parametros['lambda'])
            return max(0.1, eventos)  # Mínimo 0.1 segundos
        except Exception:
            return 1.0  # Fallback
    
    def obtener_descripcion(self) -> str:
        """Retorna descripción de la distribución de Poisson"""
        return f"Poisson (λ={self.parametros['lambda']:.2f})"


class DistribucionUniforme(DistribucionBase):
    """Distribución uniforme para tiempos constantes entre min y max"""
    
    def _validar_parametros(self):
        """Valida parámetros para distribución uniforme"""
        self.parametros.setdefault('min', 1.0)
        self.parametros.setdefault('max', 5.0)
        if self.parametros['min'] >= self.parametros['max']:
            self.parametros['min'] = 1.0
            self.parametros['max'] = 5.0
    
    def generar_tiempo_arribo(self) -> float:
        """Genera tiempo de arribo usando distribución uniforme"""
        try:
            return np.random.uniform(self.parametros['min'], self.parametros['max'])
        except Exception:
            return 1.0  # Fallback
    
    def obtener_descripcion(self) -> str:
        """Retorna descripción de la distribución uniforme"""
        return f"Uniforme ({self.parametros['min']:.1f}-{self.parametros['max']:.1f}s)"


class DistribucionNormal(DistribucionBase):
    """Distribución normal (gaussiana) para tiempos de arribo"""
    
    def _validar_parametros(self):
        """Valida parámetros para distribución normal"""
        self.parametros.setdefault('media', 3.0)
        self.parametros.setdefault('desviacion', 1.0)
        if self.parametros['desviacion'] <= 0:
            self.parametros['desviacion'] = 1.0
    
    def generar_tiempo_arribo(self) -> float:
        """Genera tiempo de arribo usando distribución normal"""
        try:
            tiempo = np.random.normal(self.parametros['media'], self.parametros['desviacion'])
            return max(0.1, tiempo)  # Asegurar valor positivo mínimo
        except Exception:
            return 1.0  # Fallback
    
    def obtener_descripcion(self) -> str:
        """Retorna descripción de la distribución normal"""
        return f"Normal (μ={self.parametros['media']:.2f}, σ={self.parametros['desviacion']:.2f})"


class DistribucionLogNormal(DistribucionBase):
    """Distribución log-normal para tiempos de arribo"""
    
    def _validar_parametros(self):
        """Valida parámetros para distribución log-normal"""
        self.parametros.setdefault('mu', 0.0)  # Parámetro de localización
        self.parametros.setdefault('sigma', 1.0)  # Parámetro de escala
        if self.parametros['sigma'] <= 0:
            self.parametros['sigma'] = 1.0
    
    def generar_tiempo_arribo(self) -> float:
        """Genera tiempo de arribo usando distribución log-normal"""
        try:
            tiempo = np.random.lognormal(self.parametros['mu'], self.parametros['sigma'])
            return max(0.1, tiempo)  # Asegurar valor positivo mínimo
        except Exception:
            return 1.0  # Fallback
    
    def obtener_descripcion(self) -> str:
        """Retorna descripción de la distribución log-normal"""
        return f"Log-Normal (μ={self.parametros['mu']:.2f}, σ={self.parametros['sigma']:.2f})"


class DistribucionGamma(DistribucionBase):
    """Distribución gamma para tiempos de arribo"""
    
    def _validar_parametros(self):
        """Valida parámetros para distribución gamma"""
        self.parametros.setdefault('forma', 2.0)  # Parámetro de forma (alpha)
        self.parametros.setdefault('escala', 1.0)  # Parámetro de escala (beta)
        if self.parametros['forma'] <= 0:
            self.parametros['forma'] = 2.0
        if self.parametros['escala'] <= 0:
            self.parametros['escala'] = 1.0
    
    def generar_tiempo_arribo(self) -> float:
        """Genera tiempo de arribo usando distribución gamma"""
        try:
            tiempo = np.random.gamma(self.parametros['forma'], self.parametros['escala'])
            return max(0.1, tiempo)  # Asegurar valor positivo mínimo
        except Exception:
            return 1.0  # Fallback
    
    def obtener_descripcion(self) -> str:
        """Retorna descripción de la distribución gamma"""
        return f"Gamma (α={self.parametros['forma']:.2f}, β={self.parametros['escala']:.2f})"


class DistribucionWeibull(DistribucionBase):
    """Distribución Weibull para tiempos de arribo"""
    
    def _validar_parametros(self):
        """Valida parámetros para distribución Weibull"""
        self.parametros.setdefault('forma', 2.0)  # Parámetro de forma (c)
        self.parametros.setdefault('escala', 1.0)  # Parámetro de escala (λ)
        if self.parametros['forma'] <= 0:
            self.parametros['forma'] = 2.0
        if self.parametros['escala'] <= 0:
            self.parametros['escala'] = 1.0
    
    def generar_tiempo_arribo(self) -> float:
        """Genera tiempo de arribo usando distribución Weibull"""
        try:
            tiempo = np.random.weibull(self.parametros['forma']) * self.parametros['escala']
            return max(0.1, tiempo)  # Asegurar valor positivo mínimo
        except Exception:
            return 1.0  # Fallback
    
    def obtener_descripcion(self) -> str:
        """Retorna descripción de la distribución Weibull"""
        return f"Weibull (c={self.parametros['forma']:.2f}, λ={self.parametros['escala']:.2f})"


class DistribucionNodo:
    """Clase principal para manejar distribuciones de probabilidad para tasas de arribo por nodo"""
    
    # Registro de tipos de distribución disponibles
    TIPOS_DISTRIBUCION = {
        'exponencial': DistribucionExponencial,
        'normal': DistribucionNormal,
        'lognormal': DistribucionLogNormal,
        'gamma': DistribucionGamma,
        'weibull': DistribucionWeibull
    }
    
    def __init__(self, tipo: str = 'exponencial', parametros: Dict = None):
        self.tipo = tipo.lower()
        self.parametros = parametros or {}
        self._distribucion = self._crear_distribucion()
    
    def _crear_distribucion(self) -> DistribucionBase:
        """Crea la instancia de distribución correspondiente"""
        if self.tipo not in self.TIPOS_DISTRIBUCION:
            print(f"⚠️ Tipo de distribución '{self.tipo}' no reconocido. Usando exponencial.")
            self.tipo = 'exponencial'
        
        clase_distribucion = self.TIPOS_DISTRIBUCION[self.tipo]
        return clase_distribucion(self.parametros)
    
    def generar_tiempo_arribo(self) -> float:
        """Genera un tiempo de arribo basado en la distribución configurada"""
        return self._distribucion.generar_tiempo_arribo()
    
    def obtener_descripcion(self) -> str:
        """Retorna una descripción legible de la distribución"""
        return self._distribucion.obtener_descripcion()
    
    def actualizar_parametros(self, nuevos_parametros: Dict):
        """Actualiza los parámetros de la distribución"""
        self.parametros.update(nuevos_parametros)
        self._distribucion = self._crear_distribucion()
    
    def cambiar_tipo(self, nuevo_tipo: str, parametros: Dict = None):
        """Cambia el tipo de distribución"""
        self.tipo = nuevo_tipo.lower()
        if parametros is not None:
            self.parametros = parametros
        self._distribucion = self._crear_distribucion()
    
    def obtener_parametros(self) -> Dict:
        """Retorna los parámetros actuales de la distribución"""
        return self.parametros.copy()
    
    def obtener_tipo(self) -> str:
        """Retorna el tipo de distribución actual"""
        return self.tipo
    
    @classmethod
    def crear_por_defecto(cls, nodo_id: str, indice: int = 0) -> 'DistribucionNodo':
        """Crea una distribución por defecto para un nodo"""
        # Distribución exponencial por defecto con tasas variadas
        lambda_val = 0.3 + (indice * 0.2)  # Tasas de 0.3 a 0.9
        return cls('exponencial', {'lambda': lambda_val})
    
    @classmethod
    def crear_desde_configuracion(cls, config: Dict) -> 'DistribucionNodo':
        """Crea una distribución desde una configuración"""
        tipo = config.get('tipo', 'exponencial')
        parametros = config.get('parametros', {})
        return cls(tipo, parametros)
    
    def to_dict(self) -> Dict:
        """Convierte la distribución a diccionario para serialización"""
        return {
            'tipo': self.tipo,
            'parametros': self.parametros.copy(),
            'descripcion': self.obtener_descripcion()
        }


class GestorDistribuciones:
    """Gestor centralizado para todas las distribuciones de nodos"""
    
    def __init__(self):
        self.distribuciones = {}  # Dict[nodo_id, DistribucionNodo]
    
    def configurar_nodo(self, nodo_id: str, tipo: str, parametros: Dict):
        """Configura la distribución para un nodo específico"""
        self.distribuciones[nodo_id] = DistribucionNodo(tipo, parametros)
    
    def configurar_distribucion(self, nodo_id: str, tipo: str, parametros: Dict):
        """Configura la distribución para un nodo específico (alias de configurar_nodo)"""
        self.configurar_nodo(nodo_id, tipo, parametros)
    
    def configurar_desde_dict(self, configuraciones: Dict[str, Dict]):
        """Configura múltiples nodos desde un diccionario de configuraciones"""
        for nodo_id, config in configuraciones.items():
            self.distribuciones[nodo_id] = DistribucionNodo.crear_desde_configuracion(config)
    
    def generar_tiempo_arribo(self, nodo_id: str) -> float:
        """Genera tiempo de arribo para un nodo específico"""
        if nodo_id in self.distribuciones:
            return self.distribuciones[nodo_id].generar_tiempo_arribo()
        else:
            # Distribución por defecto si no está configurada
            return np.random.exponential(2.0)  # 0.5 arribos por segundo
    
    def obtener_distribucion(self, nodo_id: str) -> Optional[DistribucionNodo]:
        """Obtiene la distribución de un nodo específico"""
        return self.distribuciones.get(nodo_id)
    
    def tiene_distribucion(self, nodo_id: str) -> bool:
        """Verifica si un nodo tiene distribución configurada"""
        return nodo_id in self.distribuciones
    
    def obtener_todas_distribuciones(self) -> Dict[str, Dict]:
        """Retorna todas las distribuciones configuradas"""
        resultado = {}
        for nodo_id, distribucion in self.distribuciones.items():
            resultado[nodo_id] = distribucion.to_dict()
        return resultado
    
    def inicializar_por_defecto(self, nodos: List[str]):
        """Inicializa distribuciones por defecto para una lista de nodos"""
        for i, nodo in enumerate(nodos):
            if nodo not in self.distribuciones:
                self.distribuciones[nodo] = DistribucionNodo.crear_por_defecto(nodo, i)
    
    def limpiar(self):
        """Limpia todas las distribuciones"""
        self.distribuciones.clear()
    
    def tiene_distribucion(self, nodo_id: str) -> bool:
        """Verifica si un nodo tiene distribución configurada"""
        return nodo_id in self.distribuciones
    
    def configurar_distribucion(self, nodo_id: str, tipo: str, parametros: Dict):
        """Configura la distribución para un nodo específico (alias para configurar_nodo)"""
        self.configurar_nodo(nodo_id, tipo, parametros)
    
    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas de las distribuciones"""
        tipos = {}
        for distribucion in self.distribuciones.values():
            tipo = distribucion.obtener_tipo()
            tipos[tipo] = tipos.get(tipo, 0) + 1
        
        return {
            'total_nodos': len(self.distribuciones),
            'tipos_distribucion': tipos,
            'nodos_configurados': list(self.distribuciones.keys())
        }
