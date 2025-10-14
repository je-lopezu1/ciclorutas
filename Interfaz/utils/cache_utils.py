"""
Utilidades de cache para optimización de rendimiento.

Este módulo contiene funciones y clases para manejar
el cache de datos de la interfaz y optimizar el rendimiento.
"""

import time
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class CacheEntry:
    """Entrada del cache con timestamp y datos"""
    data: Any
    timestamp: float
    ttl: float  # Time to live en segundos


class CacheManager:
    """Gestor de cache inteligente para la interfaz"""
    
    def __init__(self, default_ttl: float = 0.1):
        self.cache: Dict[str, CacheEntry] = {}
        self.default_ttl = default_ttl
        self.hit_count = 0
        self.miss_count = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del cache si es válido"""
        if key not in self.cache:
            self.miss_count += 1
            return None
        
        entry = self.cache[key]
        current_time = time.time()
        
        # Verificar si la entrada ha expirado
        if current_time - entry.timestamp > entry.ttl:
            del self.cache[key]
            self.miss_count += 1
            return None
        
        self.hit_count += 1
        return entry.data
    
    def set(self, key: str, data: Any, ttl: Optional[float] = None) -> None:
        """Establece un valor en el cache"""
        if ttl is None:
            ttl = self.default_ttl
        
        self.cache[key] = CacheEntry(
            data=data,
            timestamp=time.time(),
            ttl=ttl
        )
    
    def invalidate(self, key: str) -> None:
        """Invalida una entrada específica del cache"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self) -> None:
        """Limpia todo el cache"""
        self.cache.clear()
        self.hit_count = 0
        self.miss_count = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate,
            'cache_size': len(self.cache),
            'total_requests': total_requests
        }
    
    def cleanup_expired(self) -> int:
        """Limpia entradas expiradas del cache"""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.cache.items():
            if current_time - entry.timestamp > entry.ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)


class OptimizedCache:
    """Cache optimizado con múltiples niveles"""
    
    def __init__(self):
        self.interface_cache = CacheManager(default_ttl=0.1)  # 100ms para interfaz
        self.simulation_cache = CacheManager(default_ttl=0.5)  # 500ms para simulación
        self.stats_cache = CacheManager(default_ttl=1.0)  # 1s para estadísticas
    
    def get_interface_data(self, key: str) -> Optional[Any]:
        """Obtiene datos de la interfaz"""
        return self.interface_cache.get(key)
    
    def set_interface_data(self, key: str, data: Any) -> None:
        """Establece datos de la interfaz"""
        self.interface_cache.set(key, data)
    
    def get_simulation_data(self, key: str) -> Optional[Any]:
        """Obtiene datos de la simulación"""
        return self.simulation_cache.get(key)
    
    def set_simulation_data(self, key: str, data: Any) -> None:
        """Establece datos de la simulación"""
        self.simulation_cache.set(key, data)
    
    def get_stats_data(self, key: str) -> Optional[Any]:
        """Obtiene datos de estadísticas"""
        return self.stats_cache.get(key)
    
    def set_stats_data(self, key: str, data: Any) -> None:
        """Establece datos de estadísticas"""
        self.stats_cache.set(key, data)
    
    def clear_all(self) -> None:
        """Limpia todos los caches"""
        self.interface_cache.clear()
        self.simulation_cache.clear()
        self.stats_cache.clear()
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de todos los caches"""
        return {
            'interface': self.interface_cache.get_stats(),
            'simulation': self.simulation_cache.get_stats(),
            'stats': self.stats_cache.get_stats()
        }
    
    def cleanup_all(self) -> Dict[str, int]:
        """Limpia entradas expiradas de todos los caches"""
        return {
            'interface': self.interface_cache.cleanup_expired(),
            'simulation': self.simulation_cache.cleanup_expired(),
            'stats': self.stats_cache.cleanup_expired()
        }


def cache_result(ttl: float = 0.1):
    """Decorador para cachear resultados de funciones"""
    def decorator(func: Callable) -> Callable:
        cache = CacheManager(default_ttl=ttl)
        
        def wrapper(*args, **kwargs):
            # Crear clave única basada en argumentos
            key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
            
            # Intentar obtener del cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
        
        return wrapper
    return decorator


def memoize_with_ttl(ttl: float = 0.1):
    """Decorador para memoización con TTL"""
    def decorator(func: Callable) -> Callable:
        cache = {}
        
        def wrapper(*args, **kwargs):
            current_time = time.time()
            key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
            
            # Verificar si existe y no ha expirado
            if key in cache:
                result, timestamp = cache[key]
                if current_time - timestamp < ttl:
                    return result
                else:
                    del cache[key]
            
            # Ejecutar función y cachear
            result = func(*args, **kwargs)
            cache[key] = (result, current_time)
            return result
        
        return wrapper
    return decorator
