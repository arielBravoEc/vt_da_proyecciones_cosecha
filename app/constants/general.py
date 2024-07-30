from datetime import datetime, timedelta
from catalog.projections_catalog import get_excel_data
import streamlit as st


# FECHA ACTUAL
#FECHA_ACTUAL = datetime.now() - timedelta(days=70)
FECHA_ACTUAL = datetime.now()
# FECHA MINIMA DEL ULTIMO DATO: ES DECIR SI UNA PISCINA ESTá CON SU ULTIMO DATO
# MAS DE N DIAS DESACTUALIZADO, NO SE LO TOMA EN CUENTA A ESA PISCINA PARA LA PROY
FECHA_MINIMA_ULTIMO_DATO = (FECHA_ACTUAL - timedelta(days=30)).strftime("%Y-%m-%d")

MINIMO_DIAS_PROYECTO = 40
VARIABLES_INTERES = [
    "id_piscina",
    "campo",
    "piscina",
    "ha",
    "fecha_siembra",
    "fecha_muestreo",
    "tipo_proyeccion",
    "Días restantes para cumplir proyecto",
    "Mortalidad semanal",
    "densidad_siembra_ind_m2",
    "porcentaje_sob_campo",
    "peso_siembra_gr",
    "peso_actual_gr",
    "Días de ciclo finales",
    "Fecha estimada de cosecha",
    "Peso final proyectado (gr)",
    "Biomasa proyecto (lb/ha)",
    "Biomas total proyecto (lb)",
    "Sobrevivencia final de ciclo proyecto (%)",
    "FCA Proyecto",
    "Total Costo x Libra ($/lb) Proyecto",
    "UP ($/Ha/Día) Proyecto",
    "ROI Proyecto",
    "dias_cultivo",
    "crecimiento_ultimas_4_semanas",
    "Precio venta pesca final ($/kg)",
    "costo_fijo_ha_dia",
    "costo_mix_alimento_kg",
    "costo_millar_larva",
    "kgab_dia",
    "alimento_acumulado",
    "capacidad_de_carga_lbs_ha",
    "sobrevivencia_consumo"
]


farm_key = st.secrets["CLIENTE"]
DIAS_PROYECTO_DEFECTO = 90
SOB_PROYECTO_DEFECTO = 0.60
PESO_PROYECTO_DEFECTO = 30.0
COSTO_MILLAR_DEFECTO = 5.0
COSTO_MIX_DEFECTO = 1.12
COSTO_FIJO_DEFECTO = 30.0

FARMS = None
if farm_key == "NATURISA":
    FARMS = ("CAMARONES NATURISA", "CAMINO REAL", "MARCHENA")
    DIAS_PROYECTO_DEFECTO = 85
    SOB_PROYECTO_DEFECTO = 0.55
    PESO_PROYECTO_DEFECTO = 33.25
    COSTO_MIX_DEFECTO = 1.10
    COSTO_FIJO_DEFECTO = 33.0
elif farm_key == "PESFALAN":
    FARMS = ("AGLIPESCA", "AGLIPESCA SUR", "MATORRILLOS", "PESFABUELE")
    DIAS_PROYECTO_DEFECTO = 60
    SOB_PROYECTO_DEFECTO = 0.85
    PESO_PROYECTO_DEFECTO = 22.0
    COSTO_MILLAR_DEFECTO = 5.0
    COSTO_MIX_DEFECTO = 0.96
    COSTO_FIJO_DEFECTO = 29.6
elif farm_key == "SIXTO EGUIGUREN":
    FARMS = ("CALICA", "CHURUTE")
    DIAS_PROYECTO_DEFECTO = 90
    SOB_PROYECTO_DEFECTO = 0.70
    PESO_PROYECTO_DEFECTO = 28.0
    COSTO_MILLAR_DEFECTO = 3.50
    COSTO_MIX_DEFECTO = 1.29
    COSTO_FIJO_DEFECTO = 30.0
elif farm_key == 'ACUARIOS':
    FARMS = ("SATUKIN", "TECNOTEMPE")
    DIAS_PROYECTO_DEFECTO = 70
    SOB_PROYECTO_DEFECTO = 0.61
    PESO_PROYECTO_DEFECTO = 27.5

else:
    FARMS = ("CAMARONES NATURISA", "CAMINO REAL", "MARCHENA")

DEFAULT_CONFIG = {
    "prices": get_excel_data(sheet_name="precios"),
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