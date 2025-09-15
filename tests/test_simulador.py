#!/usr/bin/env python3
"""
🧪 ARCHIVO DE PRUEBA DEL SIMULADOR DE CICLORUTAS 🧪

Este archivo prueba que todos los componentes funcionen correctamente
sin errores de compatibilidad.
"""

import sys
import traceback
import os

# Agregar el directorio raíz al path para importar el paquete
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Prueba que todas las importaciones funcionen"""
    print("🔍 Probando importaciones...")
    
    try:
        import simpy
        print("✅ SimPy importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando SimPy: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando NumPy: {e}")
        return False
    
    try:
        import matplotlib.pyplot as plt
        print("✅ Matplotlib importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando Matplotlib: {e}")
        return False
    
    try:
        import tkinter as tk
        print("✅ Tkinter importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando Tkinter: {e}")
        return False
    
    return True

def test_simulacion():
    """Prueba que la simulación funcione"""
    print("\n🔍 Probando módulo de simulación...")
    
    try:
        from src.core import SimuladorCiclorutas
        from src.config import ConfiguracionSimulacion
        print("✅ Módulo de simulación importado correctamente")
        
        # Crear configuración
        config = ConfiguracionSimulacion()
        print("✅ Configuración creada correctamente")
        
        # Crear simulador
        simulador = SimuladorCiclorutas(config)
        print("✅ Simulador creado correctamente")
        
        # Inicializar simulación
        simulador.inicializar_simulacion()
        print("✅ Simulación inicializada correctamente")
        
        # Obtener estadísticas
        stats = simulador.obtener_estadisticas()
        print(f"✅ Estadísticas obtenidas: {stats['total_ciclistas']} ciclistas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en simulación: {e}")
        traceback.print_exc()
        return False

def test_visualizacion():
    """Prueba que la visualización funcione"""
    print("\n🔍 Probando visualización...")
    
    try:
        import matplotlib.pyplot as plt
        
        # Crear figura simple
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Dibujar línea simple
        ax.plot([0, 10], [0, 10], 'b-', linewidth=2, label='Línea de prueba')
        
        # Configurar gráfico
        ax.set_title("Prueba de Visualizacion")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.legend()
        ax.grid(True)
        
        print("✅ Visualización creada correctamente")
        
        # Cerrar figura para liberar memoria
        plt.close(fig)
        
        return True
        
    except Exception as e:
        print(f"❌ Error en visualización: {e}")
        traceback.print_exc()
        return False

def main():
    """Función principal de pruebas"""
    print("=" * 60)
    print("🧪 PRUEBAS DEL SIMULADOR DE CICLORUTAS 🧪")
    print("=" * 60)
    
    # Ejecutar pruebas
    tests = [
        ("Importaciones", test_imports),
        ("Simulación", test_simulacion),
        ("Visualización", test_visualizacion)
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        print(f"\n📋 Ejecutando prueba: {nombre}")
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error inesperado en {nombre}: {e}")
            resultados.append((nombre, False))
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    exitos = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    for nombre, resultado in resultados:
        estado = "✅ EXITOSA" if resultado else "❌ FALLIDA"
        print(f"{nombre}: {estado}")
    
    print(f"\n🎯 Resultado: {exitos}/{total} pruebas exitosas")
    
    if exitos == total:
        print("🎉 ¡Todas las pruebas pasaron! El simulador está listo para usar.")
        print("💡 Ejecuta 'python main.py' para iniciar la interfaz completa.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        print("💡 Asegúrate de tener todas las dependencias instaladas:")
        print("   pip install -r requirements.txt")
    
    return exitos == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
