import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, AgGridTheme, GridUpdateMode
import pandas as pd


# CUANDO USAMOS EL ULTIMO ALIMENTO PARA LA PROYECCION
def update_lineal_feed():
    if st.session_state.checkbox_lineal_feed:
        st.session_state.checkbox_dinamycal_feed = False


# CUANDO AL ULTIMO ALIMENTO LE AGREGAMOS UN PORCENTAJE
def update_dynamic_feed():
    if st.session_state.checkbox_dinamycal_feed:
        st.session_state.checkbox_lineal_feed = False


def sidebar():
    st.write("# Configuración")
    st.session_state.costo_mix = st.number_input(
        "Ingrese Costo mix alimento (kg)",
        min_value=0.0,
        max_value=15.0,
        value=1.2,
        step=0.1,
    )
    st.session_state.costo_larva = st.number_input(
        "Ingrese Costo millar larva", min_value=0.0, max_value=15.0, value=1.2, step=0.1
    )
    st.session_state.costo_fijo = st.number_input(
        "Ingrese Costo Fijo ($/ha/día)",
        min_value=0.0,
        max_value=70.0,
        value=30.0,
        step=0.1,
    )
    st.session_state.use_personalize_config_costos = st.checkbox(
        "Usar esta configuración de costos"
    )

    if st.session_state.prices_selected_rows is not None:
        # si existen filas seleccionadas
        gb = GridOptionsBuilder.from_dataframe(st.session_state.prices_selected_rows)
        gb.configure_pagination(
            paginationAutoPageSize=False, enabled=False
        )  # Habilita la paginación
        gb.configure_default_column(
            filter=True, sortable=True
        )  # Habilita el filtrado y la ordenación en cada columna
        gb.configure_column("Precios", editable=True, maxWidth=180)
        gb.configure_column("Tallas", editable=False, maxWidth=280)
        gridOptions = gb.build()
        grid_table = AgGrid(
            st.session_state.prices_selected_rows,
            gridOptions=gridOptions,
            enable_enterprise_modules=True,
            allow_unsafe_jscode=True,  # Esta opción permite usar JavaScript no seguro
            theme=AgGridTheme.STREAMLIT,  # Cambia el tema si lo deseas
            height=300,
            width="100%",  # Especifica el ancho en píxeles o porcentaje
            update_mode=GridUpdateMode.MODEL_CHANGED,
        )
        # Guardar los cambios en el dataframe en el estado de sesión
        if grid_table["data"] is not None:
            st.session_state.prices_selected_rows = pd.DataFrame(grid_table["data"])
        st.session_state.use_personalize_config_prices = st.checkbox(
            "Usar esta configuración de precios"
        )

    st.write("#### Capacidad de carga:")
    st.session_state.load_capacity = st.number_input(
        "Ingrese Capacidad de carga (Lb/ha)",
        min_value=0.0,
        max_value=15000.0,
        value=0.0,
        step=500.0,
    )
    st.session_state.use_personalize_load_capacity = st.checkbox(
        "Usar esta configuración de capacidad de carga"
    )
    st.write("#### Proyección de alimento:")
    # Crear los checkboxes
    st.checkbox(
        "Usar alimentación lineal",
        key="checkbox_lineal_feed",
        on_change=update_lineal_feed,
    )
    st.checkbox(
        "Usar alimentación con aumento porcentual semanal",
        key="checkbox_dinamycal_feed",
        on_change=update_dynamic_feed,
    )
    st.session_state.percentage_dynamical_feed = st.slider(
        "Ingrese el porcentaje de aumento de alimento: ", 0, 30, 5
    )
    st.write("Aumento del", st.session_state.percentage_dynamical_feed, "%")
