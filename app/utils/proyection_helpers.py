from catalog.projections_catalog import get_evat_data,get_excel_data
from utils.data_generation_helper import get_id,get_id_ps,generate_proyection
from utils.data_integration_helper import group_and_get_last_week_by_pool
from utils.cleaning_helpers import clean_nulls_and_fill_nan, clean_no_sense_values,filter_cycles_close_to_hasrvest
from constants.general import FECHA_MINIMA_ULTIMO_DATO,MINIMO_DIAS_PROYECTO,VARIABLES_INTERES
import streamlit as st
import numpy as np
import pandas as pd



def get_projections(farm_name, project_duration=90,  project_survival=0.75, project_range=21, is_using_personalized_cost=False, is_using_personalized_price=False, prices_table=None, cost_info=False):

    # importamos los datos de la base de datos del evat
    data_df = get_evat_data(farm_name)
    #importamos datos de precios
    precios_df = get_excel_data( sheet_name='precios')
    # importamos datos de distribucion por tallas
    distribucion_tallas_df = get_excel_data( sheet_name='distribucion')
    # importamos datos de aguaje
    aguajes_df = get_excel_data( sheet_name='aguajes')
    ## configuramos los nuevos costos en caso de ser personalizado
    if is_using_personalized_cost:
        data_df['costo_mix_alimento_kg'] = cost_info['mix']
        data_df['costo_millar_larva'] = cost_info['millar']
        data_df['costo_fijo_ha_dia'] = cost_info['fijo']
    ## configuramos los nuevos precios en caso de ser personalizado
    if is_using_personalized_price:
        precios_df = prices_table
    print(precios_df)

    
    ## llenamos los nulos de raleos y vairables economicas y comprobamos nulos
    evat_consolidado = clean_nulls_and_fill_nan(data_df)
    ### analizamos las variables para encontrar errores
    evat_consolidado = clean_no_sense_values(evat_consolidado)
    ### creamos id
    evat_consolidado['id'] = np.vectorize(get_id)(evat_consolidado['campo'], evat_consolidado['piscina'],evat_consolidado['fecha_siembra'])
    evat_consolidado['id_piscina'] = np.vectorize(get_id_ps)(evat_consolidado['campo'], evat_consolidado['piscina'])
    # agrupamos para obtener el ultimo dato de cada piscina
    evat_ultima_semana_df = group_and_get_last_week_by_pool(evat_consolidado)
    # filtramos solo piscinas actualizadas
    evat_ultima_semana_df =  evat_ultima_semana_df[evat_ultima_semana_df['fecha_muestreo'] >= FECHA_MINIMA_ULTIMO_DATO]
    ## reseteamos el index
    evat_ultima_semana_df = evat_ultima_semana_df.reset_index(drop=True)
    ## creamos dos columnas en base a la duracion y sobrevivencia del proyecto
    evat_ultima_semana_df['dias_proyecto'] = project_duration
    evat_ultima_semana_df['sobrevivencia_proyecto'] = project_survival
    #filtramos piscinas cerca a cosecha y que sus dias de cultivo sean mayores al del proyecto
    evat_ultima_semana_df = filter_cycles_close_to_hasrvest(evat_ultima_semana_df,MINIMO_DIAS_PROYECTO)
    # creamos una copa para comenzar la proyeccion
    evat_df = evat_ultima_semana_df.copy()
    # partimos por el dia de proyecto
    print(evat_df.columns)
    evat_df['Días faltantes para lograr el peso del proyecto'] = np.where(project_duration > evat_df['dias_cultivo'],
                                                                        project_duration - evat_df['dias_cultivo'],
                                                                        0
                                                                        ) 
    evat_df['Días restantes para cumplir proyecto'] = evat_df['Días faltantes para lograr el peso del proyecto']
    evat_df = generate_proyection(evat_df,project_survival,project_duration,precios_df, distribucion_tallas_df)
    proyecciones_df = evat_df[VARIABLES_INTERES]
    evat__hacia_atras_df = evat_df.copy()
    progress_text = f"Generando {project_range} proyecciones hacia adelante"
    my_bar_foward = st.progress(0, text=progress_text)
    for i in range(project_range):
        evat_df['tipo_proyeccion'] = 'después de la proyección'
        evat_df['Días restantes para cumplir proyecto'] = evat_df['Días restantes para cumplir proyecto'] + 1
        evat_df = generate_proyection(evat_df, project_survival, project_duration, precios_df, distribucion_tallas_df, 1)
        proyecciones_df = pd.concat([proyecciones_df, evat_df[VARIABLES_INTERES]], ignore_index=True)
        my_bar_foward.progress(round(((i+1)*100)/project_range), text=progress_text)
    my_bar_foward.empty()
    evat_df = evat__hacia_atras_df.copy()
    progress_text = f"Generando {project_range} proyecciones hacia atrás"
    my_bar_backward = st.progress(0, text=progress_text)
    for i in range(project_range):
        evat_df['tipo_proyeccion'] = 'antes de la proyección'
        evat_df['Días restantes para cumplir proyecto'] = evat_df['Días restantes para cumplir proyecto'] - 1
        evat_df = generate_proyection(evat_df,project_survival,project_duration,precios_df, distribucion_tallas_df, -1)
        proyecciones_df = pd.concat([proyecciones_df, evat_df[VARIABLES_INTERES]], ignore_index=True)
        my_bar_backward.progress(round(((i+1)*100)/project_range), text=progress_text)
    my_bar_backward.empty()

    proyecciones_df['Fecha estimada de cosecha'] = proyecciones_df['Fecha estimada de cosecha'].dt.tz_localize(None)
    #### calcumalos si es aguaje o no
    def get_is_Aguaje(fecha_estimada_cosecha):
        res = 0
        for ind in aguajes_df.index:
            date_start, date_end = aguajes_df['INICIO'][ind], aguajes_df['FIN'][ind]
            if fecha_estimada_cosecha >= date_start and fecha_estimada_cosecha <= date_end:
                res = 1
                return res
        return 0
    proyecciones_df['aguaje'] = proyecciones_df['Fecha estimada de cosecha'].apply(get_is_Aguaje)
    ### calculamos la talla
    proyecciones_df['talla'] = 1000/proyecciones_df['Peso final proyectado (gr)']
    proyecciones_df['talla'] = proyecciones_df['talla'].round(2)
    ### calculamos el precio en lb
    proyecciones_df['Precio venta pesca final ($/lb)'] = proyecciones_df['Precio venta pesca final ($/kg)']/2.20462
    proyecciones_df['Precio venta pesca final ($/lb)'] = proyecciones_df['Precio venta pesca final ($/lb)'].round(2)
    proyecciones_df['FCA Proyecto'] = proyecciones_df['FCA Proyecto'].round(2)
    proyecciones_df['ROI Proyecto'] = proyecciones_df['ROI Proyecto']*100
    proyecciones_df['ROI Proyecto'] = proyecciones_df['ROI Proyecto'].round(2)
    
    proyecciones_df['UP ($/Ha/Día) Proyecto'] = proyecciones_df['UP ($/Ha/Día) Proyecto'].round(2)
    proyecciones_df['Total Costo x Libra ($/lb) Proyecto'] = proyecciones_df['Total Costo x Libra ($/lb) Proyecto'].round(2)
    proyecciones_df= proyecciones_df.rename(columns={
                    'Días de ciclo finales': 'dias',
                    "Peso final proyectado (gr)": "peso",
                    "Biomasa proyecto (lb/ha)": "biomasa",
                    "Sobrevivencia final de ciclo proyecto (%)": "sobrevivencia",
                    "FCA Proyecto": "fca",
                    "Total Costo x Libra ($/lb) Proyecto": "costo",
                    "UP ($/Ha/Día) Proyecto": "up",
                    "ROI Proyecto": "roi",
                    'Campo': "campo",
                    'piscina' : "piscina",
                    'Fecha estimada de cosecha' : 'fecha_estimada_cosecha',
                    'peso_siembra_gr' : 'peso_siembra',
                    'densidad_siembra_ind_m2' : 'densidad_siembra',
                    'dias_cultivo' : 'dia_final',
                    'peso_actual_gr' : 'peso_actual',
                    'Precio venta pesca final ($/lb)' : 'precio_venta_lbs',
                    'Precio venta pesca final ($/kg)' : "precio_venta_pesca"
                        })
    proyecciones_df = proyecciones_df.sort_values(by=["piscina", "fecha_estimada_cosecha"])
    return proyecciones_df


def get_prices_dataframe():
    precios_df = get_excel_data( sheet_name='precios')