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
                
                # Calcular estadísticas de uso
                total_uso = sum(simulador.arcos_utilizados.values())
                porcentaje_uso = (uso_count / max(1, total_uso)) * 100 if total_uso > 0 else 0
                
                # Calcular tiempo promedio de desplazamiento (basado en velocidad promedio)
                velocidad_promedio = 12.5  # km/h promedio (3.47 m/s)
                tiempo_promedio = distancia / (velocidad_promedio * 1000 / 3600) if distancia > 0 else 0
                
                # Crear fila con datos optimizados
                fila = [
                    tramo_id,
                    origen,
                    destino,
                    f"{distancia:.1f}",
                    uso_count,
                    f"{porcentaje_uso:.1f}%",
                    f"{tiempo_promedio:.1f}s"
                ]
                
                # Agregar solo los atributos reales que existen y tienen valor
                atributos_importantes = ['seguridad', 'luminosidad', 'inclinacion']
                for attr in atributos_importantes:
                    if attr in atributos_reales and attr in atributos:
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
            'Ciclistas que lo usaron', 'Porcentaje de uso', 'Tiempo promedio (s)'
        ]
        
        # Solo agregar columnas de atributos que realmente existen en los datos
        if simulador.usar_grafo_real and simulador.grafo and datos_tramos:
            # Verificar qué atributos realmente tienen datos
            atributos_con_datos = set()
            for fila in datos_tramos:
                # Las columnas de atributos empiezan después de las 7 columnas básicas
                for i, attr in enumerate(['seguridad', 'luminosidad', 'inclinacion']):
                    col_index = 7 + i  # 7 columnas básicas + índice del atributo
                    if col_index < len(fila) and fila[col_index] != 'N/A':
                        atributos_con_datos.add(attr)
            
            # Solo agregar columnas para atributos que tienen datos
            for attr in ['seguridad', 'luminosidad', 'inclinacion']:
                if attr in atributos_con_datos:
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
                    # Fallback: calcular tiempo estimado si no hay datos reales
                    velocidad_promedio = 12.5  # km/h promedio
                    tiempo_total = distancia_total / (velocidad_promedio * 1000 / 3600) if distancia_total > 0 else 0
                
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
                    f"{distancia_total:.1f}",
                    f"{tiempo_total:.1f}s",
                    f"{tiempo_promedio_tramo:.1f}s",
                    f"{velocidad_promedio_ciclista:.2f} m/s",
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
                                fila.append(f"{pref_valor:.2f}")
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
            datos_tiempos.append(["Tiempo promedio de viaje", f"{tiempo_promedio:.2f} segundos"])
            datos_tiempos.append(["Tiempo mínimo de viaje", f"{tiempo_minimo:.2f} segundos"])
            datos_tiempos.append(["Tiempo máximo de viaje", f"{tiempo_maximo:.2f} segundos"])
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
            
            # Formatear tiempos de tramos
            tiempos_tramos_str = "; ".join([f"{t:.1f}s" for t in tiempos_tramos[:5]])
            if len(tiempos_tramos) > 5:
                tiempos_tramos_str += f" (+{len(tiempos_tramos)-5} más)"
            
            datos_tiempos.append([
                f"Ciclista {ciclista_id} ({origen}→{destino})",
                f"{tiempo_total:.2f}",
                num_tramos,
                f"{tiempo_promedio_tramo:.2f}",
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
