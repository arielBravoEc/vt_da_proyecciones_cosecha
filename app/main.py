import streamlit as st
from constants.general import BACKGROUND_COLOR, CARD_CSS,CARD_CSS_V2, container_css,PRIMARY_COLOR,PRIMARY_COLOR_BACKGROUND,DIAS_PROYECTO_DEFECTO,SOB_PROYECTO_DEFECTO
from utils.proyection_helpers import get_projections
from utils.data_integration_helper import get_last
from utils.data_generation_helper import export_df_to_pdf, export_df_to_pdfv2
from components.linechart_component import plot_line_chart
from catalog.projections_catalog import get_excel_data
from components.button_component import get_button_with_icon
from components.table_component import plot_table_with_filters_and_sort, plot_table_groupped, plot_table_prices
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.chart_container import chart_container
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, AgGridTheme, GridUpdateMode
from streamlit_modal import Modal
import time



st.set_page_config(layout="wide", initial_sidebar_state=st.session_state.setdefault("sidebar_state","collapsed"),)
# Usamos st.markdown para inyectar el CSS 
st.markdown(BACKGROUND_COLOR, unsafe_allow_html=True)

# Inicializar estado de la aplicación
if 'data' not in st.session_state:
    st.session_state.data = None
if 'prices_data' not in st.session_state:
    st.session_state.prices_data = None
if 'pool_selection' not in st.session_state:
    st.session_state.pool_selection = None
if 'costo_larva' not in st.session_state:
    st.session_state.costo_larva = None
if 'costo_mix' not in st.session_state:
    st.session_state.costo_mix = None
if 'costo_fijo' not in st.session_state:
    st.session_state.costo_fijo = None
if 'use_personalize_config_costos' not in st.session_state:
    st.session_state.use_personalize_config_costos = None
if 'use_personalize_config_prices' not in st.session_state:
    st.session_state.use_personalize_config_prices = None
if 'variable_selection' not in st.session_state:
    st.session_state.variable_selection = None
# Ensure selected_rows key exists in session state
if 'selected_rows' not in st.session_state:
    st.session_state.selected_rows = []
if 'prices_selected_rows' not in st.session_state:
    st.session_state.prices_selected_rows = get_excel_data( sheet_name='precios')
# Inicializar la variable de estado para controlar la visibilidad del panel lateral
if 'show_sidebar' not in st.session_state:
    st.session_state.show_sidebar = False

st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"/>',
    unsafe_allow_html=True,
)

if(st.session_state.get("flag")):
    st.session_state.sidebar_state = st.session_state.flag
    del st.session_state.flag # or you could do => st.session_state.flag = False
    time.sleep(0.01)
    st.rerun()

def set_sidebar_state(value):
    if(st.session_state.sidebar_state == value):
        st.session_state.flag = value
        st.session_state.sidebar_state = "expanded" if value == "collapsed" else "collapsed"
    else:
        st.session_state.sidebar_state = value
    st.rerun()

@st.experimental_fragment
def get_btn():
    #if st.button(label="Cerrar Panel", key="buttonn"):
    #    set_sidebar_state("collapsed")
    st.title("Configuración")
    st.session_state.costo_mix = st.number_input("Ingrese Costo mix alimento (kg)", min_value=0.0, max_value=15.0, value=1.2, step=0.1)
    st.session_state.costo_larva = st.number_input("Ingrese Costo millar larva", min_value=0.0, max_value=15.0, value=1.2, step=0.1)
    st.session_state.costo_fijo = st.number_input("Ingrese Costo Fijo ($/ha/día)", min_value=0.0, max_value=70.0, value=30.0, step=0.1)
    st.session_state.use_personalize_config_costos = st.checkbox("Usar esta configuración de costos")
     # Verificar si los datos están en session_state
    #st.session_state.prices_data = get_excel_data( sheet_name='precios')
    #st.session_state.prices_selected_rows = get_excel_data( sheet_name='precios')

    if st.session_state.prices_selected_rows is not None: 
        #plot_table_prices(st.session_state.prices_selected_rows, 'prices_selected_rows')
        # Crea un GridOptionsBuilder
        #data_prices = st.session_state.prices_selected_rows  
        #data_prices_df = data_prices.copy()
        gb = GridOptionsBuilder.from_dataframe(st.session_state.prices_selected_rows)
        gb.configure_pagination(paginationAutoPageSize=False, enabled=False)  # Habilita la paginación
        gb.configure_default_column(filter=True, sortable=True)  # Habilita el filtrado y la ordenación en cada columna
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
                width='100%',  # Especifica el ancho en píxeles o porcentaje
                update_mode=GridUpdateMode.MODEL_CHANGED,

            )
        # Guardar los cambios en el dataframe en el estado de sesión
        if grid_table['data'] is not None:
            st.session_state.prices_selected_rows = pd.DataFrame(grid_table['data'])
        st.session_state.use_personalize_config_prices = st.checkbox("Usar esta configuración de precios")
with st.sidebar:
    get_btn()
#st.write(st.session_state)





# Initialize the modal
modal = Modal(key="example_modal", title="Cosechas Seleccionadas", max_width=1200)




st.title("Proyecciones de cosechas")
st.text("La herramienta ofrece valiosas estimaciones para guiar sus decisiones, pero es esencial considerarla como una recomendación, \nya que factores externos pueden influir en los resultados.")

st.markdown(container_css, unsafe_allow_html=True)


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
        with cols_button[2]:
             if(st.button("Personalizar proyección")):
                set_sidebar_state("expanded")
        with cols_button[0]:
            st.text("Configuración Inicial" )
        col1, col2, col3 = st.columns(3)
        with col1:
            farm_selection = st.selectbox(
             "Seleccione el campo",
             ("CAMARONES NATURISA", "CAMINO REAL", "MARCHENA"))
            range_days = st.number_input("Seleccione Rango Proyecto", min_value=0, max_value=90, value=21, step=1)
        with col2:
            sob = st.number_input("Seleccione Sobrevivencia Proyecto", min_value=0.0, max_value=1.0, value=SOB_PROYECTO_DEFECTO, step=0.05)
            # Botón para controlar la apertura/cierre del panel
            show_panel = False
            # Crear un botón en la barra lateral
            
        with col3:
            duration = st.number_input("Seleccione Días Proyecto", min_value=0, max_value=100, value=DIAS_PROYECTO_DEFECTO, step=1)
       
            
            
        #a = st.line_chart({'data': [1, 2, 3, 4, 5]},  use_container_width=True)
        #st.button('Procesar y Mostrar Datos')
        

col_button_proy, col_button_selection = st.columns([0.5,0.5])
 # Verificar si los datos están en session_state



   

with col_button_proy:
    with stylable_container(
    key="container_with_border",
    css_styles=f"""
        button p:before {{
            font-family: 'Font Awesome 5 Free';
            content: '\f133';
            display: inline-block;
            padding-right: 3px;
            padding-left: 3px;
            vertical-align: middle;
            font-weight: 900;
        }}
        """
    ):
        a = st.button('Generar Proyecciones')
        if a:

                with st.spinner('Generando proyección, por favor espere unos segundos.'):
                    #data = get_projections(farm_name=farm_selection,project_duration=duration, project_survival=sob, project_range=range_days)
                    flag_use_cost = False
                    flag_use_prices = False
                    if st.session_state.use_personalize_config_costos:
                        flag_use_cost = True
                    if st.session_state.use_personalize_config_prices:
                        flag_use_prices = True
                        
                    st.session_state.data = get_projections(farm_name=farm_selection,project_duration=duration, project_survival=sob, project_range=range_days,
                    is_using_personalized_cost = flag_use_cost,
                    is_using_personalized_price = flag_use_prices,
                    prices_table = st.session_state.prices_selected_rows,
                    cost_info = {
                        "mix": st.session_state.costo_mix,
                        "millar": st.session_state.costo_larva,
                        "fijo": st.session_state.costo_fijo,
                    }
                    )
        
        
 # Verificar si los datos están en session_state
if st.session_state.data is not None: 
    

    data = st.session_state.data  
    data_proyecciones = data.copy()    
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

        st.write("DATOS REALES")
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
        st.write("PROYECCIONES")
    
        data_proyecciones.rename(columns=
            {"campo": "Campo",
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
             "precio_venta_pesca": "Precio venta pesca final ($/Kg)"
             }
        , inplace=True)
        data_v2 = data_proyecciones[[ "Campo","Piscina", "Fecha Estimada Cosecha",
                           "Días","Peso (gr)","Biomasa (lb/ha)","Sobrevivencia final",
                           "FCA","Costo lb/camaron","UP($/ha/dia)","ROI(%)",
                           "Precio venta pesca final ($/Kg)","tipo_proyeccion", "aguaje",]].round(2)

        plot_table_with_filters_and_sort(data_v2, 'selected_rows')
             
    if st.session_state.data is not None: 
            if st.button("Abrir Selección"):
                modal.open()

            # Display the modal
            if modal.is_open():
                with modal.container():
                    with stylable_container(
                    key="container_with_border_button",
                    css_styles=r"""
                        button p:before {
                            font-family: 'Font Awesome 5 Free';
                            content: '\f6ad';
                            display: inline-block; 
                            padding-right: 3px;
                            padding-left: 3px;
                            vertical-align: middle;
                            font-weight: 900;
                        }
                        """,
                    ):
                        st.dataframe(st.session_state.selected_rows)   
                        # Crear un botón para exportar el DataFrame a PDF
                        #if st.button('Exportar a PDF'):
                            #export_df_to_pdf(st.session_state.selected_rows, 'proyecciones.pdf')
                        st.markdown(export_df_to_pdfv2(st.session_state.selected_rows, 'dataframe.pdf'), unsafe_allow_html=True)


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
    unsafe_allow_html=True
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
           st.session_state.pool_selection = st.selectbox(
             "Piscina",
             pools)
        with col2:
            st.session_state.variable_selection = st.selectbox(
             "Variable a analizar",
             ("Costo lb/camaron","UP($/ha/dia)", "ROI(%)", "Precio venta pesca final ($/Kg)"))
        plot_line_chart(data_proyecciones, st.session_state.variable_selection)
            