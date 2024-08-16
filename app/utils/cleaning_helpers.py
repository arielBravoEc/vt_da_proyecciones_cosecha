import pandas as pd
import numpy as np


def clean_nulls_and_fill_nan(data_df: pd.DataFrame) -> pd.DataFrame:
    """
    Esta ``función`` elimina del dataframe original valores nulos
    y faltantes de los principales indicadores

    Args:
        data_df (Pandas dataframe): Datos del evat.

    Returns:
        Retorna pandas dataframe
    """
    data_df["peso_raleo_1"] = data_df["peso_raleo_1"].fillna(0)
    data_df["peso_raleo_2"] = data_df["peso_raleo_2"].fillna(0)
    data_df["peso_raleo_3"] = data_df["peso_raleo_3"].fillna(0)
    data_df["biomasa_raleo_lb_ha_1"] = data_df["biomasa_raleo_lb_ha_1"].fillna(0)
    data_df["biomasa_raleo_lb_ha_2"] = data_df["biomasa_raleo_lb_ha_2"].fillna(0)
    data_df["biomasa_raleo_lb_ha_3"] = data_df["biomasa_raleo_lb_ha_3"].fillna(0)
    # comprobamos nulos

    data_df["peso_siembra_gr"] = data_df["peso_siembra_gr"].apply(
        pd.to_numeric, errors="coerce"
    )
    data_df["peso_actual_gr"] = data_df["peso_actual_gr"].apply(
        pd.to_numeric, errors="coerce"
    )
    data_df["dias_cultivo"] = data_df["dias_cultivo"].apply(
        pd.to_numeric, errors="coerce"
    )
    # print(data_df.shape)
    data_df["ha"] = data_df["ha"].apply(pd.to_numeric, errors="coerce")
    data_df["alimento_acumulado"] = data_df["alimento_acumulado"].apply(
        pd.to_numeric, errors="coerce"
    )
    # para validar que se ingresan nulos
    nulos_por_columna = (
        data_df[
            [
                "fecha_muestreo",
                "dias_cultivo",
                "campo",
                "piscina",
                "fecha_siembra",
                "densidad_siembra_ind_m2",
                "peso_actual_gr",
                "kgab_dia",
                "alimento_acumulado",
                "ha",
                "porcentaje_sob_campo",
                "crecimiento_ultimas_4_semanas",
                "costo_fijo_ha_dia",
                "costo_millar_larva",
                "costo_mix_alimento_kg",
                "crecimiento_lineal_semanal",
                "peso_siembra_gr",
            ]
        ]
        .isnull()
        .sum()
    )
    # imprimir en caso de revision
    # print(nulos_por_columna)
    data_df = data_df.dropna(
        axis=0,
        subset=[
            "fecha_muestreo",
            "dias_cultivo",
            "campo",
            "piscina",
            "fecha_siembra",
            "densidad_siembra_ind_m2",
            "peso_actual_gr",
            "kgab_dia",
            "alimento_acumulado",
            "ha",
            "porcentaje_sob_campo",
            "crecimiento_ultimas_4_semanas",
            "costo_fijo_ha_dia",
            "costo_millar_larva",
            "costo_mix_alimento_kg",
            "crecimiento_lineal_semanal",
            "peso_siembra_gr",
        ],
    )
    print(data_df.shape)
    return data_df


def clean_no_sense_values(data_df: pd.DataFrame) -> pd.DataFrame:
    """
    Esta ``función`` elimina del dataframe original valores fuera de
    contexto y que no tienen sentido

    Args:
        data_df (Pandas dataframe): Datos del evat.

    Returns:
        Retorna pandas dataframe
    """
    # eliminamos ps 132 de aglipesca debido a que es precria
    data_df = data_df.drop(
        data_df[(data_df["piscina"] == "132") & (data_df["campo"] == "AGLIPESCA")].index
    )
    data_df = data_df[data_df["densidad_siembra_ind_m2"] > 2]
    data_df = data_df[data_df["densidad_siembra_ind_m2"] < 70]
    data_df = data_df[data_df["peso_siembra_gr"] > 0.1]
    data_df = data_df[data_df["ha"] > 0]
    data_df = data_df[data_df["densidad_siembra_ind_m2"] > 5]
    data_df = data_df[data_df["porcentaje_sob_campo"] > 0.17]
    data_df = data_df[data_df["porcentaje_sob_campo"] <= 1.3]
    data_df = data_df[data_df["crecimiento_ultimas_4_semanas"] > 0]
    data_df["crecimiento_ultimas_4_semanas"] = np.where(
        data_df["crecimiento_ultimas_4_semanas"] > 4,
        data_df["crecimiento_lineal_semanal"],
        data_df["crecimiento_ultimas_4_semanas"],
    )
    data_df = data_df[data_df["crecimiento_ultimas_4_semanas"] > 0]
    data_df = data_df[data_df["crecimiento_ultimas_4_semanas"] < 5]
    data_df = data_df[data_df["dias_cultivo"] > 0]
    data_df = data_df[data_df["alimento_acumulado"] > 0]
    data_df = data_df[data_df["kgab_dia"] > 0]
    return data_df


def filter_cycles_close_to_hasrvest(
    data_df: pd.DataFrame, min_dias: int
) -> pd.DataFrame:
    """
    Esta ``función`` elimina del dataframe datos de piscinas que no están
    cerca de cosecharse de acerdo a un minimo de días establecido

    Args:
        data_df (Pandas dataframe): Datos del evat.
        min_dias (int): mínimo de  días para considerar si un ciclo
        está cerca de cosecha y puede ser analizado.

    Returns:
        Retorna pandas dataframe
    """
    # filtramos las piscinas que su dia de cultivo es mayor a sus dias de proyecto
    data_df = data_df[data_df["dias_cultivo"] < data_df["dias_proyecto"]]
    data_df["diff_dias"] = data_df["dias_proyecto"] - data_df["dias_cultivo"]
    # filtramos pisicnas que no estan cerca a cosecha
    data_df = data_df[data_df["diff_dias"] <= min_dias]
    data_df = data_df.sort_values(by="fecha_muestreo", ascending=False)
    return data_df
