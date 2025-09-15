#!/usr/bin/env python3
"""
🚴 EJEMPLO BÁSICO - SIMULADOR DE CICLORUTAS 🚴

Este ejemplo muestra cómo usar el simulador de manera básica
sin interfaz gráfica.

Autor: Sistema de Simulación de Ciclorutas
Versión: 2.0 (Refactorizado)
"""

import sys
import os

# Agregar el directorio raíz al path para importar el paquete
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import SimuladorCiclorutas, crear_simulador_rapido
from src.config import ConfiguracionSimulacion


def ejemplo_basico():
    """Ejemplo básico de uso del simulador."""
    print("🚴 EJEMPLO BÁSICO - SIMULADOR DE CICLORUTAS")
    print("=" * 50)
    
    # Crear simulador con configuración rápida
    simulador = crear_simulador_rapido()
    
    # Crear grafo de ejemplo
    simulador.crear_grafo_ejemplo()
    
    # Inicializar simulación
    simulador.inicializar_simulacion()
    
    print("✅ Simulador inicializado con grafo de ejemplo")
    print(f"📊 Estado: {simulador.obtener_estado_actual()}")
    
    # Ejecutar algunos pasos de simulación
    print("\n🔄 Ejecutando simulación...")
    pasos_ejecutados = 0
    max_pasos = 50
    
    simulador.estado = "ejecutando"
    
    while pasos_ejecutados < max_pasos and simulador.ejecutar_paso():
        pasos_ejecutados += 1
        
        if pasos_ejecutados % 10 == 0:
            estado = simulador.obtener_estado_actual()
            print(f"   Paso {pasos_ejecutados}: Tiempo {estado['tiempo_actual']:.1f}s")
    
    # Obtener estadísticas finales
    print("\n📈 ESTADÍSTICAS FINALES:")
    stats = simulador.obtener_estadisticas()
    
    print(f"   Total ciclistas: {stats['total_ciclistas']}")
    print(f"   Ciclistas activos: {stats['ciclistas_activos']}")
    print(f"   Ciclistas completados: {stats['ciclistas_completados']}")
    print(f"   Velocidad promedio: {stats['velocidad_promedio']:.1f} m/s")
    print(f"   Rutas utilizadas: {stats['rutas_utilizadas']}")
    print(f"   Total viajes: {stats['total_viajes']}")
    
    print("\n✅ Ejemplo completado exitosamente!")


def ejemplo_configuracion_personalizada():
    """Ejemplo con configuración personalizada."""
    print("\n🚴 EJEMPLO CON CONFIGURACIÓN PERSONALIZADA")
    print("=" * 50)
    
    # Crear configuración personalizada
    config = ConfiguracionSimulacion(
        velocidad_min=5.0,
        velocidad_max=25.0,
        duracion_simulacion=120.0,
        max_ciclistas_simultaneos=30
    )
    
    # Crear simulador con configuración personalizada
    simulador = SimuladorCiclorutas(config)
    
    # Crear grafo de ejemplo
    simulador.crear_grafo_ejemplo()
    
    # Configurar distribuciones personalizadas
    distribuciones = {
        'A': {'tipo': 'exponencial', 'parametros': {'lambda': 0.8}},
        'B': {'tipo': 'poisson', 'parametros': {'lambda': 2.0}},
        'C': {'tipo': 'uniforme', 'parametros': {'min': 1.0, 'max': 3.0}},
        'D': {'tipo': 'exponencial', 'parametros': {'lambda': 0.5}},
        'E': {'tipo': 'uniforme', 'parametros': {'min': 0.5, 'max': 2.0}}
    }
    
    simulador.configurar_distribuciones_nodos(distribuciones)
    
    print("✅ Simulador configurado con distribuciones personalizadas")
    print("📊 Distribuciones configuradas:")
    for nodo, dist in simulador.obtener_distribuciones_nodos().items():
        print(f"   {nodo}: {dist['descripcion']}")
    
    # Inicializar y ejecutar simulación
    simulador.inicializar_simulacion()
    simulador.estado = "ejecutando"
    
    print("\n🔄 Ejecutando simulación personalizada...")
    pasos_ejecutados = 0
    max_pasos = 100
    
    while pasos_ejecutados < max_pasos and simulador.ejecutar_paso():
        pasos_ejecutados += 1
        
        if pasos_ejecutados % 20 == 0:
            estado = simulador.obtener_estado_actual()
            print(f"   Paso {pasos_ejecutados}: Tiempo {estado['tiempo_actual']:.1f}s")
    
    # Generar reporte completo
    print("\n📊 REPORTE COMPLETO:")
    reporte = simulador.generar_reporte_completo()
    print(reporte)


if __name__ == "__main__":
    try:
        ejemplo_basico()
        ejemplo_configuracion_personalizada()
    except Exception as e:
        print(f"❌ Error ejecutando ejemplo: {e}")
        import traceback
        traceback.print_exc()
