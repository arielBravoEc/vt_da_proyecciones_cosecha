from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, AgGridTheme,GridUpdateMode, DataReturnMode
from constants.general import  TABLE_STYLE
import streamlit as st
import pandas as pd
from utils.data_integration_helper import get_last

def plot_table_with_filters_and_sort(data_df, state_key):
    
    # Código JavaScript para aplicar estilos condicionales a toda la fila
    row_style_jscode = JsCode("""
    function(params) {
        if (params.data.tipo_proyeccion == 'fecha estimada de cosecha' && params.data.aguaje != 1) {
            return { 'color': '#884de3', 'fontWeight': 'bold' };
        } else if (params.data.aguaje == 1 && params.data.tipo_proyeccion != 'fecha estimada de cosecha') {
            return { 'backgroundColor': '#d3d3d3' };
        } else if (params.data.aguaje == 1 && params.data.tipo_proyeccion == 'fecha estimada de cosecha') {
            return { 'backgroundColor': '#d3d3d3', 'fontWeight': 'bold','color': '#884de3' };
        
        } else {
            return { 'color': 'black' };
        }
    }
    """)
    checkbox_event_jscode = JsCode("""
        function(params) {
            var selectedRows = params.api.getSelectedRows();
            if (selectedRows.length > 0) {
                var selectedRowData = selectedRows.map(row => row.data);
                Streamlit.setComponentValue(selectedRowData);
            }
    }
    """)
    data_df['IsMax'] =  data_df.groupby('Piscina')['ROI(%)'].transform(lambda x: x == x.max())
    data_df['IsMax_Up'] =  data_df.groupby('Piscina')['UP($/ha/dia)'].transform(lambda x: x == x.max())

    # Definir la función de JavaScript para resaltar la celda con el valor máximo
    cellstyle_jscode_roi = JsCode("""
    function(params) {
        if (params.data.IsMax) {
            return {'backgroundColor': 'lightgreen', 'color': 'black'};
        } else {
            return null;
        }
    }
    """)
    cellstyle_jscode_up = JsCode("""
    function(params) {
        if (params.data.IsMax_Up) {
            return {'backgroundColor': 'lightgreen', 'color': 'black'};
        } else {
            return null;
        }
    }
    """)
    # Crea un GridOptionsBuilder
    gb = GridOptionsBuilder.from_dataframe(data_df)
    # configuramos ancho de columnas
    gb.configure_column("Campo", header_name="CAMPO", maxWidth=181)
    gb.configure_column("Piscina", header_name="PS", maxWidth=55)
    gb.configure_column("Fecha Estimada Cosecha", header_name="FECHA ESTIMADA COSECHA", maxWidth=132, wrapHeaderText=True, autoHeaderHeight=True)
    gb.configure_column("Días", header_name="DIAS", maxWidth=65, wrapHeaderText=True, autoHeaderHeight=True)
    gb.configure_column("Peso (gr)", header_name="PESO (GR)", maxWidth=70, wrapHeaderText=True, autoHeaderHeight=True)
    gb.configure_column("Biomasa (lb/ha)", header_name="BIOMASA (LB/HA)", maxWidth=90, wrapHeaderText=True, autoHeaderHeight=True)
    gb.configure_column("Sobrevivencia final", header_name="SOBRE. FINAL", maxWidth=80, wrapHeaderText=True, autoHeaderHeight=True)
    gb.configure_column("FCA", maxWidth=61, wrapHeaderText=True, autoHeaderHeight=True)
    gb.configure_column("Costo lb/camaron", header_name="COSTO LB/CAMARON", maxWidth=115, wrapHeaderText=True, autoHeaderHeight=True)
    gb.configure_column("UP($/ha/dia)", header_name="UP ($/HA/DIA)", maxWidth=97, wrapHeaderText=True, autoHeaderHeight=True, cellStyle=cellstyle_jscode_up )
    gb.configure_column("ROI(%)", maxWidth=80, wrapHeaderText=True, autoHeaderHeight=True, cellStyle=cellstyle_jscode_roi )
    gb.configure_column("Precio venta pesca final ($/Kg)", header_name="PRECIO PONDERADO FINAL ($/kg)", maxWidth=155, wrapHeaderText=True, autoHeaderHeight=True )
    gb.configure_column("tipo_proyeccion", header_name="TIPO PROYECCION", maxWidth=180, wrapHeaderText=True, autoHeaderHeight=True )
    gb.configure_column("aguaje", header_name="AGUAJE", maxWidth=100, wrapHeaderText=True, autoHeaderHeight=True, hide=True )
    gb.configure_pagination(paginationAutoPageSize=False, enabled=False)  # Habilita la paginación
    gb.configure_default_column(editable=False, filter=True, sortable=True)  # Habilita el filtrado y la ordenación en cada columna
    gb.configure_column("IsMax", hide=True)
    gb.configure_column("IsMax_Up", hide=True)
    gb.configure_selection(selection_mode='multiple', use_checkbox=True)
    gb.configure_grid_options(onSelectionChanged=checkbox_event_jscode, 
                              getRowStyle=row_style_jscode,
                              
                              )  # Aplica estilos condicionales a toda la fila
    gridOptions = gb.build()

    # Definir estilos personalizados para el encabezado
    
    # CSS personalizado para cambiar el color de fondo en el estado de hover

    cols_table = st.columns([1])
    with cols_table[0]:
    # Muestra el DataFrame en un AgGrid con tamaño fijo y desplazamiento
        grid_table = AgGrid(
            data_df,
            gridOptions=gridOptions,
            enable_enterprise_modules=True,
            allow_unsafe_jscode=True,  # Esta opción permite usar JavaScript no seguro
            theme=AgGridTheme.STREAMLIT,  # Cambia el tema si lo deseas
            height=400,  # Especifica la altura en píxeles
            width='100%',  # Especifica el ancho en píxeles o porcentaje
            custom_css=TABLE_STYLE,  # Aplica el CSS personalizado
            update_mode=GridUpdateMode.SELECTION_CHANGED,

        )

    # DataFrame para almacenar las filas seleccionadas
    
    # Update session state with the current selection
    st.session_state[state_key] = grid_table["selected_rows"]


def plot_table_groupped(data_df):
    data_df.rename(columns=
            {"campo": "CAMPO",
             "piscina": "PISCINA",
             "fecha_siembra": "FECHA SIEMBRA",
             "peso_siembra": "PESO SIEMBRA",
             "densidad_siembra": "DENSIDAD SIEMBRA",
             "peso_actual": "ÚLTIMO PESO TOMADO",
             "dia_final": "ÚLTIMO DÍA DATA REAL",
             "crecimiento_ultimas_4_semanas": "CREC ULT 4 SEMANAS",
             "costo_fijo_ha_dia": "COSTO FIJO ($/HA/DIA)",
             "costo_mix_alimento_kg": "COSTO MIX (KG)",
             "costo_millar_larva": "COSTO MILLAR",
             "kgab_dia": "KG ABBB/DIA",
             'fecha_muestreo': "ULTIMA FECHA MUESTREO"
             }
        , inplace=True)
    data_df = data_df.groupby("PISCINA").agg({
        "FECHA SIEMBRA": get_last,
        "ULTIMA FECHA MUESTREO": get_last,
        "ÚLTIMO DÍA DATA REAL": "median",
        "PESO SIEMBRA": "median",
        "DENSIDAD SIEMBRA": "median",
        "ÚLTIMO PESO TOMADO": "median",
        "CREC ULT 4 SEMANAS": "median",
        "COSTO FIJO ($/HA/DIA)": "median",
        "COSTO MIX (KG)": "median",
        "COSTO MILLAR": "median",
        "KG ABBB/DIA": "median"
    })
    data_df = data_df.sort_values(by="ÚLTIMO DÍA DATA REAL", ascending=False)
    data_df.reset_index(inplace=True)
    data_df = data_df.round(2)
    # Crea un GridOptionsBuilder
    gb = GridOptionsBuilder.from_dataframe(data_df)
    # configuramos ancho de columnas
    gb.configure_column("PISCINA", maxWidth=100)
    gb.configure_column("FECHA SIEMBRA", maxWidth=140)
    gb.configure_column("ULTIMA FECHA MUESTREO", maxWidth=140, wrapHeaderText=True, autoHeaderHeight=True)
    gb.configure_column("ÚLTIMO DÍA DATA REAL", maxWidth=95, wrapHeaderText=True, autoHeaderHeight=True)
    gb.configure_column("PESO SIEMBRA", header_name="PESO SIEMBRA (GR)", maxWidth=95, wrapHeaderText=True, autoHeaderHeight=True)
    gb.configure_column("DENSIDAD SIEMBRA", header_name="DENSIDAD SIEMBRA (IND/M2)", maxWidth=100, wrapHeaderText=True, autoHeaderHeight=True)
    gb.configure_column("ÚLTIMO PESO TOMADO",  maxWidth=110, wrapHeaderText=True, autoHeaderHeight=True)
    gb.configure_column("CREC ULT 4 SEMANAS", maxWidth=100, wrapHeaderText=True, autoHeaderHeight=True)
    gb.configure_column("COSTO FIJO ($/HA/DIA)",  maxWidth=105, wrapHeaderText=True, autoHeaderHeight=True)
    gb.configure_column("COSTO MIX (KG)",  maxWidth=107, wrapHeaderText=True, autoHeaderHeight=True )
    gb.configure_column("COSTO MILLAR", maxWidth=100, wrapHeaderText=True, autoHeaderHeight=True )
    gb.configure_column("KG ABBB/DIA",  maxWidth=155, wrapHeaderText=True, autoHeaderHeight=True )
    gb.configure_pagination(paginationAutoPageSize=False, enabled=False)  # Habilita la paginación
    gb.configure_default_column(editable=False, filter=True, sortable=True)  # Habilita el filtrado y la ordenación en cada columna
    #gb.configure_selection(selection_mode='multiple', use_checkbox=True)
    gridOptions = gb.build()

    cols_table_groupped = st.columns([1])
    with cols_table_groupped[0]:
    # Muestra el DataFrame en un AgGrid con tamaño fijo y desplazamiento
        AgGrid(
            data_df,
            gridOptions=gridOptions,
            enable_enterprise_modules=True,
            allow_unsafe_jscode=True,  # Esta opción permite usar JavaScript no seguro
            theme=AgGridTheme.STREAMLIT,  # Cambia el tema si lo deseas
            height=270,  # Especifica la altura en píxeles
            width='100%',  # Especifica el ancho en píxeles o porcentaje
            custom_css=TABLE_STYLE,  # Aplica el CSS personalizado
            update_mode=GridUpdateMode.SELECTION_CHANGED,

        )
    
    #st.dataframe(data_df.round(2))


def plot_table_prices(data_df, state_key):
    # Crea un GridOptionsBuilder
    gb = GridOptionsBuilder.from_dataframe(data_df)
    gb.configure_pagination(paginationAutoPageSize=False, enabled=False)  # Habilita la paginación
    gb.configure_default_column(filter=True, sortable=True)  # Habilita el filtrado y la ordenación en cada columna
    gb.configure_column("Precios", editable=True, maxWidth=180)
    gb.configure_column("Tallas", editable=False, maxWidth=280)
    gridOptions = gb.build()
    grid_table = AgGrid(
            data_df,
            gridOptions=gridOptions,
            enable_enterprise_modules=True,
            allow_unsafe_jscode=True,  # Esta opción permite usar JavaScript no seguro
            theme=AgGridTheme.STREAMLIT,  # Cambia el tema si lo deseas
            height=300,
            width='100%',  # Especifica el ancho en píxeles o porcentaje
            update_mode=GridUpdateMode.SELECTION_CHANGED,

        )
    st.session_state[state_key] = grid_table['data']

