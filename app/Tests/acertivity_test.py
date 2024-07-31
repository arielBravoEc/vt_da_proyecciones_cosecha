

import sys
import os
import warnings
import numpy as np
import pandas as pd
# Suprimir FutureWarnings
warnings.simplefilter(action='ignore')
from datetime import datetime, timedelta
# Añadir la ruta del proyecto a sys.path para que Python pueda encontrar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.proyection_helpers import get_projections
from Tests.test_constants import COSTO_FIJO,COSTO_MILLAR,DIAS_PROYECTO,COSTO_MIX,RANGO_PROYECCION,SOB_PROYECTO, FARM_NAME,PORCENTAJE_AB,PORCENTAJE_SOB,SOBREVIVENCIA_CAMPO, PRICES_DF,CLIENT_NAME_BENCH,CLIENT_NAME_EVAT,FECHA_MINIMA_ULTIMO_DATO,MINIMO_DIAS_PROYECTO
from catalog.projections_catalog import get_bench_data_for_test


bench_df = get_bench_data_for_test(CLIENT_NAME_BENCH, "2024-05-01")
## en el caso de aglipessca quitamos los primeros 3 caracteres para hacer match con el bench
bench_df['NombrePiscina'] = np.where(bench_df['NombreCampo'] == "AGLIPESCA",
                                    bench_df['NombrePiscina'].str[3:],
                                    bench_df['NombrePiscina']
                                     )
#iteramos cada pisicna cosechada para obtener su proyeccion 1, 2 , 3 semanas antes
proyecciones_lst = []
for i in range(1,4):
    for index, row in bench_df.iterrows():
            row_proyection = row
            row_proyection['SemanaProyectada'] = i
            week_date = row['FechaCosecha'] -  timedelta(days=6*i)
            row_proyection['FechaProyeccion'] = week_date
            proy_data = get_projections(
                            farm_name=CLIENT_NAME_EVAT,
                            project_duration=row['DiasCiclo'],
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
                            fecha_maxima_muestreo = week_date,
                            pool_proy_test=row['NombrePiscina']
                        )
            #print(proy_data.columns)
            if len(proy_data) > 0:
                row_proyection['CostoFijo_HaDia_Proyeccion'] = proy_data['costo_fijo_ha_dia'][0]
                row_proyection['FCA_Proyeccion'] = proy_data['fca'][0]
                row_proyection['PesoPescaProyeccion'] = proy_data['peso'][0]
                row_proyection['PrecioCamaronPesca_Proyeccion'] = proy_data['precio_venta_pesca'][0]
                row_proyection['AlimentoAcumuladoKg_Proyeccion'] = proy_data['Kilos AABB Totales para cumplir proyecto'][0]
                row_proyection['SobPesca_Proyeccion'] = proy_data['sobrevivencia'][0]
                row_proyection['PrecioMixAlimento_Proyeccion'] = proy_data['costo_mix_alimento_kg'][0]
                row_proyection['PrecioLarva_Proyeccion'] = proy_data['costo_millar_larva'][0]
                row_proyection['BiomasaPescaLbHa_Proyeccion'] = proy_data['biomasa'][0]
                row_proyection['CostoLbCamaron_Proyeccion'] = proy_data['costo'][0]
                row_proyection['UP_HaDia_Proyeccion'] = proy_data['up'][0]
                row_proyection['UltimaSobCampo'] = proy_data['porcentaje_sob_campo'][0]
                row_proyection['UltimoPesoMuestreo'] = proy_data['peso_actual'][0]
                row_proyection['UltimaSobConsumo'] = proy_data['sobrevivencia_consumo'][0]
                row_proyection['UltimoAlimentoAcumuladoKg'] = proy_data['alimento_acumulado'][0]
                proyecciones_lst.append(pd.DataFrame(row_proyection).transpose())
            #print(type(row_proyection))
            
acertividad_df  = pd.concat(proyecciones_lst, ignore_index=True)
acertividad_df['DensidadFinal_Im2_Proyeccion'] = acertividad_df['DensidadSiembra_Im2']*(acertividad_df['SobPesca_Proyeccion']/100)
acertividad_df['SobPesca'] = acertividad_df['SobPesca']*100

## calculamos las precisiones
def calculate_mape(real,pred):
    mape = (1 - (abs(real - pred) / abs(real)))
    if mape < 0:
        return 0
    else:
        return mape
        #return 5
acertividad_df['PrecisionFCA'] = np.vectorize(calculate_mape, otypes=[np.float64])(acertividad_df['FCA'],acertividad_df['FCA_Proyeccion'])
acertividad_df['PrecisionPesoPesca'] = np.vectorize(calculate_mape, otypes=[np.float64])(acertividad_df['PesoPesca'],acertividad_df['PesoPescaProyeccion'])
acertividad_df['PrecisionSobPesca'] = np.vectorize(calculate_mape, otypes=[np.float64])(acertividad_df['SobPesca'],acertividad_df['SobPesca_Proyeccion'])
acertividad_df['PrecisionAlimentoAcumuladoKg'] = np.vectorize(calculate_mape, otypes=[np.float64])(acertividad_df['AlimentoAcumuladoKg'],acertividad_df['AlimentoAcumuladoKg_Proyeccion'])
acertividad_df['PrecisionDensidadFinal_Im2'] = np.vectorize(calculate_mape, otypes=[np.float64])(acertividad_df['DensidadFinal_Im2'],acertividad_df['DensidadFinal_Im2_Proyeccion'])
acertividad_df['PrecisionCostoFijo_HaDia'] = np.vectorize(calculate_mape, otypes=[np.float64])(acertividad_df['CostoFijo_HaDia'],acertividad_df['CostoFijo_HaDia_Proyeccion'])
acertividad_df['PrecisionPrecioMixAlimento'] = np.vectorize(calculate_mape, otypes=[np.float64])(acertividad_df['PrecioMixAlimento'],acertividad_df['PrecioMixAlimento_Proyeccion'])
acertividad_df['PrecisionPrecioLarva'] = np.vectorize(calculate_mape, otypes=[np.float64])(acertividad_df['PrecioLarva'],acertividad_df['PrecioLarva_Proyeccion'])
acertividad_df['PrecisionCostoLbCamaron'] = np.vectorize(calculate_mape, otypes=[np.float64])(acertividad_df['CostoLbCamaron'],acertividad_df['CostoLbCamaron_Proyeccion'])
acertividad_df['PrecisionUP_HaDia'] = np.vectorize(calculate_mape, otypes=[np.float64])(acertividad_df['UP_HaDia'],acertividad_df['UP_HaDia_Proyeccion'])
acertividad_df['PrecisionPrecioCamaronPesca'] = np.vectorize(calculate_mape, otypes=[np.float64])(acertividad_df['PrecioCamaronPesca'],acertividad_df['PrecioCamaronPesca_Proyeccion'])
acertividad_df['PrecisionBiomasaPescaLbHa'] = np.vectorize(calculate_mape, otypes=[np.float64])(acertividad_df['BiomasaPescaLbHa'], acertividad_df['BiomasaPescaLbHa_Proyeccion'])
#print(acertividad_df[['PrecisionUP_HaDia', 'UP_HaDia', 'UP_HaDia_Proyeccion']])
acertividad_df.to_excel("./acertividad.xlsx", index = False)
print(bench_df)
print("DATASET DE ACERTIVIDAD GENERADO")