#!/usr/bin/env python3
"""
🔍 MÓDULO DE VALIDADORES - SIMULADOR DE CICLORUTAS 🔍

Este módulo contiene funciones de validación comunes utilizadas
en todo el sistema de simulación.

Autor: Sistema de Simulación de Ciclorutas
Versión: 2.0 (Refactorizado)
"""

from typing import Any, List, Tuple, Dict, Optional
import numpy as np


class ValidadorNumerico:
    """Clase para validaciones numéricas."""
    
    @staticmethod
    def validar_rango(valor: float, min_val: float, max_val: float, nombre: str = "valor") -> Tuple[bool, str]:
        """
        Valida que un valor esté dentro de un rango específico.
        
        Args:
            valor: Valor a validar
            min_val: Valor mínimo permitido
            max_val: Valor máximo permitido
            nombre: Nombre del parámetro para mensajes de error
            
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        if not isinstance(valor, (int, float)):
            return False, f"{nombre} debe ser un número"
        
        if valor < min_val:
            return False, f"{nombre} debe ser mayor o igual a {min_val}"
        
        if valor > max_val:
            return False, f"{nombre} debe ser menor o igual a {max_val}"
        
        return True, ""
    
    @staticmethod
    def validar_positivo(valor: float, nombre: str = "valor") -> Tuple[bool, str]:
        """
        Valida que un valor sea positivo.
        
        Args:
            valor: Valor a validar
            nombre: Nombre del parámetro para mensajes de error
            
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        if not isinstance(valor, (int, float)):
            return False, f"{nombre} debe ser un número"
        
        if valor <= 0:
            return False, f"{nombre} debe ser mayor que 0"
        
        return True, ""
    
    @staticmethod
    def validar_no_negativo(valor: float, nombre: str = "valor") -> Tuple[bool, str]:
        """
        Valida que un valor sea no negativo.
        
        Args:
            valor: Valor a validar
            nombre: Nombre del parámetro para mensajes de error
            
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        if not isinstance(valor, (int, float)):
            return False, f"{nombre} debe ser un número"
        
        if valor < 0:
            return False, f"{nombre} debe ser mayor o igual a 0"
        
        return True, ""


class ValidadorTexto:
    """Clase para validaciones de texto."""
    
    @staticmethod
    def validar_no_vacio(texto: str, nombre: str = "texto") -> Tuple[bool, str]:
        """
        Valida que un texto no esté vacío.
        
        Args:
            texto: Texto a validar
            nombre: Nombre del parámetro para mensajes de error
            
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        if not isinstance(texto, str):
            return False, f"{nombre} debe ser una cadena de texto"
        
        if not texto.strip():
            return False, f"{nombre} no puede estar vacío"
        
        return True, ""
    
    @staticmethod
    def validar_longitud(texto: str, min_longitud: int, max_longitud: int, 
                        nombre: str = "texto") -> Tuple[bool, str]:
        """
        Valida la longitud de un texto.
        
        Args:
            texto: Texto a validar
            min_longitud: Longitud mínima
            max_longitud: Longitud máxima
            nombre: Nombre del parámetro para mensajes de error
            
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        if not isinstance(texto, str):
            return False, f"{nombre} debe ser una cadena de texto"
        
        longitud = len(texto)
        if longitud < min_longitud:
            return False, f"{nombre} debe tener al menos {min_longitud} caracteres"
        
        if longitud > max_longitud:
            return False, f"{nombre} debe tener máximo {max_longitud} caracteres"
        
        return True, ""


class ValidadorLista:
    """Clase para validaciones de listas."""
    
    @staticmethod
    def validar_no_vacia(lista: List[Any], nombre: str = "lista") -> Tuple[bool, str]:
        """
        Valida que una lista no esté vacía.
        
        Args:
            lista: Lista a validar
            nombre: Nombre del parámetro para mensajes de error
            
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        if not isinstance(lista, list):
            return False, f"{nombre} debe ser una lista"
        
        if len(lista) == 0:
            return False, f"{nombre} no puede estar vacía"
        
        return True, ""
    
    @staticmethod
    def validar_longitud_minima(lista: List[Any], min_longitud: int, 
                               nombre: str = "lista") -> Tuple[bool, str]:
        """
        Valida que una lista tenga una longitud mínima.
        
        Args:
            lista: Lista a validar
            min_longitud: Longitud mínima requerida
            nombre: Nombre del parámetro para mensajes de error
            
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        if not isinstance(lista, list):
            return False, f"{nombre} debe ser una lista"
        
        if len(lista) < min_longitud:
            return False, f"{nombre} debe tener al menos {min_longitud} elementos"
        
        return True, ""


class ValidadorCoordenadas:
    """Clase para validaciones de coordenadas."""
    
    @staticmethod
    def validar_coordenada(coordenada: Tuple[float, float], nombre: str = "coordenada") -> Tuple[bool, str]:
        """
        Valida que una coordenada sea válida.
        
        Args:
            coordenada: Coordenada a validar (x, y)
            nombre: Nombre del parámetro para mensajes de error
            
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        if not isinstance(coordenada, (tuple, list)):
            return False, f"{nombre} debe ser una tupla o lista"
        
        if len(coordenada) != 2:
            return False, f"{nombre} debe tener exactamente 2 elementos (x, y)"
        
        x, y = coordenada
        
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            return False, f"Los elementos de {nombre} deben ser números"
        
        if not np.isfinite(x) or not np.isfinite(y):
            return False, f"Los elementos de {nombre} deben ser números finitos"
        
        return True, ""
    
    @staticmethod
    def validar_coordenadas_multiples(coordenadas: Dict[str, Tuple[float, float]], 
                                    nombre: str = "coordenadas") -> Tuple[bool, List[str]]:
        """
        Valida múltiples coordenadas.
        
        Args:
            coordenadas: Diccionario de coordenadas
            nombre: Nombre del parámetro para mensajes de error
            
        Returns:
            Tuple[bool, List[str]]: (es_valido, lista_errores)
        """
        errores = []
        
        if not isinstance(coordenadas, dict):
            errores.append(f"{nombre} debe ser un diccionario")
            return False, errores
        
        for key, coord in coordenadas.items():
            es_valido, mensaje = ValidadorCoordenadas.validar_coordenada(coord, f"{nombre}[{key}]")
            if not es_valido:
                errores.append(mensaje)
        
        return len(errores) == 0, errores


class ValidadorConfiguracion:
    """Clase para validaciones de configuración."""
    
    @staticmethod
    def validar_configuracion_simulacion(config: Any) -> Tuple[bool, List[str]]:
        """
        Valida una configuración de simulación.
        
        Args:
            config: Configuración a validar
            
        Returns:
            Tuple[bool, List[str]]: (es_valido, lista_errores)
        """
        errores = []
        
        # Validar velocidad mínima
        if hasattr(config, 'velocidad_min'):
            es_valido, mensaje = ValidadorNumerico.validar_positivo(
                config.velocidad_min, "velocidad_min"
            )
            if not es_valido:
                errores.append(mensaje)
        
        # Validar velocidad máxima
        if hasattr(config, 'velocidad_max'):
            es_valido, mensaje = ValidadorNumerico.validar_positivo(
                config.velocidad_max, "velocidad_max"
            )
            if not es_valido:
                errores.append(mensaje)
        
        # Validar que velocidad_min < velocidad_max
        if (hasattr(config, 'velocidad_min') and hasattr(config, 'velocidad_max') and
            config.velocidad_min >= config.velocidad_max):
            errores.append("velocidad_min debe ser menor que velocidad_max")
        
        # Validar duración de simulación
        if hasattr(config, 'duracion_simulacion'):
            es_valido, mensaje = ValidadorNumerico.validar_positivo(
                config.duracion_simulacion, "duracion_simulacion"
            )
            if not es_valido:
                errores.append(mensaje)
        
        # Validar máximo de ciclistas
        if hasattr(config, 'max_ciclistas_simultaneos'):
            es_valido, mensaje = ValidadorNumerico.validar_positivo(
                config.max_ciclistas_simultaneos, "max_ciclistas_simultaneos"
            )
            if not es_valido:
                errores.append(mensaje)
        
        return len(errores) == 0, errores


class ValidadorGeneral:
    """Clase que agrupa todas las validaciones."""
    
    def __init__(self):
        """Inicializa el validador general."""
        self.numerico = ValidadorNumerico()
        self.texto = ValidadorTexto()
        self.lista = ValidadorLista()
        self.coordenadas = ValidadorCoordenadas()
        self.configuracion = ValidadorConfiguracion()
    
    def validar_todo(self, config: Any) -> Tuple[bool, List[str]]:
        """
        Valida toda la configuración.
        
        Args:
            config: Configuración a validar
            
        Returns:
            Tuple[bool, List[str]]: (es_valido, lista_errores)
        """
        return self.configuracion.validar_configuracion_simulacion(config)
    
    def __str__(self) -> str:
        """Representación string del validador."""
        return "ValidadorGeneral(validaciones_completas)"


# Instancia global del validador
validador = ValidadorGeneral()
