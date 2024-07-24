

import sys
import os
import warnings

# Suprimir FutureWarnings
warnings.simplefilter(action='ignore')

# Añadir la ruta del proyecto a sys.path para que Python pueda encontrar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.proyection_helpers import get_projections
from Tests.test_constants import COSTO_FIJO,COSTO_MILLAR,DIAS_PROYECTO,COSTO_MIX,RANGO_PROYECCION,SOB_PROYECTO, FARM_NAME,PORCENTAJE_AB,PORCENTAJE_SOB,SOBREVIVENCIA_CAMPO, PRICES_DF,CLIENT_NAME_BENCH,CLIENT_NAME_EVAT,FECHA_MINIMA_ULTIMO_DATO,MINIMO_DIAS_PROYECTO
from catalog.projections_catalog import get_bench_data_for_test

proyections_df = get_projections(
                        farm_name=FARM_NAME,
                        project_duration=DIAS_PROYECTO,
                        project_survival=SOB_PROYECTO,
                        project_range=RANGO_PROYECCION,
                        is_using_personalized_cost=True,
                        is_using_personalized_price=True,
                        prices_table=PRICES_DF,
                        cost_info={
                            "mix": COSTO_MIX,
                            "millar": COSTO_MILLAR,
                            "fijo": COSTO_FIJO,
                        },
                        is_using_personalized_load_capacity=True,
                        load_capacity=10000,
                        is_using_lineal_feed=True,
                        percentage_dynamical_feed=PORCENTAJE_AB,
                        is_using_sob_campo = SOBREVIVENCIA_CAMPO,
                        percentage_sob = PORCENTAJE_SOB,
                        test=True,
                        fecha_ultimo_dato = FECHA_MINIMA_ULTIMO_DATO,
                        minimo_dias_proyecto = MINIMO_DIAS_PROYECTO,
                        fecha_maxima_muestreo = "2024-05-20"
                    )
bench_df = get_bench_data_for_test(CLIENT_NAME_BENCH, "2024-05-01")
print(bench_df)