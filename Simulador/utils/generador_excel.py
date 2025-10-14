"""
Generador de archivos Excel para resultados de simulación.

Este módulo contiene la funcionalidad para exportar los resultados
de la simulación a archivos Excel con múltiples hojas.
"""

import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import networkx as nx


class GeneradorExcel:
    """Clase para generar archivos Excel con resultados de simulación"""
    
    def __init__(self, carpeta_resultados: str = "resultados"):
        self.carpeta_resultados = carpeta_resultados
        self.asegurar_carpeta_existe()
    
    def asegurar_carpeta_existe(self):
        """Asegura que la carpeta de resultados existe"""
        if not os.path.exists(self.carpeta_resultados):
            os.makedirs(self.carpeta_resultados)
    
    def generar_archivo_resultados(self, simulador, nombre_grafo: str = "simulacion") -> str:
        """
        Genera un archivo Excel completo con los resultados de la simulación
        
        Args:
            simulador: Instancia del simulador con todos los datos
            nombre_grafo: Nombre del grafo para el archivo
            
        Returns:
            str: Ruta del archivo generado
        """
        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"{nombre_grafo}_{timestamp}.xlsx"
        ruta_archivo = os.path.join(self.carpeta_resultados, nombre_archivo)
        
        # Crear el archivo Excel con múltiples hojas
        with pd.ExcelWriter(ruta_archivo, engine='openpyxl') as writer:
            
            # Hoja 1: Información General de la Simulación
            self._crear_hoja_info_simulacion(simulador, writer)
            
            # Hoja 2: Tramos
            self._crear_hoja_tramos(simulador, writer)
            
            # Hoja 3: Ciclistas
            self._crear_hoja_ciclistas(simulador, writer)
        
        print(f"✅ Archivo Excel generado: {ruta_archivo}")
        return ruta_archivo
    
    def _crear_hoja_info_simulacion(self, simulador, writer):
        """Crea la hoja con información general de la simulación"""
        
        # Obtener estadísticas completas
        from ..utils.estadisticas_utils import EstadisticasUtils
        stats = EstadisticasUtils.calcular_estadisticas_completas(simulador)
        
        # Preparar datos para la hoja
        datos_info = []
        
        # Información básica
        datos_info.append(["INFORMACIÓN GENERAL", ""])
        datos_info.append(["Fecha de simulación", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        datos_info.append(["Duración de simulación", f"{simulador.config.duracion_simulacion} segundos"])
        datos_info.append(["Estado final", simulador.estado])
        datos_info.append(["Tiempo transcurrido", f"{simulador.tiempo_actual:.2f} segundos"])
        datos_info.append(["", ""])
        
        # Información del grafo
        datos_info.append(["INFORMACIÓN DEL GRAFO", ""])
        if simulador.usar_grafo_real and simulador.grafo:
            datos_info.append(["Usando grafo real", "Sí"])
            datos_info.append(["Número de nodos", stats.get('grafo_nodos', 0)])
            datos_info.append(["Número de arcos", stats.get('grafo_arcos', 0)])
            datos_info.append(["Grafo conectado", "Sí" if stats.get('grafo_conectado', False) else "No"])
            datos_info.append(["Distancia promedio arcos", f"{stats.get('distancia_promedio_arcos', 0):.2f} metros"])
        else:
            datos_info.append(["Usando grafo real", "No"])
        datos_info.append(["", ""])
        
        # Estadísticas de ciclistas
        datos_info.append(["ESTADÍSTICAS DE CICLISTAS", ""])
        datos_info.append(["Total de ciclistas creados", stats.get('total_ciclistas', 0)])
        datos_info.append(["Ciclistas activos", stats.get('ciclistas_activos', 0)])
        datos_info.append(["Ciclistas completados", stats.get('ciclistas_completados', 0)])
        datos_info.append(["Velocidad promedio", f"{stats.get('velocidad_promedio', 0):.2f} km/h"])
        datos_info.append(["Velocidad mínima", f"{stats.get('velocidad_minima', 0):.2f} km/h"])
        datos_info.append(["Velocidad máxima", f"{stats.get('velocidad_maxima', 0):.2f} km/h"])
        datos_info.append(["", ""])
        
        # Estadísticas de rutas
        datos_info.append(["ESTADÍSTICAS DE RUTAS", ""])
        datos_info.append(["Rutas únicas utilizadas", stats.get('rutas_utilizadas', 0)])
        datos_info.append(["Total de viajes", stats.get('total_viajes', 0)])
        
        ruta_mas_usada = stats.get('ruta_mas_usada', 'Sin datos')
        if ruta_mas_usada != 'N/A':
            datos_info.append(["Ruta más usada", ruta_mas_usada])
        else:
            datos_info.append(["Ruta más usada", "Sin datos"])
        
        tramo_mas_concurrido = stats.get('tramo_mas_concurrido', 'Sin datos')
        if tramo_mas_concurrido != 'N/A':
            datos_info.append(["Tramo más concurrido", tramo_mas_concurrido])
        else:
            datos_info.append(["Tramo más concurrido", "Sin datos"])
        
        datos_info.append(["", ""])
        
        # Estadísticas de nodos
        datos_info.append(["ESTADÍSTICAS DE NODOS", ""])
        nodo_mas_activo = stats.get('nodo_mas_activo', 'Sin datos')
        if nodo_mas_activo != 'N/A':
            datos_info.append(["Nodo más activo", nodo_mas_activo])
        else:
            datos_info.append(["Nodo más activo", "Sin datos"])
        datos_info.append(["", ""])
        
        # Estadísticas de perfiles
        datos_info.append(["ESTADÍSTICAS DE PERFILES", ""])
        datos_info.append(["Total ciclistas con perfil", stats.get('total_ciclistas_con_perfil', 0)])
        
        perfil_mas_usado = stats.get('perfil_mas_usado', 'Sin datos')
        if perfil_mas_usado != 'N/A':
            datos_info.append(["Perfil más usado", perfil_mas_usado])
        else:
            datos_info.append(["Perfil más usado", "Sin datos"])
        
        # Crear DataFrame y escribir a Excel
        df_info = pd.DataFrame(datos_info, columns=['Parámetro', 'Valor'])
        df_info.to_excel(writer, sheet_name='Info Simulación', index=False)
        
        # Ajustar ancho de columnas
        worksheet = writer.sheets['Info Simulación']
        worksheet.column_dimensions['A'].width = 30
        worksheet.column_dimensions['B'].width = 50
    
    def _crear_hoja_tramos(self, simulador, writer):
        """Crea la hoja con información detallada de los tramos"""
        
        datos_tramos = []
        
        if simulador.usar_grafo_real and simulador.grafo:
            # Obtener atributos reales disponibles en el grafo
            atributos_reales = self._obtener_atributos_reales(simulador.grafo)
            
            # Obtener información de todos los arcos del grafo
            for origen, destino, atributos in simulador.grafo.edges(data=True):
                # Información básica del tramo
                tramo_id = f"{origen}->{destino}"
                uso_count = simulador.arcos_utilizados.get(tramo_id, 0)
                
                # Características básicas del tramo
                distancia = atributos.get('distancia', atributos.get('distancia_real', 0))
                peso = atributos.get('weight', 0)
                
                # Calcular estadísticas de uso
                total_uso = sum(simulador.arcos_utilizados.values())
                porcentaje_uso = (uso_count / max(1, total_uso)) * 100 if total_uso > 0 else 0
                
                # Determinar momento más ocupado y más vacío (simplificado)
                momento_ocupado = "Pico de uso" if uso_count > 0 else "Sin uso"
                momento_vacio = "Sin uso" if uso_count == 0 else "Uso moderado"
                
                # Crear fila con datos básicos
                fila = [
                    tramo_id,
                    origen,
                    destino,
                    distancia,
                    peso,
                    uso_count,
                    f"{porcentaje_uso:.1f}%",
                    momento_ocupado,
                    momento_vacio
                ]
                
                # Agregar solo los atributos reales que existen
                for attr in atributos_reales:
                    valor = atributos.get(attr, 'N/A')
                    fila.append(valor)
                
                datos_tramos.append(fila)
        
        # Crear columnas dinámicamente
        columnas = [
            'ID Tramo', 'Nodo Origen', 'Nodo Destino', 'Distancia (m)', 'Peso',
            'Ciclistas que lo usaron', 'Porcentaje de uso', 'Momento más ocupado', 'Momento más vacío'
        ]
        
        # Agregar columnas de atributos reales
        if simulador.usar_grafo_real and simulador.grafo:
            atributos_reales = self._obtener_atributos_reales(simulador.grafo)
            for attr in atributos_reales:
                columnas.append(attr.title())
        
        df_tramos = pd.DataFrame(datos_tramos, columns=columnas)
        
        # Ordenar por uso (más usado primero)
        df_tramos = df_tramos.sort_values('Ciclistas que lo usaron', ascending=False)
        
        # Escribir a Excel
        df_tramos.to_excel(writer, sheet_name='Tramos', index=False)
        
        # Ajustar ancho de columnas
        worksheet = writer.sheets['Tramos']
        for col in worksheet.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 20)
            worksheet.column_dimensions[column].width = adjusted_width
    
    def _crear_hoja_ciclistas(self, simulador, writer):
        """Crea la hoja con información detallada de los ciclistas"""
        
        datos_ciclistas = []
        
        # Procesar información de cada ciclista
        for ciclista_id, ruta_info in simulador.rutas_por_ciclista.items():
            # Información básica del ciclista
            origen = ruta_info.get('origen', 'N/A')
            destino = ruta_info.get('destino', 'N/A')
            ruta_detallada = ruta_info.get('ruta_detallada', 'N/A')
            ruta_simple = ruta_info.get('ruta_simple', 'N/A')
            
            # Obtener perfil del ciclista
            perfil = simulador.perfiles_ciclistas.get(ciclista_id, 'Sin perfil')
            
            # Obtener arcos utilizados por este ciclista
            arcos_ciclista = simulador.arcos_por_ciclista.get(ciclista_id, [])
            num_tramos = len(arcos_ciclista)
            tramos_utilizados = "; ".join(arcos_ciclista) if arcos_ciclista else "N/A"
            
            # Calcular distancia total (aproximada)
            distancia_total = 0
            if simulador.usar_grafo_real and simulador.grafo:
                for arco in arcos_ciclista:
                    if "->" in arco:
                        nodo_origen, nodo_destino = arco.split("->")
                        if simulador.grafo.has_edge(nodo_origen, nodo_destino):
                            dist = simulador.grafo[nodo_origen][nodo_destino].get('distancia_real', 
                                                                                   simulador.grafo[nodo_origen][nodo_destino].get('distancia', 0))
                            distancia_total += dist
            
            # Estado del ciclista
            estado = simulador.estado_ciclistas.get(ciclista_id, 'Desconocido')
            
            # Crear fila básica
            fila = [
                ciclista_id,
                origen,
                destino,
                ruta_simple,
                ruta_detallada,
                perfil if isinstance(perfil, str) else f"Perfil {perfil}",
                num_tramos,
                f"{distancia_total:.1f}",
                tramos_utilizados,
                estado
            ]
            
            # Agregar preferencias del perfil solo si están disponibles
            if isinstance(perfil, dict):
                # Obtener atributos reales disponibles en el grafo
                if simulador.usar_grafo_real and simulador.grafo:
                    atributos_reales = self._obtener_atributos_reales(simulador.grafo)
                    for attr in atributos_reales:
                        preferencia = perfil.get(attr, 'N/A')
                        fila.append(preferencia)
                else:
                    # Si no hay grafo, usar atributos por defecto
                    for attr in ['seguridad', 'luminosidad', 'inclinacion']:
                        preferencia = perfil.get(attr, 'N/A')
                        fila.append(preferencia)
            else:
                # Si no hay perfil, agregar N/A para todos los atributos
                if simulador.usar_grafo_real and simulador.grafo:
                    atributos_reales = self._obtener_atributos_reales(simulador.grafo)
                    for _ in atributos_reales:
                        fila.append('N/A')
                else:
                    for _ in ['seguridad', 'luminosidad', 'inclinacion']:
                        fila.append('N/A')
            
            datos_ciclistas.append(fila)
        
        # Crear columnas dinámicamente
        columnas = [
            'ID Ciclista', 'Origen', 'Destino', 'Ruta Simple', 'Ruta Detallada',
            'Perfil', 'Número de Tramos', 'Distancia Total (m)', 'Tramos Utilizados', 'Estado'
        ]
        
        # Agregar columnas de preferencias solo para atributos reales
        if simulador.usar_grafo_real and simulador.grafo:
            atributos_reales = self._obtener_atributos_reales(simulador.grafo)
            for attr in atributos_reales:
                columnas.append(f'Pref. {attr.title()}')
        else:
            # Atributos por defecto si no hay grafo
            for attr in ['seguridad', 'luminosidad', 'inclinacion']:
                columnas.append(f'Pref. {attr.title()}')
        
        df_ciclistas = pd.DataFrame(datos_ciclistas, columns=columnas)
        
        # Ordenar por ID de ciclista
        df_ciclistas = df_ciclistas.sort_values('ID Ciclista')
        
        # Escribir a Excel
        df_ciclistas.to_excel(writer, sheet_name='Ciclistas', index=False)
        
        # Ajustar ancho de columnas
        worksheet = writer.sheets['Ciclistas']
        for col in worksheet.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 30)
            worksheet.column_dimensions[column].width = adjusted_width
    
    def _obtener_atributos_reales(self, grafo) -> List[str]:
        """Obtiene los atributos reales disponibles en el grafo"""
        atributos_reales = set()
        
        # Recorrer todos los arcos para encontrar atributos
        for origen, destino, atributos in grafo.edges(data=True):
            for key in atributos.keys():
                # Excluir atributos técnicos
                if key not in ['weight', 'distancia_real']:
                    atributos_reales.add(key)
        
        # Convertir a lista y ordenar
        return sorted(list(atributos_reales))
