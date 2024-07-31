import streamlit as st
import pandas as  pd
import json
from constants.general import (
    DIAS_PROYECTO_DEFECTO,
    SOB_PROYECTO_DEFECTO,
    FARMS,
    PESO_PROYECTO_DEFECTO,
)
from constants.css_constants import (
    BACKGROUND_COLOR,
    CONTAINER_CSS,
)

from constants.general import (
    COSTO_MIX_DEFECTO,
    COSTO_MILLAR_DEFECTO,
    COSTO_FIJO_DEFECTO
)
from utils.proyection_helpers import get_projections
from utils.data_generation_helper import create_sob_and_ind_in_column
from components.linechart_component import plot_line_chart,plot_line_chart_with_two_axis,plot_line_chart_with_two_axis_v2
from components.side_bar_component import sidebar
from catalog.projections_catalog import get_excel_data
from components.modal_component import show_modal
from components.table_component import (
    plot_table_with_filters_and_sort,
    plot_table_groupped,
)
from streamlit_extras.stylable_container import stylable_container
from streamlit_modal import Modal

import warnings
import numpy as np
## local storage
from streamlit_local_storage import LocalStorage

st.set_page_config(
    layout="wide",
    initial_sidebar_state=st.session_state.setdefault("sidebar_state", "collapsed"),
)
# inicializamos el almacenamiento local
storage = LocalStorage()
all_config  = storage.getAll()
print(all_config)
with st.spinner('Cargando datos precios...'):
    precios_df = get_excel_data(sheet_name="precios")
# configuraciones por defecto
default_config = {
    "prices": precios_df.to_dict(orient='list'),
    "DIAS_PROYECTO_DEFECTO": DIAS_PROYECTO_DEFECTO,
    "SOB_PROYECTO_DEFECTO": SOB_PROYECTO_DEFECTO,
    "PESO_PROYECTO_DEFECTO": PESO_PROYECTO_DEFECTO,
    "COSTO_MILLAR_DEFECTO": COSTO_MILLAR_DEFECTO,
    "COSTO_MIX_DEFECTO": COSTO_MIX_DEFECTO,
    "COSTO_FIJO_DEFECTO": COSTO_FIJO_DEFECTO,
    "load_capacity": 0.0,
    "is_using_lineal_feed": True,
    "percentage_dynamical_feed": 5,
    "is_using_sob_campo": True,
    "percentage_dynamical_sob": 0,
    "use_personalize_config_costos": False,
    "use_personalize_config_prices": False
}


# Cargar las configuraciones guardadas o usarlas por defecto
# Función para cargar las configuraciones guardadas o usar por defecto
def load_config():
    #try:
        print(type(storage.getItem("config")))
        #stored_config = storage.getItem("config") or {}
        if type(storage.getItem("config")) is  type(None):
            print("aaaaa")
            print(default_config['prices'])
            return default_config
        else:
            print("bbbb")
            stored_config = storage.getItem("config") or {}
            return stored_config
    #except TypeError as e:
    #    print(f"Error al obtener el ítem: {e}")
    #    return default_config

# Cargar configuraciones guardadas o usar por defecto
config = load_config()
st.session_state.load_config =config 

# Suprimir FutureWarnings
warnings.simplefilter(action='ignore', category=FutureWarning)


# Usamos st.markdown para inyectar el CSS
st.markdown(BACKGROUND_COLOR, unsafe_allow_html=True)

if st.session_state.load_config:

    # cargamos los precios por defecto
    if "prices_selected_rows" not in st.session_state:
        st.session_state.prices_selected_rows = pd.DataFrame.from_dict(config['prices'])

    if 'load_config' not in st.session_state:
        st.session_state.load_config = None
    # Inicializar estado de la aplicación
    if "data" not in st.session_state:
        st.session_state.data = None
    if "prices_data" not in st.session_state:
        st.session_state.prices_data = None
    if "pool_selection" not in st.session_state:
        st.session_state.pool_selection = None
    if "costo_larva" not in st.session_state:
        st.session_state.costo_larva = None
    if "costo_mix" not in st.session_state:
        st.session_state.costo_mix = None
    if "costo_fijo" not in st.session_state:
        st.session_state.costo_fijo = None
    if "use_personalize_config_costos" not in st.session_state:
        st.session_state.use_personalize_config_costos = config['use_personalize_config_costos']
    if "use_personalize_config_prices" not in st.session_state:
        st.session_state.use_personalize_config_prices = config['use_personalize_config_prices']
    if "variable_selection" not in st.session_state:
        st.session_state.variable_selection = None
        # para el seungo grafico de lineas
    if "variable_selection_plot_1" not in st.session_state:
        st.session_state.variable_selection_plot_1 = None
    if "variable_selection_plot_2" not in st.session_state:
        st.session_state.variable_selection_plot_2 = None
    # Ensure selected_rows key exists in session state
    if "selected_rows" not in st.session_state:
        st.session_state.selected_rows = []

    # Inicializar la variable de estado para controlar la visibilidad del panel lateral
    if "show_sidebar" not in st.session_state:
        st.session_state.show_sidebar = False
    if "use_personalize_load_capacity" not in st.session_state:
        st.session_state.use_personalize_load_capacity = None
    if "load_capacity" not in st.session_state:
        st.session_state.load_capacity = None
    if "checkbox_lineal_feed" not in st.session_state:
        st.session_state.checkbox_lineal_feed = config['is_using_lineal_feed']
    if "checkbox_dinamycal_feed" not in st.session_state:
        st.session_state.checkbox_dinamycal_feed = not config['is_using_lineal_feed'] 
    if "percentage_dynamical_feed" not in st.session_state:
        st.session_state.percentage_dynamical_feed = config['percentage_dynamical_feed']
    # SOBREVIVENCIA
    if "checkbox_sob_campo" not in st.session_state:
        st.session_state.checkbox_sob_campo = config['is_using_sob_campo']  
    if "checkbox_sob_consumo" not in st.session_state:
        st.session_state.checkbox_sob_consumo = not config['is_using_sob_campo']
    if "percentage_dynamical_sob" not in st.session_state:
        st.session_state.percentage_dynamical_sob = config['percentage_dynamical_sob']
    #variables de conf de pesos, sob
    if "peso_proyecto" not in st.session_state:
        st.session_state.peso_proyecto = None
    if "sob_proyecto" not in st.session_state:
        st.session_state.sob_proyecto = None
    if "dias_proyecto" not in st.session_state:
        st.session_state.dias_proyecto = None



    # PARA PODER USAR ICONOS DE FONT AWESOME
    st.markdown(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"/>',
        unsafe_allow_html=True,
    )





    # creamos la funcionalidad del sidebar de configuraciones
    #@st.experimental_fragment
    def get_sidebar():
        sidebar(float(config['COSTO_MIX_DEFECTO']), 
                float(config['COSTO_FIJO_DEFECTO']), 
                float(config['COSTO_MILLAR_DEFECTO']), 
                float(config['load_capacity']),
                config['percentage_dynamical_feed'],
                config['percentage_dynamical_sob'],
                storage
                )


    with st.sidebar:
        get_sidebar()


    # Iniciamos el modal
    modal = Modal(key="example_modal", title="Cosechas Seleccionadas", max_width=1200)


    st.title("Proyecciones de cosechas")
    st.write(
        "La herramienta ofrece valiosas estimaciones para guiar sus decisiones, pero es esencial"
        + " considerarla como una recomendación, ya que hay factores externos que pueden influir en los resultados."
    )


    st.markdown(CONTAINER_CSS, unsafe_allow_html=True)


    with stylable_container(
        key="container_with_borderv0",
        css_styles="""
                {
                    background-color: white;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    transition: transform 0.2s;
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    border-radius: 10px;
                    padding: calc(1em - 1px)
                }
                """,
    ):
        cols_button = st.columns(3)
        #with cols_button[2]:
        #    if st.button("Personalizar proyección"):
        #        set_sidebar_state("expanded")
        with cols_button[0]:
            st.write("##### CONFIGURACION INICIAL")
            # st.text("Configuración Inicial" )
        col1, col2, col3 = st.columns(3)
        with col1:
            farm_selection = st.selectbox("Seleccione el campo", FARMS)
            st.session_state.peso_proyecto = st.number_input(
                "Seleccione Peso Proyecto",
                min_value=0.0,
                max_value=60.0,
                value=float(config['PESO_PROYECTO_DEFECTO']),
                step=1.0,
            )
        with col2:
            st.session_state.sob_proyecto = st.number_input(
                "Seleccione Sobrevivencia Proyecto",
                min_value=0.0,
                max_value=1.0,
                value=float(config['SOB_PROYECTO_DEFECTO']),
                step=0.05,
            )
            # Botón para controlar la apertura/cierre del panel
            range_days = st.number_input(
                "Seleccione Rango Proyecto", min_value=0, max_value=90, value=21, step=1
            )

        with col3:
            st.session_state.dias_proyecto = st.number_input(
                "Seleccione Días Proyecto",
                min_value=0,
                max_value=100,
                value=config['DIAS_PROYECTO_DEFECTO'],
                step=1,
            )

        # a = st.line_chart({'data': [1, 2, 3, 4, 5]},  use_container_width=True)
        # st.button('Procesar y Mostrar Datos')


    col_button_proy, col_button_selection = st.columns([0.5, 0.5])
    # Verificar si los datos están en session_state


    with col_button_proy:
        with stylable_container(
            key="container_with_border",
            css_styles="""
            button p:before {{
                font-family: 'Font Awesome 5 Free';
                content: '\f1c1';
                display: inline-block;
                padding-right: 3px;
                padding-left: 3px;
                vertical-align: middle;
                font-weight: 900;
            }}
            """,
        ):
            with stylable_container(
                key="container_with_border_button_proyection",
                css_styles=r"""
                        button p:before {
                            font-family: 'Font Awesome 5 Free';
                            content: '\f073';
                            display: inline-block;
                            padding-right: 3px;
                            padding-left: 3px;
                            vertical-align: middle;
                            font-weight: 900;
                        }
                        """,
            ):
                a = st.button("Generar Proyecciones")
                if a:

                    with st.spinner(
                        "Generando proyección, por favor espere unos segundos."
                    ):
                        flag_use_cost = False
                        flag_use_prices = False
                        flag_use_load_capacity = False
                        if st.session_state.use_personalize_config_costos:
                            flag_use_cost = True
                        if st.session_state.use_personalize_config_prices:
                            flag_use_prices = True
                        if st.session_state.use_personalize_load_capacity:
                            flag_use_load_capacity = True

                        st.session_state.data = get_projections(
                            farm_name=farm_selection,
                            project_duration=st.session_state.dias_proyecto,
                            project_survival=st.session_state.sob_proyecto,
                            project_range=range_days,
                            is_using_personalized_cost=flag_use_cost,
                            is_using_personalized_price=flag_use_prices,
                            prices_table=st.session_state.prices_selected_rows,
                            cost_info={
                                "mix": st.session_state.costo_mix,
                                "millar": st.session_state.costo_larva,
                                "fijo": st.session_state.costo_fijo,
                            },
                            is_using_personalized_load_capacity=flag_use_load_capacity,
                            load_capacity=st.session_state.load_capacity,
                            is_using_lineal_feed=st.session_state.checkbox_lineal_feed,
                            percentage_dynamical_feed=st.session_state.percentage_dynamical_feed,
                            is_using_sob_campo = st.session_state.checkbox_sob_campo,
                            percentage_sob =st.session_state.percentage_dynamical_sob,
                        )


    # Verificar si los datos están en session_state
    if st.session_state.data is not None:

        data = st.session_state.data
        data_proyecciones = data.copy()
        if len(data_proyecciones) > 0:
            with stylable_container(
                key="container_with_borderv3",
                css_styles="""
                        {
                            background-color: white;
                            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                            transition: transform 0.2s;
                            border: 1px solid rgba(49, 51, 63, 0.2);
                            border-radius: 10px;
                            padding: calc(1em - 1px);
                            max-width: 100%; /* Ajustar el ancho máximo al 100% del contenedor padre */
                            max-height: 350px; /* Ajustar la altura máxima según sea necesario */
                            overflow: hidden; /* Ocultar cualquier desbordamiento inicial */
                            overflow-y: auto; /* Permitir desplazamiento vertical */
                            display: flex; /* Usar flexbox para manejar mejor el contenido */
                            flex-direction: column; /* Alinear elementos en columna */
                        }
                        """,
            ):

                st.write("##### DATOS REALES")
                data_grouped = data.copy()
                plot_table_groupped(data_grouped)
            with stylable_container(
                key="container_with_borderv5",
                css_styles="""
                    {
                        background-color: white !important;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                        transition: transform 0.2s;
                        border: 1px solid rgba(49, 51, 63, 0.2);
                        border-radius: 10px;
                        padding: calc(1em - 1px);
                        max-width: 100%; /* Ajustar el ancho máximo al 100% del contenedor padre */
                        max-height: 600px; /* Ajustar la altura máxima según sea necesario */
                        overflow: hidden; /* Ocultar cualquier desbordamiento inicial */
                        overflow-y: auto; /* Permitir desplazamiento vertical */
                        display: flex; /* Usar flexbox para manejar mejor el contenido */
                        flex-direction: column; /* Alinear elementos en columna */
                    }
                        """,
            ):
                st.write("##### PROYECCIONES")

                data_proyecciones.rename(
                    columns={
                        "campo": "Campo",
                        "piscina": "Piscina",
                        "fecha_estimada_cosecha": "Fecha Estimada Cosecha",
                        "dias": "Días",
                        "peso": "Peso (gr)",
                        "biomasa": "Biomasa (lb/ha)",
                        "sobrevivencia": "Sobrevivencia final",
                        "fca": "FCA",
                        "costo": "Costo lb/camaron",
                        "up": "UP($/ha/dia)",
                        "roi": "ROI(%)",
                        "precio_venta_pesca": "Precio venta pesca final ($/Kg)",
                        "biomasa_total": "Biomasa Total (LB)",
                    },
                    inplace=True,
                )
                data_proyecciones['densidad_actual'] = (data_proyecciones['Sobrevivencia final']/100)*data_proyecciones['densidad_siembra']
                data_proyecciones['Sobrevivencia final'] = np.vectorize(create_sob_and_ind_in_column)(data_proyecciones['Sobrevivencia final'], data_proyecciones['densidad_actual'])
                data_v2 = data_proyecciones[
                    [
                        "Campo",
                        "Piscina",
                        "ha",
                        "Fecha Estimada Cosecha",
                        "Días",
                        "Peso (gr)",
                        "Biomasa (lb/ha)",
                        "Biomasa Total (LB)",
                        "Sobrevivencia final",
                        "FCA",
                        "Costo lb/camaron",
                        "UP($/ha/dia)",
                        "ROI(%)",
                        "Precio venta pesca final ($/Kg)",
                        "tipo_proyeccion",
                        "aguaje",
                        "capacidad_de_carga_lbs_ha",
                    ]
                ].round(2)

                plot_table_with_filters_and_sort(
                    data_v2, "selected_rows", st.session_state.peso_proyecto
                )

            if st.session_state.data is not None:
                with stylable_container(
                    key="container_with_border_button_seleccion",
                    css_styles=r"""
                            button p:before {
                                font-family: 'Font Awesome 5 Free';
                                content: '\f07c';
                                display: inline-block;
                                padding-right: 3px;
                                padding-left: 3px;
                                vertical-align: middle;
                                font-weight: 900;
                            }
                            """,
                ):
                    if st.button("Abrir Selección"):
                        modal.open()

                # mostramos el modal en caso de que se haga click en abrir
                if modal.is_open():
                    with modal.container():
                        show_modal()

            st.markdown(
                """
            <style>
            .reportview-container .main .block-container{
                max-width: 80%;215
                padding-top: 5rem;
                padding-right: 5rem;
                padding-left: 5rem;
                padding-bottom: 5rem;
            }
            </style>
            """,
                unsafe_allow_html=True,
            )

            with stylable_container(
                key="container_with_borderv2",
                css_styles="""
                    {
                        background-color: white;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                        transition: transform 0.2s;
                        border: 1px solid rgba(49, 51, 63, 0.2);
                        border-radius: 10px;
                        padding: calc(1em - 1px);
                        max-width: 100%; /* Ajustar el ancho máximo al 100% del contenedor padre */
                        max-height: 600px; /* Ajustar la altura máxima según sea necesario */
                        overflow: hidden; /* Ocultar cualquier desbordamiento inicial */
                        overflow-y: auto; /* Permitir desplazamiento vertical */
                        display: flex; /* Usar flexbox para manejar mejor el contenido */
                        flex-direction: column; /* Alinear elementos en columna */
                    }
                    """,
            ):
                col1, col2 = st.columns(2)
                pools = tuple(data_proyecciones["Piscina"].unique())
                with col1:
                    st.session_state.pool_selection = st.selectbox("Piscina", pools)
                with col2:
                    st.session_state.variable_selection = st.selectbox(
                        "Variable a analizar",
                        (
                            "UP($/ha/dia)",
                            "Peso (gr)",
                            "Costo lb/camaron",
                        
                            "Precio venta pesca final ($/Kg)",
                        ),
                    )
                plot_line_chart(data_proyecciones, st.session_state.variable_selection)
            with stylable_container(
                key="container_with_borderv2",
                css_styles="""
                    {
                        background-color: white;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                        transition: transform 0.2s;
                        border: 1px solid rgba(49, 51, 63, 0.2);
                        border-radius: 10px;
                        padding: calc(1em - 1px);
                        max-width: 100%; /* Ajustar el ancho máximo al 100% del contenedor padre */
                        max-height: 600px; /* Ajustar la altura máxima según sea necesario */
                        overflow: hidden; /* Ocultar cualquier desbordamiento inicial */
                        overflow-y: auto; /* Permitir desplazamiento vertical */
                        display: flex; /* Usar flexbox para manejar mejor el contenido */
                        flex-direction: column; /* Alinear elementos en columna */
                    }
                    """,
            ):
                cols_plot = st.columns(3)
                pools = tuple(data_proyecciones["Piscina"].unique())
                with cols_plot[0]:
                    st.session_state.pool_selection = st.selectbox("Piscina:", pools)
                with cols_plot[1]:
                    st.session_state.variable_selection_plot_1 = st.selectbox(
                        "Variable #1 a analizar",
                        (
                            "Peso (gr)",
                            "Costo lb/camaron",
                            "UP($/ha/dia)",
                            "Precio venta pesca final ($/Kg)",
                        ),
                    )
                with cols_plot[2]:
                    st.session_state.variable_selection_plot_2 = st.selectbox(
                        "Variable #2 a analizar",
                        (
                            "UP($/ha/dia)",
                            "Peso (gr)",
                            "Costo lb/camaron",
                            "Precio venta pesca final ($/Kg)",
                        ),
                    )
                plot_line_chart_with_two_axis_v2(data_proyecciones, st.session_state.variable_selection_plot_1, st.session_state.variable_selection_plot_2)
        else:
            #no hay datos
            st.warning('Para este campo no existen datos de piscinas actualizadas en los últimos 30 días.', icon="⚠️")