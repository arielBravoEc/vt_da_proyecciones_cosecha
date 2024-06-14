from datetime import datetime, timedelta
import streamlit as st

# Define el background de la app
BACKGROUND_COLOR = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: #F6F7FC; /* Aquí puedes poner el color que desees */
    background-image: none;
}
</style>
"""

# Define el CSS para las cards
CARD_CSS = """
<style>
.card {
    background-color: #ffffff; /* Color de fondo blanco */
    border-radius: 10px; /* Bordes redondeados */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Sombra */
    margin: 20px 0; /* Espaciado entre tarjetas */
    padding: 20px; /* Espaciado interno */
    transition: transform 0.2s; /* Transición suave */
}

.card:hover {
    transform: translateY(-10px); /* Efecto hover */
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2); /* Sombra más intensa al hacer hover */
}

.card-title {
    font-size: 24px; /* Tamaño del título */
    font-weight: bold; /* Negrita */
    margin-bottom: 10px; /* Espaciado inferior */
}

.card-content {
    font-size: 16px; /* Tamaño del contenido */
    color: #333; /* Color del texto */
}

.card-footer {
    display: flex; /* Flexbox para el pie de la tarjeta */
    justify-content: flex-end; /* Alinear al final */
    margin-top: 20px; /* Espaciado superior */
}

.card-button {
    padding: 10px 20px; /* Espaciado interno del botón */
    background-color: #007bff; /* Color de fondo del botón */
    color: #fff; /* Color del texto del botón */
    border: none; /* Sin bordes */
    border-radius: 5px; /* Bordes redondeados del botón */
    text-decoration: none; /* Sin subrayado */
    cursor: pointer; /* Cursor de puntero */
    transition: background-color 0.2s; /* Transición suave */
}

.card-button:hover {
    background-color: #0056b3; /* Color de fondo del botón al hacer hover */
}
</style>
"""

CARD_CSS_V2 = """
<style>
.card {
    background-color: #ffffff;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    padding: 20px;
    margin-bottom: 20px;
}

.card-title {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
}

.icon {
    width: 30px;
    height: 30px;
    margin-right: 10px;
}
</style>
"""

container_css = """
<style>
/* Selector para el fondo del contenedor */
body {
    background-color: #f0f0f0 !important;  /* Color de fondo */
}
</style>
"""

# FECHA ACTUAL
FECHA_ACTUAL = datetime.now()
# FECHA MINIMA DEL ULTIMO DATO: ES DECIR SI UNA PISCINA ESTá CON SU ULTIMO DATO
# MAS DE N DIAS DESACTUALIZADO, NO SE LO TOMA EN CUENTA A ESA PISCINA PARA LA PROY
FECHA_MINIMA_ULTIMO_DATO = (FECHA_ACTUAL -  timedelta(days=30)).strftime("%Y-%m-%d")
PRIMARY_COLOR = '#884de3'
PRIMARY_COLOR_BACKGROUND = 'rgba(136, 77, 227, 0.2)'
MINIMO_DIAS_PROYECTO = 40
VARIABLES_INTERES = ['id_piscina', 'campo', 'piscina', 'ha', 'fecha_siembra', 'fecha_muestreo', 'tipo_proyeccion', 'Días restantes para cumplir proyecto',  
                          'Mortalidad semanal','densidad_siembra_ind_m2', 'porcentaje_sob_campo', 'peso_siembra_gr', 'peso_actual_gr', 'Días de ciclo finales', 
                          'Fecha estimada de cosecha', 'Peso final proyectado (gr)', 
                           'Biomasa proyecto (lb/ha)', 'Biomas total proyecto (lb)', 'Sobrevivencia final de ciclo proyecto (%)', 'FCA Proyecto', 'Total Costo x Libra ($/lb) Proyecto',
                           "UP ($/Ha/Día) Proyecto", 'ROI Proyecto', 'dias_cultivo', 'crecimiento_ultimas_4_semanas', 'Precio venta pesca final ($/kg)', 'costo_fijo_ha_dia', 'costo_mix_alimento_kg', 'costo_millar_larva', 'kgab_dia', 'alimento_acumulado', 'capacidad_de_carga_lbs_ha']

TABLE_STYLE = {
        ".ag-theme-streamlit .ag-row-hover": {
            "background-color": f"{PRIMARY_COLOR_BACKGROUND} !important"  # Cambia este valor al color morado que desees
        },
        ".ag-theme-streamlit .ag-menu-option:hover": {
            "background-color": f"{PRIMARY_COLOR_BACKGROUND} !important",  # Cambia este valor al color morado que desees para el hover del menú
            
        },
        ".ag-header-cell-menu-button:hover":{
                "color": f"{PRIMARY_COLOR} !important"
            },
        ".ag-checkbox-input-wrapper.ag-checked:after": {
        
            "color": f"{PRIMARY_COLOR} !important"  # Cambia el color del borde del checkbox
        },
        ".ag-tab-selected": {
        
            "border-bottom-color": f"{PRIMARY_COLOR} !important"  # Cambia el color del borde del checkbox
        }
    }


farm_key = st.secrets["CLIENTE"]

FARMS = None
if farm_key == "NATURISA":
    FARMS = ("CAMARONES NATURISA", "CAMINO REAL", "MARCHENA")
elif farm_key == "PESFALAN":
    FARMS = ("AGLIPESCA", "AGLIPESCA SUR", "MATORRILLOS", "PESFABUELE")
else:
    FARMS = ("CAMARONES NATURISA", "CAMINO REAL", "MARCHENA")

DIAS_PROYECTO_DEFECTO =  83
SOB_PROYECTO_DEFECTO = 0.48
PESO_PROYECTO_DEFECTO = None

if farm_key == "NATURISA":
    DIAS_PROYECTO_DEFECTO =  83
    SOB_PROYECTO_DEFECTO = 0.48
    PESO_PROYECTO_DEFECTO = 33.25
elif farm_key == "PESFALAN":
    DIAS_PROYECTO_DEFECTO =  68
    SOB_PROYECTO_DEFECTO = 0.71
    PESO_PROYECTO_DEFECTO = 21.0


