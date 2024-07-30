import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, AgGridTheme, GridUpdateMode
from streamlit_extras.stylable_container import stylable_container
import pandas as pd
from constants.general import (
    COSTO_MIX_DEFECTO,
    COSTO_MILLAR_DEFECTO,
    COSTO_FIJO_DEFECTO,
    DEFAULT_CONFIG
)
import time

# CUANDO USAMOS EL ULTIMO ALIMENTO PARA LA PROYECCION
def update_lineal_feed():
    if st.session_state.checkbox_lineal_feed:
        st.session_state.checkbox_dinamycal_feed = False

# actualizamos el checkbox cuando el usuario selecciona sobrevivencia de campo
def update_sob_campo():
    if st.session_state.checkbox_sob_campo:
        st.session_state.checkbox_sob_consumo = False
# actualizamos el checkbox cuando el usuario selecciona sobrevivencia de consumo
def update_sob_consumo():
    if st.session_state.checkbox_sob_consumo:
        st.session_state.checkbox_sob_campo = False


# CUANDO AL ULTIMO ALIMENTO LE AGREGAMOS UN PORCENTAJE
def update_dynamic_feed():
    if st.session_state.checkbox_dinamycal_feed:
        st.session_state.checkbox_lineal_feed = False


def sidebar(costo_mix_defecto, costo_fijo_defecto, costo_millar_defecto, load_capacity_default, 
            percentage_feed_default, percentage_sob_default, storage):
    st.write("# Configuración")
    st.session_state.costo_mix = st.number_input(
        "Ingrese Costo mix alimento (kg)",
        min_value=0.0,
        max_value=15.0,
        value=costo_mix_defecto,
        step=0.1,
    )
    st.session_state.costo_larva = st.number_input(
        "Ingrese Costo millar larva", min_value=0.0, max_value=30.0, value=costo_millar_defecto, step=0.1
    )
    st.session_state.costo_fijo = st.number_input(
        "Ingrese Costo Fijo ($/ha/día)",
        min_value=0.0,
        max_value=70.0,
        value=costo_fijo_defecto,
        step=0.1,
    )
    st.session_state.use_personalize_config_costos = st.checkbox(
        "Usar esta configuración de costos",
        value=st.session_state.use_personalize_config_costos
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
            update_mode=GridUpdateMode.VALUE_CHANGED,
        )
        # Guardar los cambios en el dataframe en el estado de sesión
        if grid_table["data"] is not None:
            #st.session_state.prices_selected_rows = pd.DataFrame(grid_table["data"])
            new_df = pd.DataFrame(grid_table["data"])
            if not new_df.equals(st.session_state.prices_selected_rows):
                st.session_state.prices_selected_rows = new_df
                
                #st.rerun()
        st.session_state.use_personalize_config_prices = st.checkbox(
            "Usar esta configuración de precios",
            value=st.session_state.use_personalize_config_prices
        )

    st.write("#### Capacidad de carga:")
    st.session_state.load_capacity = st.number_input(
        "Ingrese Capacidad de carga (Lb/ha)",
        min_value=0.0,
        max_value=15000.0,
        value=load_capacity_default,
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
        "Ingrese el porcentaje de aumento de alimento: ", 0, 30, percentage_feed_default
    )
    st.write("Aumento del", st.session_state.percentage_dynamical_feed, "%")
    st.write("#### Sobrevivencia:")
    st.checkbox(
        "Usar sobreviencia campo",
        key="checkbox_sob_campo",
        on_change=update_sob_campo,
    )
    st.checkbox(
        "Usar sobreviencia consumo",
        key="checkbox_sob_consumo",
        on_change=update_sob_consumo,
    )
    st.session_state.percentage_dynamical_sob = st.slider(
        "Ingrese un porcentaje de aumento\disminución de la sob: ", -10, 10, percentage_sob_default
    )


    with stylable_container(
            key="container_with_border_button_save_config",
            css_styles=r"""
                    button p:before {
                        font-family: 'Font Awesome 5 Free';
                        content: '\f0c7';
                        display: inline-block;
                        padding-right: 3px;
                        padding-left: 3px;
                        vertical-align: middle;
                        font-weight: 900;
                    }
                    """,
        ):
            save_button = st.button("Guardar esta configuración")
            if save_button:
                 new_config = {
                    "prices": st.session_state.prices_selected_rows.to_dict(orient='list'),
                    "DIAS_PROYECTO_DEFECTO": st.session_state.dias_proyecto,
                    "SOB_PROYECTO_DEFECTO": st.session_state.sob_proyecto,
                    "PESO_PROYECTO_DEFECTO": st.session_state.peso_proyecto,
                    "COSTO_MILLAR_DEFECTO": st.session_state.costo_larva,
                    "COSTO_MIX_DEFECTO": st.session_state.costo_mix,
                    "COSTO_FIJO_DEFECTO": st.session_state.costo_fijo,
                    "load_capacity": st.session_state.load_capacity,
                    "is_using_lineal_feed": st.session_state.checkbox_lineal_feed,
                    "percentage_dynamical_feed": st.session_state.percentage_dynamical_feed,
                    "is_using_sob_campo": st.session_state.checkbox_sob_campo,
                    "percentage_dynamical_sob": st.session_state.percentage_dynamical_sob,
                    "use_personalize_config_costos": st.session_state.use_personalize_config_costos,
                    "use_personalize_config_prices": st.session_state.use_personalize_config_prices
                }
                 storage.setItem("config", new_config)
                 st.success("¡Configuración guardada!")
    with stylable_container(
            key="container_with_border_button_delete_config",
            css_styles=r"""
                    button p:before {
                        font-family: 'Font Awesome 5 Free';
                        content: '\f2ed';
                        display: inline-block;
                        padding-right: 3px;
                        padding-left: 3px;
                        vertical-align: middle;
                        font-weight: 900;
                    }
                    """,
        ):
            reset_button = st.button("Volver a configuración por defecto")
            if reset_button:
                with st.spinner('Procesando...'):
                    storage.deleteAll()
                    st.success("¡Configuración restablecida por favor vuelve a actualizar la aplicación.")