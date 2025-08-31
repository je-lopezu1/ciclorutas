#!/usr/bin/env python3
"""
🚴 SIMULADOR DE CICLORUTAS - SISTEMA COMPLETO 🚴

Este es el archivo principal para ejecutar el simulador completo de ciclorutas
con interfaz gráfica y control avanzado.

Autor: Sistema de Simulación de Ciclorutas
Versión: 1.0
"""

import sys
import os

def verificar_dependencias():
    """Verifica que todas las dependencias estén instaladas"""
    dependencias = [
        'simpy',
        'matplotlib',
        'numpy',
        'tkinter'
    ]
    
    faltantes = []
    
    for dep in dependencias:
        try:
            if dep == 'tkinter':
                import tkinter
            else:
                __import__(dep)
        except ImportError:
            faltantes.append(dep)
    
    if faltantes:
        print("❌ ERROR: Faltan las siguientes dependencias:")
        for dep in faltantes:
            print(f"   - {dep}")
        print("\n📦 Para instalar las dependencias, ejecuta:")
        print("   pip install simpy matplotlib numpy")
        print("\n💡 tkinter viene incluido con Python")
        return False
    
    print("✅ Todas las dependencias están instaladas correctamente")
    return True

def mostrar_bienvenida():
    """Muestra mensaje de bienvenida"""
    print("=" * 60)
    print("🚴 SIMULADOR DE CICLORUTAS - SISTEMA COMPLETO 🚴")
    print("=" * 60)
    print()
    print("🎯 CARACTERÍSTICAS PRINCIPALES:")
    print("   • Simulación en tiempo real de ciclorutas en forma de Y")
    print("   • Interfaz gráfica intuitiva y moderna")
    print("   • Control completo de parámetros de simulación")
    print("   • Visualización en tiempo real con matplotlib")
    print("   • Estadísticas detalladas y actualizadas")
    print()
    print("🎮 CONTROLES DISPONIBLES:")
    print("   • Configurar número de ciclistas, velocidades y distancias")
    print("   • Iniciar, pausar, detener y adelantar simulación")
    print("   • Crear nuevas simulaciones con diferentes parámetros")
    print("   • Visualizar estadísticas en tiempo real")
    print()
    print("🔧 PARÁMETROS CONFIGURABLES:")
    print("   • Número de ciclistas: 5-100")
    print("   • Velocidad mínima: 1.0-20.0 m/s")
    print("   • Velocidad máxima: 1.0-30.0 m/s")
    print("   • Distancia A: 20.0-100.0 m")
    print("   • Distancia B: 15.0-80.0 m")
    print("   • Distancia C: 15.0-80.0 m")
    print()

def main():
    """Función principal del sistema"""
    print("🔍 Verificando dependencias...")
    
    if not verificar_dependencias():
        print("\n❌ No se pueden ejecutar las dependencias. Saliendo...")
        sys.exit(1)
    
    mostrar_bienvenida()
    
    print("🚀 Iniciando interfaz gráfica...")
    print("💡 La ventana se abrirá en unos segundos...")
    print()
    
    try:
        # Importar e iniciar la interfaz
        from interfaz_simulacion import main as iniciar_interfaz
        iniciar_interfaz()
        
    except ImportError as e:
        print(f"❌ ERROR: No se pudo importar la interfaz: {e}")
        print("💡 Asegúrate de que todos los archivos estén en el mismo directorio")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ ERROR inesperado: {e}")
        print("💡 Revisa que todas las dependencias estén correctamente instaladas")
        sys.exit(1)

if __name__ == "__main__":
    main()
