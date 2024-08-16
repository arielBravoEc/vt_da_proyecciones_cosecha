from catalog.projections_catalog import (
    get_evat_data,
    get_excel_data,
    get_evat_data_test,
)
from utils.data_generation_helper import get_id, get_id_ps, generate_proyection
from utils.data_integration_helper import group_and_get_last_week_by_pool
from utils.cleaning_helpers import (
    clean_nulls_and_fill_nan,
    clean_no_sense_values,
    filter_cycles_close_to_hasrvest,
)
from constants.general import (
    FECHA_MINIMA_ULTIMO_DATO,
    MINIMO_DIAS_PROYECTO,
    VARIABLES_INTERES,
    DIAS_SECADO,
    MESSAGE_ERROR_NULLS,
)
import streamlit as st
import numpy as np
import pandas as pd


def get_projections(
    farm_name: str,
    project_duration: int = 90,
    project_survival: float = 0.75,
    project_range: int = 21,
    is_using_personalized_cost: bool = False,
    is_using_personalized_price: bool = False,
    prices_table: pd.DataFrame = None,
    cost_info: dict = {},
    is_using_personalized_load_capacity: bool = False,
    load_capacity: float = None,
    is_using_lineal_feed: bool = False,
    is_using_dynamical_feed: bool = False,
    is_using_bw_feed: bool = True,
    percentage_dynamical_feed: int = None,
    is_using_sob_campo: bool = False,
    percentage_sob: int = 0,
    test: bool = False,  # para el testeo especificamente
    fecha_ultimo_dato: str = FECHA_MINIMA_ULTIMO_DATO,  # para el testeo especificamente
    minimo_dias_proyecto: int = MINIMO_DIAS_PROYECTO,  # para el testeo especificamente
    fecha_maxima_muestreo=None,  # opcional para el testeo especificamente
    pool_proy_test: str = None,  # opcional para el testeo especificamente
):
    """
    Esta ``función`` procesa el evat y retorna todas las proyecciones.
    Args:
        farm_name (str): Nombre del campo.
        project_survival (float): sobrevivencia del proyecto
        project_duration (int): duracion del proyecto
        project_range (int): rango de días para hacer la proyección antes y después
        is_using_personalized_cost (bool): booleano que indica si se está
        usando costos personalizados o por defecto
        is_using_personalized_price (bool): booleano que indica si se está
        usando precios personalizados o por defecto
        prices_table (pd.DataFrame): variable que guarda los precios personalizados
        cost_info (dict): diccionario con los valores de los costos personalizados
        is_using_personalized_load_capacity (bool): variable que nos dice si está
        usando capac de carga personalizada o el dato del evat.
        load_capacity (float): variable con la capacidad de carga personalizada
        is_using_lineal_feed (bool): booleano que indica si se está usando
        alimentación de manera lineal para la proyección.
        is_using_dynamical_feed (bool): booleano que indica si se está usando
        alimentación con un aumento porcentual para la proyección.
        is_using_bw_feed (bool): booleano que indica si se está usando
        alimentación en base a la curva de bw.
        percentage_dynamical_feed (int): porcentaje de aumento de alimento en la proyeccion
        (sirve cuando se selecciona proyectar el alimento de manera dinamica)
        is_using_sob_campo (bool): booleano que indica si se está usando son de campo o
        por consumo para hacer la proyeccion
        percentage_sob  (int): porcentaje de aumento o dismunución
        de sobrevivencia en la proyeccion
        test (bool): variable que nos indica cuando se está haciendo un test
        de acertividad.
        fecha_ultimo_dato (str): Fecha con el ultimo dato a considerar en los muestreos
        (debe ser 30 dias menor a la ultima cosecha analizada)
        minimo_dias_proyecto (int): mínimo de  días para considerar si un ciclo
        está cerca de cosecha y puede ser analizado.
        fecha_maxima_muestreo: para el test de acertividad
        variable que nos ayuda a determinar el dato maximo a
        obtener de la base para simular n semanas anteriores.

        pool_proy_test (str): para el test de acertividad: indica de
        que piscina se va a realizar la proyeccion.
    Returns:
        Retorna el dataframe con las proyecciones
    """

    # importamos los datos de la base de datos del evat
    if test:
        data_df = get_evat_data_test(farm_name, fecha_maxima_muestreo, pool_proy_test)
    else:
        # si no es test
        data_df = get_evat_data(farm_name)
    # eliminamos ps 132 de aglipesca debido a que es precria

    if len(data_df) > 0:
        # importamos datos de precios
        precios_df = get_excel_data(sheet_name="precios")
        # importamos datos de distribucion por tallas
        distribucion_tallas_df = get_excel_data(sheet_name="distribucion")
        # importamos datos de aguaje
        aguajes_df = get_excel_data(sheet_name="aguajes")
        # dias secos por defecto
        empty_days = DIAS_SECADO
        # configuramos los nuevos costos en caso de ser personalizado
        if is_using_personalized_cost:
            data_df["costo_mix_alimento_kg"] = cost_info["mix"]
            data_df["costo_millar_larva"] = cost_info["millar"]
            data_df["costo_fijo_ha_dia"] = cost_info["fijo"]
            empty_days = cost_info["dias_secos"]
        if is_using_personalized_load_capacity:
            data_df["capacidad_de_carga_lbs_ha"] = load_capacity
        # configuramos los nuevos precios en caso de ser personalizado
        if is_using_personalized_price:
            precios_df = prices_table
        # print(prices_table)

        # analizamos las variables para encontrar errores
        # print(data_df[data_df['piscina']== '19'])
        # VALIDAMOS QUE SE ELIMINEN DATOS POR VALORES QUE NO TIENEN SENTIDO
        try:
            # llenamos los nulos de raleos y vairables economicas y comprobamos nulos
            evat_consolidado = clean_nulls_and_fill_nan(data_df)
            evat_consolidado = clean_no_sense_values(evat_consolidado)
            evat_consolidado["id"] = np.vectorize(get_id)(
                evat_consolidado["campo"],
                evat_consolidado["piscina"],
                evat_consolidado["fecha_siembra"],
            )
            evat_consolidado["id_piscina"] = np.vectorize(get_id_ps)(
                evat_consolidado["campo"], evat_consolidado["piscina"]
            )
            # agrupamos para obtener el ultimo dato de cada piscina
            evat_ultima_semana_df = group_and_get_last_week_by_pool(evat_consolidado)
        except ValueError as e:
            if (
                "cannot call 'vectorize' on size 0 inputs unless 'otypes' is set"
                in str(e)
            ):
                print(
                    "Error: La entrada es de tamaño 0. Por favor, verifica tus datos."
                )
            else:
                print(f"Error: {e}")
            return pd.DataFrame(), MESSAGE_ERROR_NULLS
        # creamos id
        if len(evat_ultima_semana_df) == 0:
            return pd.DataFrame, MESSAGE_ERROR_NULLS
        # filtramos solo piscinas actualizadas
        # print("AA", evat_ultima_semana_df.shape)
        # print(evat_ultima_semana_df)
        if not test:
            evat_ultima_semana_df = evat_ultima_semana_df[
                evat_ultima_semana_df["fecha_muestreo"] >= fecha_ultimo_dato
            ]
        # print("fecha: ", fecha_ultimo_dato)
        # print("BBB ", evat_ultima_semana_df.shape)
        # reseteamos el index
        evat_ultima_semana_df = evat_ultima_semana_df.reset_index(drop=True)
        # creamos dos columnas en base a la duracion y sobrevivencia del proyecto
        evat_ultima_semana_df["dias_proyecto"] = project_duration
        evat_ultima_semana_df["sobrevivencia_proyecto"] = project_survival
        # filtramos piscinas cerca a cosecha y que sus dias de cultivo sean mayores al del proyecto
        evat_ultima_semana_df = filter_cycles_close_to_hasrvest(
            evat_ultima_semana_df, minimo_dias_proyecto
        )
        # print(evat_ultima_semana_df.shape)
        # creamos una copa para comenzar la proyeccion
        evat_df = evat_ultima_semana_df.copy()
        # partimos por el dia de proyecto
        evat_df["Días faltantes para lograr el peso del proyecto"] = np.where(
            project_duration > evat_df["dias_cultivo"],
            project_duration - evat_df["dias_cultivo"],
            0,
        )
        evat_df["Días restantes para cumplir proyecto"] = evat_df[
            "Días faltantes para lograr el peso del proyecto"
        ]
        evat_df = generate_proyection(
            farm_name,
            evat_df,
            project_survival,
            project_duration,
            precios_df,
            distribucion_tallas_df,
            is_using_lineal_feed=is_using_lineal_feed,
            is_using_dynamical_feed=is_using_dynamical_feed,
            empty_days=empty_days,
            percentage_dynamical_feed=percentage_dynamical_feed,
            is_using_sob_campo=is_using_sob_campo,
            percentage_sob=percentage_sob,
        )
        # print(evat_df.columns)
        proyecciones_df = evat_df[VARIABLES_INTERES]
        evat__hacia_atras_df = evat_df.copy()
        progress_text = f"Generando {project_range} proyecciones hacia adelante"
        my_bar_foward = st.progress(0, text=progress_text)
        for i in range(project_range):
            evat_df["tipo_proyeccion"] = "después de la proyección"
            evat_df["Días restantes para cumplir proyecto"] = (
                evat_df["Días restantes para cumplir proyecto"] + 1
            )
            evat_df = generate_proyection(
                farm_name,
                evat_df,
                project_survival,
                project_duration,
                precios_df,
                distribucion_tallas_df,
                dias_ciclo_finales=1,
                is_using_lineal_feed=is_using_lineal_feed,
                is_using_dynamical_feed=is_using_dynamical_feed,
                empty_days=empty_days,
                percentage_dynamical_feed=percentage_dynamical_feed,
                is_using_sob_campo=is_using_sob_campo,
                percentage_sob=percentage_sob,
            )
            proyecciones_df = pd.concat(
                [proyecciones_df, evat_df[VARIABLES_INTERES]], ignore_index=True
            )
            my_bar_foward.progress(
                round(((i + 1) * 100) / project_range), text=progress_text
            )
        my_bar_foward.empty()
        evat_df = evat__hacia_atras_df.copy()
        progress_text = f"Generando {project_range} proyecciones hacia atrás"
        my_bar_backward = st.progress(0, text=progress_text)
        for i in range(project_range):
            evat_df["tipo_proyeccion"] = "antes de la proyección"
            evat_df["Días restantes para cumplir proyecto"] = (
                evat_df["Días restantes para cumplir proyecto"] - 1
            )
            evat_df = generate_proyection(
                farm_name,
                evat_df,
                project_survival,
                project_duration,
                precios_df,
                distribucion_tallas_df,
                dias_ciclo_finales=-1,
                is_using_lineal_feed=is_using_lineal_feed,
                is_using_dynamical_feed=is_using_dynamical_feed,
                empty_days=empty_days,
                percentage_dynamical_feed=percentage_dynamical_feed,
                is_using_sob_campo=is_using_sob_campo,
                percentage_sob=percentage_sob,
            )
            proyecciones_df = pd.concat(
                [proyecciones_df, evat_df[VARIABLES_INTERES]], ignore_index=True
            )
            my_bar_backward.progress(
                round(((i + 1) * 100) / project_range), text=progress_text
            )
        my_bar_backward.empty()

        proyecciones_df["Fecha estimada de cosecha"] = proyecciones_df[
            "Fecha estimada de cosecha"
        ].dt.tz_localize(None)

        # calcumalos si es aguaje o no
        def get_is_Aguaje(fecha_estimada_cosecha):
            res = 0
            for ind in aguajes_df.index:
                date_start, date_end = aguajes_df["INICIO"][ind], aguajes_df["FIN"][ind]
                if (
                    fecha_estimada_cosecha >= date_start
                    and fecha_estimada_cosecha <= date_end
                ):
                    res = 1
                    return res
            return 0

        proyecciones_df["aguaje"] = proyecciones_df["Fecha estimada de cosecha"].apply(
            get_is_Aguaje
        )
        # calculamos la talla
        proyecciones_df["talla"] = 1000 / proyecciones_df["Peso final proyectado (gr)"]
        proyecciones_df["talla"] = proyecciones_df["talla"].round(2)
        # calculamos el precio en lb
        proyecciones_df["Precio venta pesca final ($/lb)"] = (
            proyecciones_df["Precio venta pesca final ($/kg)"] / 2.20462
        )
        proyecciones_df["Precio venta pesca final ($/lb)"] = proyecciones_df[
            "Precio venta pesca final ($/lb)"
        ].round(2)
        proyecciones_df["FCA Proyecto"] = proyecciones_df["FCA Proyecto"].round(2)
        proyecciones_df["ROI Proyecto"] = proyecciones_df["ROI Proyecto"] * 100
        proyecciones_df["ROI Proyecto"] = proyecciones_df["ROI Proyecto"].round(2)

        proyecciones_df["UP ($/Ha/Día) Proyecto"] = proyecciones_df[
            "UP ($/Ha/Día) Proyecto"
        ].round(2)
        proyecciones_df["Total Costo x Libra ($/lb) Proyecto"] = proyecciones_df[
            "Total Costo x Libra ($/lb) Proyecto"
        ].round(2)
        proyecciones_df = proyecciones_df.rename(
            columns={
                "Días de ciclo finales": "dias_proyectados",
                "Peso final proyectado (gr)": "peso_proyectado_gr",
                "Biomasa proyecto (lb/ha)": "biomasa_proyectada_lb_ha",
                "Biomas total proyecto (lb)": "biomasa_total_proyectada_lb",
                "Sobrevivencia final de ciclo proyecto (%)": "sobrevivencia_pesca_proyectada",
                "FCA Proyecto": "fca",
                "Total Costo x Libra ($/lb) Proyecto": "costo_lb_proyecto",
                "UP ($/Ha/Día) Proyecto": "up_proyecto",
                "ROI Proyecto": "roi_proyecto",
                "Campo": "campo",
                "piscina": "piscina",
                "Fecha estimada de cosecha": "fecha_estimada_cosecha",
                "peso_siembra_gr": "peso_siembra",
                "densidad_siembra_ind_m2": "densidad_siembra",
                "dias_cultivo": "dia_final",
                "peso_actual_gr": "peso_actual",
                "Precio venta pesca final ($/lb)": "precio_venta_lbs",
                "Precio venta pesca final ($/kg)": "precio_venta_pesca_kg",
            }
        )
        proyecciones_df = proyecciones_df.sort_values(
            by=["piscina", "fecha_estimada_cosecha"]
        )
        proyecciones_df["fecha_estimada_cosecha"] = proyecciones_df[
            "fecha_estimada_cosecha"
        ].astype(str)
        proyecciones_df["fecha_estimada_cosecha"] = proyecciones_df[
            "fecha_estimada_cosecha"
        ].str.slice(0, 10)
        proyecciones_df["fecha_siembra"] = proyecciones_df["fecha_siembra"].astype(str)
        proyecciones_df["fecha_siembra"] = proyecciones_df["fecha_siembra"].str.slice(
            0, 10
        )
        proyecciones_df["fecha_muestreo"] = proyecciones_df["fecha_muestreo"].astype(
            str
        )
        proyecciones_df["fecha_muestreo"] = proyecciones_df["fecha_muestreo"].str.slice(
            0, 10
        )
        # proyecciones_df["biomasa_total"] = (
        #    proyecciones_df["biomasa"] * proyecciones_df["ha"]
        # )
        proyecciones_df["precio_venta_lbs_con_rendimiento"] = (
            proyecciones_df["precio_venta_lbs"] * 0.95
        )
        if len(proyecciones_df) > 0:
            return proyecciones_df, "Proyecciones generadas con éxito."
        else:
            return proyecciones_df, MESSAGE_ERROR_NULLS
    else:
        # si no hay datos retornamos vacio
        proyecciones_df = data_df
        return (
            proyecciones_df,
            "Para este campo no existen datos de piscinas actualizadas en los últimos 30 días.",
        )
