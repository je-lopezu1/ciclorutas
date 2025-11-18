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
        try:
            with pd.ExcelWriter(ruta_archivo, engine='openpyxl') as writer:
                
                # Hoja 1: Información General de la Simulación
                print("📋 Creando hoja Info Simulación...")
                self._crear_hoja_info_simulacion(simulador, writer)
                
                # Hoja 2: Tramos
                print("🛣️ Creando hoja Tramos...")
                self._crear_hoja_tramos(simulador, writer)
                
                # Hoja 3: Ciclistas
                print("🚴 Creando hoja Ciclistas...")
                self._crear_hoja_ciclistas(simulador, writer)
                
                # Hoja 4: Tiempos de Desplazamiento
                print("⏱️ Creando hoja Tiempos...")
                self._crear_hoja_tiempos(simulador, writer)
                
        except Exception as e:
            print(f"❌ Error creando archivo Excel: {e}")
            raise
        
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
        datos_info.append(["Duración de simulación (segundos)", simulador.config.duracion_simulacion])
        datos_info.append(["Estado final", simulador.estado])
        datos_info.append(["Tiempo transcurrido (segundos)", round(simulador.tiempo_actual, 2)])
        datos_info.append(["", ""])
        
        # Información del grafo
        datos_info.append(["INFORMACIÓN DEL GRAFO", ""])
        if simulador.usar_grafo_real and simulador.grafo:
            datos_info.append(["Usando grafo real", "Sí"])
            datos_info.append(["Número de nodos", stats.get('grafo_nodos', 0)])
            datos_info.append(["Número de arcos", stats.get('grafo_arcos', 0)])
            datos_info.append(["Grafo conectado", "Sí" if stats.get('grafo_conectado', False) else "No"])
            datos_info.append(["Distancia promedio arcos (metros)", round(stats.get('distancia_promedio_arcos', 0), 2)])
        else:
            datos_info.append(["Usando grafo real", "No"])
        datos_info.append(["", ""])
        
        # Estadísticas de ciclistas
        datos_info.append(["ESTADÍSTICAS DE CICLISTAS", ""])
        datos_info.append(["Total de ciclistas creados", stats.get('total_ciclistas', 0)])
        datos_info.append(["Ciclistas activos", stats.get('ciclistas_activos', 0)])
        datos_info.append(["Ciclistas completados", stats.get('ciclistas_completados', 0)])
        # Convertir velocidades de m/s a km/h (multiplicar por 3.6)
        velocidad_promedio_ms = stats.get('velocidad_promedio', 0)
        velocidad_minima_ms = stats.get('velocidad_minima', 0)
        velocidad_maxima_ms = stats.get('velocidad_maxima', 0)
        datos_info.append(["Velocidad promedio (km/h)", round(velocidad_promedio_ms * 3.6, 2)])
        datos_info.append(["Velocidad mínima (km/h)", round(velocidad_minima_ms * 3.6, 2)])
        datos_info.append(["Velocidad máxima (km/h)", round(velocidad_maxima_ms * 3.6, 2)])
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
        
        # Calcular ocupación de arcos una sola vez para optimizar
        ocupacion_arcos = {}
        try:
            ocupacion_arcos = simulador.calcular_ocupacion_arcos_tiempo(intervalo=1.0)
        except Exception as e:
            print(f"Advertencia: No se pudo calcular ocupación de arcos: {e}")
            ocupacion_arcos = {}
        
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
                
                # Calcular estadísticas de uso
                total_uso = sum(simulador.arcos_utilizados.values())
                porcentaje_uso = (uso_count / max(1, total_uso)) * 100 if total_uso > 0 else 0
                
                # Calcular tiempo promedio real de desplazamiento basado en los tiempos reales de los ciclistas
                tiempo_promedio = self._calcular_tiempo_promedio_tramo(simulador, tramo_id)
                
                # Calcular promedio de ciclistas en el tramo a lo largo de toda la simulación
                promedio_ciclistas = self._calcular_promedio_ciclistas_tramo(simulador, tramo_id, ocupacion_arcos)
                
                # Crear fila con datos optimizados
                fila = [
                    tramo_id,
                    origen,
                    destino,
                    round(distancia, 1),
                    uso_count,
                    round(porcentaje_uso, 1),
                    round(tiempo_promedio, 1),
                    round(promedio_ciclistas, 2)
                ]
                
                # Agregar TODOS los atributos reales que existen dinámicamente
                for attr in atributos_reales:
                    if attr not in ['weight', 'distancia', 'distancia_real']:  # Excluir técnicos
                        if attr in atributos:
                            valor = atributos.get(attr)
                            # Solo agregar si el valor no es None, vacío o 0
                            if valor is not None and valor != '' and valor != 0:
                                fila.append(valor)
                            else:
                                fila.append('N/A')
                        else:
                            fila.append('N/A')
                
                datos_tramos.append(fila)
        
        # Crear columnas dinámicamente basadas en los datos reales
        columnas = [
            'ID Tramo', 'Nodo Origen', 'Nodo Destino', 'Distancia (m)', 
            'Ciclistas que lo usaron', 'Porcentaje de uso (%)', 'Tiempo promedio (s)',
            'Promedio de ciclistas'
        ]
        
        # Detectar y agregar columnas dinámicamente
        if simulador.usar_grafo_real and simulador.grafo and datos_tramos:
            # Obtener nombres de atributos dinámicamente del grafo
            if datos_tramos:
                primera_fila = datos_tramos[0]  # Definir primera_fila
                # Detectar cuántos atributos adicionales hay
                num_atributos_adicionales = len(primera_fila) - 7  # 7 columnas básicas
                # Usar los nombres reales de los atributos encontrados
                atributos_encontrados = []
                for edge_data in simulador.grafo.edges(data=True):
                    for key in edge_data[2].keys():
                        if key not in ['weight', 'distancia', 'distancia_real']:
                            if key not in atributos_encontrados:
                                atributos_encontrados.append(key)
                    if len(atributos_encontrados) >= num_atributos_adicionales:
                        break
                
                # Agregar columnas con nombres reales
                for attr in atributos_encontrados[:num_atributos_adicionales]:
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
        
        try:
            # Obtener TODOS los ciclistas que participaron en la simulación
            todos_ciclistas = set()
            
            # Agregar ciclistas de rutas
            todos_ciclistas.update(simulador.rutas_por_ciclista.keys())
            
            # Agregar ciclistas de estado
            todos_ciclistas.update(simulador.estado_ciclistas.keys())
            
            # Agregar ciclistas de arcos
            todos_ciclistas.update(simulador.arcos_por_ciclista.keys())
            
            # Agregar ciclistas de tiempos
            todos_ciclistas.update(simulador.tiempos_por_ciclista.keys())
            
            print(f"🔍 Procesando {len(todos_ciclistas)} ciclistas totales...")
            datos_ciclistas = []
            
            # Procesar información de cada ciclista
            for ciclista_id in sorted(todos_ciclistas):
                # Obtener información de ruta si existe
                ruta_info = simulador.rutas_por_ciclista.get(ciclista_id, {})
                origen = ruta_info.get('origen', 'N/A')
                destino = ruta_info.get('destino', 'N/A')
                ruta_simple = ruta_info.get('ruta_simple', 'N/A')
                ruta_detallada = ruta_info.get('ruta_detallada', 'N/A')
                
                # Obtener perfil del ciclista
                perfil = simulador.perfiles_ciclistas.get(ciclista_id, 'Sin perfil')
                
                # Obtener arcos utilizados por este ciclista
                arcos_ciclista = simulador.arcos_por_ciclista.get(ciclista_id, [])
                num_tramos = len(arcos_ciclista)
                
                # Calcular distancia total
                distancia_total = 0
                if simulador.usar_grafo_real and simulador.grafo:
                    for arco in arcos_ciclista:
                        if "->" in arco:
                            nodo_origen, nodo_destino = arco.split("->")
                            if simulador.grafo.has_edge(nodo_origen, nodo_destino):
                                dist = simulador.grafo[nodo_origen][nodo_destino].get('distancia_real', 
                                                                                       simulador.grafo[nodo_origen][nodo_destino].get('distancia', 0))
                                distancia_total += dist
                
                # Obtener tiempo total real de la simulación
                tiempo_total = simulador.tiempos_por_ciclista.get(ciclista_id, 0)
                if tiempo_total == 0:
                    # Fallback: calcular tiempo estimado usando promedio de velocidades de la configuración
                    if hasattr(simulador, 'config') and simulador.config:
                        velocidad_min = simulador.config.velocidad_min  # m/s
                        velocidad_max = simulador.config.velocidad_max  # m/s
                        velocidad_promedio = (velocidad_min + velocidad_max) / 2.0  # m/s
                    else:
                        velocidad_promedio = 12.5 * 1000 / 3600  # 12.5 km/h = 3.47 m/s (fallback)
                    tiempo_total = distancia_total / velocidad_promedio if distancia_total > 0 and velocidad_promedio > 0 else 0
                
                # Obtener tiempos por tramo
                tiempos_tramos = simulador.tiempos_por_tramo.get(ciclista_id, [])
                tiempo_promedio_tramo = sum(tiempos_tramos) / len(tiempos_tramos) if tiempos_tramos else 0
                
                # Estado del ciclista
                estado = simulador.estado_ciclistas.get(ciclista_id, 'Desconocido')
                
                # Velocidad promedio del ciclista
                velocidad_promedio_ciclista = (distancia_total / tiempo_total) if tiempo_total > 0 else 0
                
                # Resumir tramos utilizados (máximo 5)
                tramos_resumidos = arcos_ciclista[:5] if len(arcos_ciclista) > 5 else arcos_ciclista
                tramos_utilizados = "; ".join(tramos_resumidos)
                if len(arcos_ciclista) > 5:
                    tramos_utilizados += f" (+{len(arcos_ciclista)-5} más)"
                
                # Crear fila completa con toda la información de la simulación
                fila = [
                    ciclista_id,
                    origen,
                    destino,
                    ruta_simple,
                    ruta_detallada,
                    perfil if isinstance(perfil, str) else f"Perfil {perfil}",
                    num_tramos,
                    round(distancia_total, 1),
                    round(tiempo_total, 1),
                    round(tiempo_promedio_tramo, 1),
                    round(velocidad_promedio_ciclista, 2),
                    tramos_utilizados,
                    estado
                ]
                
                # Agregar preferencias del perfil dinámicamente
                if isinstance(perfil, dict) and perfil:
                    # Obtener todas las preferencias disponibles en el perfil
                    preferencias_disponibles = ['seguridad', 'luminosidad', 'distancia', 'inclinacion']
                    for attr in preferencias_disponibles:
                        if attr in perfil and perfil[attr] is not None and perfil[attr] != '':
                            pref_valor = perfil.get(attr)
                            if isinstance(pref_valor, (int, float)):
                                fila.append(round(pref_valor, 2))
                            else:
                                fila.append(str(pref_valor))
                        else:
                            fila.append('N/A')
                else:
                    # Si no hay perfil, agregar N/A para todas las preferencias
                    fila.extend(['N/A', 'N/A', 'N/A', 'N/A'])
                
                # Almacenar la fila completa para análisis posterior
                datos_ciclistas.append(fila)
            
            # Crear columnas dinámicamente basadas en los datos reales
            columnas_basicas = [
                'ID Ciclista', 'Origen', 'Destino', 'Ruta Simple', 'Ruta Detallada',
                'Perfil', 'Número de Tramos', 'Distancia Total (m)', 'Tiempo Total (s)', 
                'Tiempo Promedio por Tramo (s)', 'Velocidad Promedio (m/s)', 'Tramos Utilizados', 'Estado'
            ]
            
            # Verificar qué preferencias realmente tienen datos
            preferencias_con_datos = set()
            for fila in datos_ciclistas:
                # Las preferencias empiezan después de las 13 columnas básicas
                for i, pref in enumerate(['seguridad', 'luminosidad', 'distancia', 'inclinacion']):
                    col_index = 13 + i  # 13 columnas básicas + índice de preferencia
                    if col_index < len(fila) and fila[col_index] != 'N/A':
                        preferencias_con_datos.add(pref)
            
            # Crear columnas finales
            columnas = columnas_basicas.copy()
            for pref in ['seguridad', 'luminosidad', 'distancia', 'inclinacion']:
                if pref in preferencias_con_datos:
                    columnas.append(f'Pref. {pref.title()}')
            
            # Recortar las filas para que coincidan con las columnas
            datos_ciclistas_recortados = []
            for fila in datos_ciclistas:
                # Tomar solo las columnas básicas + las preferencias que tienen datos
                fila_recortada = fila[:13]  # 13 columnas básicas
                for i, pref in enumerate(['seguridad', 'luminosidad', 'distancia', 'inclinacion']):
                    if pref in preferencias_con_datos:
                        col_index = 13 + i
                        if col_index < len(fila):
                            fila_recortada.append(fila[col_index])
                datos_ciclistas_recortados.append(fila_recortada)
            
            df_ciclistas = pd.DataFrame(datos_ciclistas_recortados, columns=columnas)
            
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
                
            print(f"✅ Hoja Ciclistas creada con {len(datos_ciclistas)} registros")
            
        except Exception as e:
            print(f"❌ Error creando hoja Ciclistas: {e}")
            # Crear hoja de error como fallback
            error_df = pd.DataFrame([['Error', f'No se pudo procesar ciclistas: {str(e)}']], 
                                  columns=['Error', 'Descripción'])
            error_df.to_excel(writer, sheet_name='Ciclistas', index=False)
    
    def _crear_hoja_tiempos(self, simulador, writer):
        """Crea la hoja con estadísticas de tiempos de desplazamiento"""
        
        datos_tiempos = []
        
        # Estadísticas generales de tiempos
        if simulador.tiempos_por_ciclista:
            tiempos_totales = list(simulador.tiempos_por_ciclista.values())
            tiempo_promedio = sum(tiempos_totales) / len(tiempos_totales)
            tiempo_minimo = min(tiempos_totales)
            tiempo_maximo = max(tiempos_totales)
            
            datos_tiempos.append(["ESTADÍSTICAS GENERALES DE TIEMPOS", ""])
            datos_tiempos.append(["Total de ciclistas con tiempo registrado", len(tiempos_totales)])
            datos_tiempos.append(["Tiempo promedio de viaje (segundos)", round(tiempo_promedio, 2)])
            datos_tiempos.append(["Tiempo mínimo de viaje (segundos)", round(tiempo_minimo, 2)])
            datos_tiempos.append(["Tiempo máximo de viaje (segundos)", round(tiempo_maximo, 2)])
            datos_tiempos.append(["", ""])
        
        # Detalles por ciclista
        datos_tiempos.append(["DETALLES POR CICLISTA", ""])
        datos_tiempos.append(["ID Ciclista", "Tiempo Total (s)", "Número de Tramos", "Tiempo Promedio por Tramo (s)", "Tramos con Tiempo", "Ruta Completa"])
        
        for ciclista_id, tiempo_total in simulador.tiempos_por_ciclista.items():
            # Obtener información del ciclista
            ruta_info = simulador.rutas_por_ciclista.get(ciclista_id, {})
            origen = ruta_info.get('origen', 'N/A')
            destino = ruta_info.get('destino', 'N/A')
            ruta_detallada = ruta_info.get('ruta_detallada', 'N/A')
            
            # Obtener tiempos por tramo
            tiempos_tramos = simulador.tiempos_por_tramo.get(ciclista_id, [])
            num_tramos = len(tiempos_tramos)
            tiempo_promedio_tramo = sum(tiempos_tramos) / len(tiempos_tramos) if tiempos_tramos else 0
            
            # Formatear tiempos de tramos (sin unidades en los valores)
            tiempos_tramos_str = "; ".join([f"{round(t, 1)}" for t in tiempos_tramos[:5]])
            if len(tiempos_tramos) > 5:
                tiempos_tramos_str += f" (+{len(tiempos_tramos)-5} más)"
            
            datos_tiempos.append([
                f"Ciclista {ciclista_id} ({origen}→{destino})",
                round(tiempo_total, 2),
                num_tramos,
                round(tiempo_promedio_tramo, 2),
                tiempos_tramos_str,
                ruta_detallada
            ])
        
        # Crear DataFrame
        df_tiempos = pd.DataFrame(datos_tiempos, columns=['Métrica', 'Valor', 'Detalle 1', 'Detalle 2', 'Detalle 3', 'Ruta Completa'])
        
        # Escribir a Excel
        df_tiempos.to_excel(writer, sheet_name='Tiempos', index=False)
        
        # Ajustar ancho de columnas
        worksheet = writer.sheets['Tiempos']
        worksheet.column_dimensions['A'].width = 40
        worksheet.column_dimensions['B'].width = 20
        worksheet.column_dimensions['C'].width = 15
        worksheet.column_dimensions['D'].width = 20
        worksheet.column_dimensions['E'].width = 30
        worksheet.column_dimensions['F'].width = 50  # Ruta Completa - más ancha
    
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
    
    def _calcular_tiempo_promedio_tramo(self, simulador, tramo_id: str) -> float:
        """
        Calcula el tiempo promedio real que tardaron todos los ciclistas en un tramo.
        
        Args:
            simulador: Instancia del simulador
            tramo_id: Identificador del tramo (formato: "origen->destino")
        
        Returns:
            Tiempo promedio en segundos (float). Retorna 0.0 si no hay datos.
        """
        try:
            tiempos_tramo = []
            
            # Recorrer todos los ciclistas que pasaron por este tramo
            # IMPORTANTE: Un ciclista puede pasar múltiples veces por el mismo arco
            # Necesitamos contar TODAS las veces, no solo la primera
            if hasattr(simulador, 'arcos_por_ciclista') and hasattr(simulador, 'tiempos_por_tramo'):
                for ciclista_id, arcos_ciclista in simulador.arcos_por_ciclista.items():
                    # Verificar si este ciclista pasó por este tramo (puede aparecer múltiples veces)
                    if tramo_id in arcos_ciclista:
                        # Obtener TODOS los índices donde aparece este tramo (no solo el primero)
                        if ciclista_id in simulador.tiempos_por_tramo:
                            tiempos_ciclista = simulador.tiempos_por_tramo[ciclista_id]
                            
                            # Buscar todas las ocurrencias del tramo en la ruta del ciclista
                            for indice, arco in enumerate(arcos_ciclista):
                                if arco == tramo_id and indice < len(tiempos_ciclista):
                                    tiempo_tramo = tiempos_ciclista[indice]
                                    if tiempo_tramo > 0:  # Solo incluir tiempos válidos
                                        tiempos_tramo.append(tiempo_tramo)
            
            # Calcular el promedio
            if tiempos_tramo:
                tiempo_promedio = sum(tiempos_tramo) / len(tiempos_tramo)
                return tiempo_promedio
            
            # Si no hay datos reales, calcular estimado basado en distancia y velocidad promedio
            # usando el promedio entre velocidad mínima y máxima de la configuración
            if simulador.usar_grafo_real and simulador.grafo:
                # Obtener distancia del tramo
                origen, destino = tramo_id.split('->')
                if simulador.grafo.has_edge(origen, destino):
                    atributos = simulador.grafo[origen][destino]
                    distancia = atributos.get('distancia', atributos.get('distancia_real', 0))
                    if distancia > 0:
                        # Calcular velocidad promedio usando el promedio entre velocidad mínima y máxima
                        # de la configuración de la simulación
                        if hasattr(simulador, 'config') and simulador.config:
                            velocidad_min = simulador.config.velocidad_min  # m/s
                            velocidad_max = simulador.config.velocidad_max  # m/s
                            velocidad_promedio = (velocidad_min + velocidad_max) / 2.0
                        else:
                            # Fallback si no hay configuración (velocidad promedio por defecto)
                            velocidad_promedio = 12.5 * 1000 / 3600  # 12.5 km/h = 3.47 m/s
                        
                        tiempo_estimado = distancia / velocidad_promedio if velocidad_promedio > 0 else 0
                        return tiempo_estimado
            
            return 0.0
            
        except Exception as e:
            print(f"Error al calcular tiempo promedio para tramo {tramo_id}: {e}")
            return 0.0
    
    def _calcular_promedio_ciclistas_tramo(self, simulador, tramo_id: str, ocupacion_arcos: Dict = None) -> float:
        """
        Calcula el promedio de ciclistas en un tramo a lo largo de toda la simulación.
        
        Args:
            simulador: Instancia del simulador
            tramo_id: Identificador del tramo (formato: "origen->destino")
            ocupacion_arcos: Diccionario con ocupación de arcos (opcional, para optimización)
        
        Returns:
            Promedio de ciclistas en el tramo (float)
        """
        try:
            # Si no se proporciona ocupacion_arcos, calcularla
            if ocupacion_arcos is None:
                ocupacion_arcos = simulador.calcular_ocupacion_arcos_tiempo(intervalo=1.0)
            
            # Obtener datos de ocupación para este tramo
            if tramo_id in ocupacion_arcos and ocupacion_arcos[tramo_id]:
                ocupacion_tiempo = ocupacion_arcos[tramo_id]
                
                # Si hay datos de ocupación, calcular el promedio
                if ocupacion_tiempo:
                    ocupaciones = [ocupacion for _, ocupacion in ocupacion_tiempo]
                    promedio = sum(ocupaciones) / len(ocupaciones) if ocupaciones else 0.0
                    return promedio
            
            # Si no hay datos de ocupación calculados, usar el método alternativo
            # basado en eventos de entrada/salida
            if hasattr(simulador, 'eventos_arcos') and simulador.eventos_arcos:
                # Filtrar eventos de este arco
                eventos_arco = [(t, tipo, ciclista_id) 
                               for t, a, tipo, ciclista_id in simulador.eventos_arcos 
                               if a == tramo_id]
                
                if eventos_arco:
                    # Ordenar eventos por tiempo
                    eventos_arco.sort(key=lambda x: x[0])
                    
                    # Calcular ocupación promedio usando método de integración temporal
                    tiempo_total = simulador.tiempo_actual if simulador.tiempo_actual > 0 else 1.0
                    tiempo_ocupado_total = 0.0
                    ocupacion_actual = 0
                    tiempo_anterior = 0.0
                    
                    for tiempo_evento, tipo_evento, _ in eventos_arco:
                        # Acumular tiempo ocupado desde el último evento
                        tiempo_ocupado_total += ocupacion_actual * (tiempo_evento - tiempo_anterior)
                        tiempo_anterior = tiempo_evento
                        
                        if tipo_evento == 'entrada':
                            ocupacion_actual += 1
                        elif tipo_evento == 'salida':
                            ocupacion_actual = max(0, ocupacion_actual - 1)
                    
                    # Agregar tiempo restante hasta el final
                    tiempo_ocupado_total += ocupacion_actual * (tiempo_total - tiempo_anterior)
                    
                    # Calcular promedio
                    promedio = tiempo_ocupado_total / tiempo_total if tiempo_total > 0 else 0.0
                    return promedio
            
            # Si no hay datos disponibles, retornar 0
            return 0.0
            
        except Exception as e:
            print(f"Error al calcular promedio de ciclistas para tramo {tramo_id}: {e}")
            return 0.0
