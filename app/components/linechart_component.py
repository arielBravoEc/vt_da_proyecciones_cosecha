import streamlit as st
import altair as alt
import numpy as np
import pandas as pd
from datetime import datetime
from utils.data_transformation import obtener_valor_normalizado
from constants.graphs_constants import (
    LABEL_FONT_SIZE,
    MARK_POINT_SIZE,
    AXIS_FONT_SIZE,
    PRIMARY_COLOR,
    TERTIARY_COLOR,
    DARK_BLUE_COLOR,
    LINE_SIZE,
    PLOT_MAPPING_VARIABLES_NAME,
    DICCIONARIO_NORMALIZACION_TOOLTIP,
)

FECHA_ACTUAL = datetime.now()


def plot_line_chart(data_df: pd.DataFrame, pool_str: str, variable_str: str) -> None:
    """
    Esta ``función`` hace un plot de un gráfico de
    líneas de una pisicna usando la librería altair
    Args:
        data_df (Pandas dataframe): Datos de las proyecciones.
        pool_str (str): string con el nombre de la pisicna a graficar
        variable_str (str): Nombre de la variable a
        graficar en el eje de las y.
        Esta variable debe pertenecer al dataframe,
        caso contrario presentará error.
    Raises:
        ValueError: Si faltan columnas requeridas en el DataFrame.
    Returns:
        Retorna None
    """
    # convertimos la variable de la opcion del select a su respectiva columna para mostrar los datos
    variable_str_normalizada = obtener_valor_normalizado(
        variable_str, DICCIONARIO_NORMALIZACION_TOOLTIP
    )
    # Verificar la presencia de las columnas necesarias
    required_columns = [
        "dias_proyectados",
        "piscina",
        "dias_proyectados",
        "up_proyecto",
        "costo_lb_proyecto",
        "peso_proyectado_gr",
    ]
    missing_columns = [col for col in required_columns if col not in data_df.columns]
    if missing_columns:
        raise ValueError(
            f"Faltan las siguientes columnas requeridas: "
            f"{', '.join(missing_columns)}"
        )
    min_dia = data_df[data_df["piscina"] == pool_str]["dias_proyectados"].min() - 1
    max_dia = data_df[data_df["piscina"] == pool_str]["dias_proyectados"].max() + 1
    # para el rango de dias a graficar en el eje x
    dias_values = list(range(min_dia, max_dia + 1))
    # creamos el gráfico con altair
    line_chart = (
        alt.Chart(data_df[data_df["piscina"] == pool_str])
        .mark_line(size=3, color="#884DE3")
        .encode(
            x=alt.X(
                "dias_proyectados",
                axis=alt.Axis(
                    title="Días",
                    values=dias_values,
                    titleFontSize=AXIS_FONT_SIZE,
                    labelFontSize=LABEL_FONT_SIZE,
                ),
            ),
            y=alt.Y(
                variable_str_normalizada,
                axis=alt.Axis(
                    title=variable_str,
                    titleFontSize=AXIS_FONT_SIZE,
                    labelFontSize=LABEL_FONT_SIZE,
                ),
            ),
            tooltip=[
                "dias_proyectados",
                "up_proyecto",
                "costo_lb_proyecto",
                "peso_proyectado_gr",
            ],
        )
    )
    # Agregar markers a la líneawesd
    points = line_chart.mark_point(
        size=MARK_POINT_SIZE, color=PRIMARY_COLOR, filled=True
    ).encode(x="dias_proyectados", y=variable_str_normalizada)
    chart = (line_chart + points).interactive()
    cols_plot = st.columns([1])
    with cols_plot[0]:
        st.altair_chart(chart, use_container_width=True)


def plot_rentability_graph(data_df: pd.DataFrame) -> None:
    """
    Esta ``función`` hace un plot de un gráfico de
    líneas del precio de venta del camaron, junto con el peso y costo lb
    para realizar un análisis de rentabilidad de 1 o más piscinas al
    mismo tiempo

    Args:
        data_df (Pandas dataframe): Datos de las proyecciones.
    Raises:
        ValueError: Si faltan columnas requeridas en el DataFrame.
    Returns:
        Retorna None
    """
    # Verificar la presencia de las columnas necesarias
    required_columns = [
        "piscina",
        "fecha_estimada_cosecha",
        "precio_venta_lbs_con_rendimiento",
        "costo_lb_proyecto",
        "peso_proyectado_gr",
        "up_proyecto",
    ]
    missing_columns = [col for col in required_columns if col not in data_df.columns]
    if missing_columns:
        raise ValueError(
            f"Faltan las siguientes columnas requeridas: "
            f"{', '.join(missing_columns)}"
        )
    # hacemos una copia para no hacer cambios al dataframe original
    data_plot_df = data_df.copy()
    # renombramos columnas para el grafico
    existing_columns = {
        k: v
        for k, v in PLOT_MAPPING_VARIABLES_NAME.items()
        if k in data_plot_df.columns
    }
    data_plot_df = data_plot_df.rename(columns=existing_columns)
    # filtramos primero las piscinas en el caso que haya seleccion
    if st.session_state.selected_pools:
        data_plot_df = data_plot_df[
            data_plot_df["Piscina"].isin(st.session_state.selected_pools)
        ]
    data_plot_df["Fecha Estimada Cosecha"] = pd.to_datetime(
        data_plot_df["Fecha Estimada Cosecha"]
    )
    data_plot_df = data_plot_df[data_plot_df["Fecha Estimada Cosecha"] > FECHA_ACTUAL]
    min_peso = data_plot_df["Peso (gr)"].min() - 1.0
    max_peso = data_plot_df["Peso (gr)"].max() + 1.0
    # para el rango del eje x
    peso_values = list(range(round(min_peso), round(max_peso) + 1))
    min_y = (
        min(
            data_plot_df["Costo lb/camaron"].min(),
            data_plot_df["Precio venta pesca final ($/Lb)"].min(),
        )
        - 0.1
    )
    max_y = (
        max(
            data_plot_df["Costo lb/camaron"].max(),
            data_plot_df["Precio venta pesca final ($/Lb)"].max(),
        )
        + 0.1
    )
    # para el rango del eje y
    y_values = list(np.arange(min_y, max_y + 0.1, 0.1))
    # creamos el grafico base colocando el peso en el eje x
    base_chart = alt.Chart(data_plot_df).encode(
        x=alt.X(
            "Peso (gr)",
            axis=alt.Axis(
                title="Peso (gr)",
                values=peso_values,
                titleFontSize=AXIS_FONT_SIZE,
                labelFontSize=LABEL_FONT_SIZE,
            ),
        ),
        tooltip=[
            "Piscina",
            "Fecha Estimada Cosecha",
            "Días",
            "UP($/ha/dia)",
            "Precio venta pesca final ($/Lb)",
            "Costo lb/camaron",
        ],
    )

    # Gráfico de puntos para costo
    point_chart1 = base_chart.mark_point(size=MARK_POINT_SIZE, filled=True).encode(
        y=alt.Y(
            "Costo lb/camaron",
            axis=alt.Axis(
                title="Costo lb/camaron",
                titleColor=TERTIARY_COLOR,
                titleFontSize=AXIS_FONT_SIZE,
                labelFontSize=LABEL_FONT_SIZE,
                values=y_values,
            ),
            scale=alt.Scale(domain=[min_y, max_y]),
        ),
        color=alt.Color("Piscina", legend=alt.Legend(title="Piscina")),
    )

    # Gráfico de línea para precio
    line_chart2 = base_chart.mark_line(size=LINE_SIZE, color=DARK_BLUE_COLOR).encode(
        y=alt.Y(
            "Precio venta pesca final ($/Lb)",
            axis=alt.Axis(
                # title='Precio venta pesca final ($/Lb)',
                titleColor="#0C3EE4",
                titleFontSize=AXIS_FONT_SIZE,
                labelFontSize=LABEL_FONT_SIZE,
                values=y_values,
            ),
            scale=alt.Scale(domain=[min_y, max_y]),
        ),
    )

    # Usar layer y ajustar resolve para manejar ejes independientes
    combined_chart = alt.layer(point_chart1, line_chart2).interactive(bind_y=False)

    cols_plot = st.columns([1])
    with cols_plot[0]:
        st.altair_chart(combined_chart, use_container_width=True)
