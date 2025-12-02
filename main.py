#!/usr/bin/env python3
"""
🚴 SIMULADOR DE CICLORUTAS - SISTEMA COMPLETO 🚴

Este es el archivo principal para ejecutar el simulador completo de ciclorutas
con interfaz gráfica y control avanzado.

Desarrollado como herramienta para tesis de pregrado en Ingeniería de Sistemas y Computación
de la Universidad de los Andes, Colombia (2025).

Autor: Sistema de Simulación de Ciclorutas
Versión: 2.0.0 (Refactorizado)
Versión inicial: 1.0.0 (Tesis de Pregrado, Universidad de los Andes, Colombia, 2025)
"""

import sys
import os

def verificar_dependencias():
    """Verifica que todas las dependencias estén instaladas"""
    dependencias = [
        'simpy',
        'matplotlib',
        'numpy',
        'tkinter',
        'pandas',
        'networkx',
        'scipy'
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
        print("   pip install simpy matplotlib numpy pandas networkx scipy")
        print("\n💡 tkinter viene incluido con Python")
        return False
    
    print("✅ Todas las dependencias están instaladas correctamente")
    return True

def mostrar_bienvenida():
    """Muestra mensaje de bienvenida"""
    print("=" * 60)
    print("🚴 SIMULADOR DE CICLORUTAS - SISTEMA COMPLETO v2.0 🚴")
    print("=" * 60)
    print()
    print("🎯 CARACTERÍSTICAS PRINCIPALES:")
    print("   • Simulación en tiempo real de redes de ciclorutas")
    print("   • Interfaz gráfica modular y moderna")
    print("   • Control completo de parámetros de simulación")
    print("   • Visualización en tiempo real con matplotlib")
    print("   • Estadísticas detalladas y actualizadas")
    print("   • Carga de grafos desde archivos Excel")
    print("   • Sistema de distribuciones de probabilidad")
    print("   • Perfiles de ciclistas personalizables")
    print()
    print("🎮 CONTROLES DISPONIBLES:")
    print("   • Configurar velocidades y parámetros de simulación")
    print("   • Cargar redes de ciclorutas desde Excel")
    print("   • Configurar distribuciones de arribo por nodo")
    print("   • Iniciar, pausar, detener y adelantar simulación")
    print("   • Crear nuevas simulaciones con diferentes parámetros")
    print("   • Visualizar estadísticas en tiempo real")
    print()
    print("🔧 PARÁMETROS CONFIGURABLES:")
    print("   • Velocidad mínima: 1.0-20.0 m/s")
    print("   • Velocidad máxima: 1.0-30.0 m/s")
    print("   • Duración de simulación: 60-3600 segundos")
    print("   • Distribuciones de probabilidad por nodo")
    print("   • Perfiles de preferencias de ciclistas")
    print()
    print("📁 FORMATO DE ARCHIVOS EXCEL:")
    print("   • Hoja 'NODOS': Lista de nodos de la red")
    print("   • Hoja 'ARCOS': Conexiones con atributos (distancia, seguridad, etc.)")
    print("   • Hoja 'PERFILES': Perfiles de ciclistas (opcional)")
    print("   • Hoja 'RUTAS': Matriz de probabilidades de destino (opcional)")
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
        # Importar e iniciar la interfaz desde el nuevo paquete
        from Interfaz import InterfazSimulacion
        import tkinter as tk
        
        root = tk.Tk()
        app = InterfazSimulacion(root)
        root.mainloop()
        
    except ImportError as e:
        print(f"❌ ERROR: No se pudo importar la interfaz: {e}")
        print("💡 Asegúrate de que todos los archivos estén en el directorio correcto")
        print("💡 Verifica que las carpetas 'Simulador' e 'Interfaz' estén presentes")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ ERROR inesperado: {e}")
        print("💡 Revisa que todas las dependencias estén correctamente instaladas")
        print("💡 Verifica que la estructura de archivos sea correcta")
        sys.exit(1)

if __name__ == "__main__":
    main()
