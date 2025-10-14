"""
Modelo de ciclista para la simulación.

Este módulo contiene las clases relacionadas con los ciclistas:
- Ciclista: Entidad individual
- PoolCiclistas: Gestión optimizada de memoria
"""

import time
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class Ciclista:
    """Clase optimizada para ciclistas con gestión de memoria"""
    
    def __init__(self, id: int):
        self.id = id
        self.coordenadas = (-1000, -1000)
        self.trayectoria = []
        self.velocidad = 0
        self.estado = 'inactivo'
        self.ruta = ""
        self.color = '#6C757D'
        self.tiempo_creacion = time.time()
        self.tiempo_ultima_actividad = time.time()
        
        # Límites de memoria por ciclista
        self.max_trayectoria_puntos = 50
        self.max_tiempo_inactivo = 300  # 5 minutos
    
    def reset(self):
        """Resetea el ciclista para reutilización"""
        self.coordenadas = (-1000, -1000)
        self.trayectoria = []
        self.velocidad = 0
        self.estado = 'inactivo'
        self.ruta = ""
        self.color = '#6C757D'
        self.tiempo_creacion = time.time()
        self.tiempo_ultima_actividad = time.time()
    
    def actualizar_posicion(self, x: float, y: float):
        """Actualiza la posición del ciclista"""
        self.coordenadas = (x, y)
        self.tiempo_ultima_actividad = time.time()
        
        # Limitar trayectoria para evitar uso excesivo de memoria
        if len(self.trayectoria) >= self.max_trayectoria_puntos:
            self.trayectoria = self.trayectoria[-self.max_trayectoria_puntos//2:]
        
        self.trayectoria.append((x, y))
    
    def es_antiguo(self) -> bool:
        """Verifica si el ciclista es muy antiguo"""
        return time.time() - self.tiempo_ultima_actividad > self.max_tiempo_inactivo
    
    def completar_viaje(self):
        """Marca el ciclista como completado"""
        self.estado = 'completado'
        self.coordenadas = (-1000, -1000)  # Posición invisible
    
    def obtener_estado(self) -> Dict:
        """Retorna el estado actual del ciclista"""
        return {
            'id': self.id,
            'coordenadas': self.coordenadas,
            'velocidad': self.velocidad,
            'estado': self.estado,
            'ruta': self.ruta,
            'color': self.color,
            'tiempo_creacion': self.tiempo_creacion,
            'tiempo_ultima_actividad': self.tiempo_ultima_actividad,
            'puntos_trayectoria': len(self.trayectoria)
        }


class PoolCiclistas:
    """Pool inteligente de ciclistas para reutilización"""
    
    def __init__(self, tamaño_inicial: int = 100, tamaño_maximo: int = 1000):
        self.tamaño_inicial = tamaño_inicial
        self.tamaño_maximo = tamaño_maximo
        self.ciclistas_disponibles = []
        self.ciclistas_activos = {}
        self.contador_id = 0
        self.estadisticas = {
            'creados': 0,
            'reutilizados': 0,
            'liberados': 0,
            'eliminados': 0
        }
        
        # Crear pool inicial
        self._inicializar_pool()
    
    def _inicializar_pool(self):
        """Inicializa el pool con ciclistas pre-creados"""
        for _ in range(self.tamaño_inicial):
            ciclista = Ciclista(self.contador_id)
            self.ciclistas_disponibles.append(ciclista)
            self.contador_id += 1
            self.estadisticas['creados'] += 1
    
    def obtener_ciclista(self) -> Optional[Ciclista]:
        """Obtiene un ciclista del pool o crea uno nuevo"""
        if self.ciclistas_disponibles:
            # Reutilizar ciclista existente
            ciclista = self.ciclistas_disponibles.pop()
            ciclista.reset()
            self.ciclistas_activos[ciclista.id] = ciclista
            self.estadisticas['reutilizados'] += 1
            return ciclista
        else:
            # Crear nuevo ciclista si el pool está vacío
            if len(self.ciclistas_activos) < self.tamaño_maximo:
                ciclista = Ciclista(self.contador_id)
                self.contador_id += 1
                self.ciclistas_activos[ciclista.id] = ciclista
                self.estadisticas['creados'] += 1
                return ciclista
            else:
                # Pool lleno, reutilizar el más antiguo
                return self._reutilizar_mas_antiguo()
    
    def _reutilizar_mas_antiguo(self) -> Optional[Ciclista]:
        """Reutiliza el ciclista más antiguo cuando el pool está lleno"""
        if not self.ciclistas_activos:
            return None
        
        # Encontrar el ciclista más antiguo
        id_mas_antiguo = min(self.ciclistas_activos.keys())
        ciclista = self.ciclistas_activos[id_mas_antiguo]
        
        # Resetear y reutilizar
        ciclista.reset()
        self.estadisticas['reutilizados'] += 1
        return ciclista
    
    def liberar_ciclista(self, ciclista: Ciclista):
        """Libera un ciclista al pool"""
        if ciclista.id in self.ciclistas_activos:
            del self.ciclistas_activos[ciclista.id]
            
            if len(self.ciclistas_disponibles) < self.tamaño_inicial:
                # Mantener pool mínimo
                self.ciclistas_disponibles.append(ciclista)
                self.estadisticas['liberados'] += 1
            else:
                # Pool lleno, eliminar ciclista
                del ciclista
                self.estadisticas['eliminados'] += 1
    
    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas del pool"""
        return {
            'ciclistas_activos': len(self.ciclistas_activos),
            'ciclistas_disponibles': len(self.ciclistas_disponibles),
            'total_creados': self.estadisticas['creados'],
            'total_reutilizados': self.estadisticas['reutilizados'],
            'total_liberados': self.estadisticas['liberados'],
            'total_eliminados': self.estadisticas['eliminados'],
            'eficiencia': self.estadisticas['reutilizados'] / max(1, self.estadisticas['creados'])
        }
    
    def limpiar_ciclistas_antiguos(self):
        """Limpia ciclistas que han estado inactivos por mucho tiempo"""
        ciclistas_a_limpiar = []
        
        for ciclista in self.ciclistas_activos.values():
            if ciclista.es_antiguo():
                ciclistas_a_limpiar.append(ciclista.id)
        
        for ciclista_id in ciclistas_a_limpiar:
            if ciclista_id in self.ciclistas_activos:
                ciclista = self.ciclistas_activos[ciclista_id]
                self.liberar_ciclista(ciclista)
        
        return len(ciclistas_a_limpiar)
    
    def reiniciar_pool(self):
        """Reinicia el pool completamente"""
        # Limpiar todos los ciclistas
        self.ciclistas_disponibles.clear()
        self.ciclistas_activos.clear()
        
        # Resetear contador y estadísticas
        self.contador_id = 0
        self.estadisticas = {
            'creados': 0,
            'reutilizados': 0,
            'liberados': 0,
            'eliminados': 0
        }
        
        # Reinicializar pool
        self._inicializar_pool()
