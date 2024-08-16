# import psycopg2
import pandas as pd
import requests
import os
import streamlit as st
from sqlalchemy import create_engine
import mysql.connector as connection
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
from office365.runtime.auth.authentication_context import AuthenticationContext
from msal import ConfidentialClientApplication
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import io


def get_evat_data(farm_name: str) -> pd.DataFrame:
    """
    Esta ``función`` obtiene datos del evat de la base de datos de genIA
    Args:
        farm_name (str): Nombre del campo.
    Returns:
        Retorna el dataframe con los datos del evat
    """
    # CREDENCIALES
    print("Intentando conectarse a la base de datos")
    string_conection = (
        f'postgresql+pg8000://{st.secrets["USER"]}:{st.secrets["PASSWORD"]}@'
        f'{st.secrets["HOST"]}:5432/{st.secrets["DATABASE"]}'
    )
    # Crear el motor de SQLAlchemy
    engine = create_engine(string_conection)
    query = f"""
            select evat.nombre_campo as campo,
                evat.piscina,
                evat.fecha_siembra,
                evat.fecha_muestreo,
                evat.ha,
                evat.dias_cultivo,
                evat.densidad_siembra_cam_m2 as densidad_siembra_ind_m2,
                evat.peso_siembra_gr,
                evat.peso_actual_gr,
                evat.alimento_diario_total as kgab_dia,
                evat.sobrevivencia,
                evat.alimento_acumulado,
                evat.sobrevivencia_actual_campo as porcentaje_sob_campo,
                evat.crecimiento_gr_semana,
                evat.crecimiento_lineal_semanal,
                evat.crecimiento_ultimas_4_semanas,
                evat.fca_campo_sin_biomasa_inicial as fca_campo,
                evat.peso_raleo_1,
                evat.peso_raleo_2,
                evat.peso_raleo_3,
                evat.biomasa_raleo_lb_ha_1,
                evat.biomasa_raleo_lb_ha_2,
                evat.biomasa_raleo_lb_ha_3,
                evat.tipo_alimento_std,
                evat.costos_fijos as costo_fijo_ha_dia,
                evat.precio_mix as costo_mix_alimento_kg,
                evat.precio_larva as costo_millar_larva,
                evat.capacidad_de_carga_lbs_ha,
                evat.sobrevivencia_consumo,
                cl.razon_social as cliente
                from productivo.evat_calculado_vista as evat
            left join cliente.cliente as cl
                on evat.codigo_cliente = cl.codigo
            where UPPER(evat.nombre_campo) = '{farm_name}'
                and evat.fecha_siembra >= '2024-01-01'

                and evat.piscina not like '%PRE%'
                        """
    print("Conexión exitosa")
    data_df = pd.read_sql_query(query, engine)

    return data_df


def get_excel_data(
    sheet_name: str = None, skiprows: int = None, usecols: str = None
) -> pd.DataFrame:
    """
    Esta ``función`` obtiene datos del archivo plano con informacion de
    precios y distribuciones de tallas
    Args:
        sheet_name (str): Nombre de la pestaña.
        skiprows (int): numero de filas a saltarse para obtener la informacion.
        usecols (str): rango de columnas para extraer la informacion.
    Returns:
        Retorna el dataframe con los datos del excel
    """
    dir_actual = os.getcwd()
    # print("Ruta del directorio actual:", dir_actual)
    ruta_excel = os.path.join(dir_actual, "app", "static", "data", "datos_evatv2.xlsm")
    data_df = pd.read_excel(
        ruta_excel, sheet_name=sheet_name, skiprows=skiprows, usecols=usecols
    )
    return data_df


def get_bench_data_for_test(farm_name: str, min_harvest_date: str) -> pd.DataFrame:
    """
    Esta ``función`` obtiene datos del bench para hacer el test de acertividad.
    Args:
        farm_name (str): Nombre del campo.
        min_harvest_date (str): fecha para filtrar y obtener solo ciclos mas recientes.
    Returns:
        Retorna el dataframe con los datos del bench
    """
    mydb = connection.connect(
        host="benchsrv.mysql.database.azure.com",
        database="importdb",
        user="vitapro_powerbi@benchsrv",
        passwd="UYBN4JNUtBRZVDh",
    )
    query = f"""select NombreCampo,
                    GrupoCliente,
                    NombrePiscina,
                    Ha,
                    FechaSiembra,
                    FechaCosecha,
                    TipoSiembra,
                    DensidadSiembra_Im2,
                    PesoSiembra,
                    PesoPesca,
                    BiomasaPesca,
                    FCA,
                    CostoFijo_HaDia,
                    PrecioLarva,
                    PrecioMixAlimento,
                    PrecioCamaronPesca,
                    MarcaAABBEngorde,
                    RendimientoPlanta,
                    DiasCiclo,
                    DensidadSiembra_Iha,
                    CrecimientoSemanal,
                    CosechaTotal,
                    SobPesca,
                    lbs_ha,
                    DensidadFinal_Im2,
                    CostoLbCamaron,
                    UP_HaDia,
                    ROI,
                    CrecimientoDiario,
                    Estatus_Raleos
                from importdb.bdciclos
                where  GrupoCliente in ('{farm_name}')
                and FechaCosecha > '{min_harvest_date}'
                order by FechaCosecha desc"""
    bench_df = pd.read_sql(query, mydb)
    bench_df["BiomasaPescaLbHa"] = bench_df["BiomasaPesca"] / bench_df["Ha"]
    bench_df["BiomasaTotalKg"] = (bench_df["lbs_ha"] * bench_df["Ha"]) / 2.2
    bench_df["AlimentoAcumuladoKg"] = bench_df["BiomasaTotalKg"] * bench_df["FCA"]
    return bench_df


def get_evat_data_test(
    client_name: str, fecha_maxima_muestreo: str, pool_proy_test: str
) -> pd.DataFrame:
    """
    Esta ``función`` obtiene datos del evat de la base de datos de genIA para
    test de acertividad
    Args:
        client_name (str): Nombre del cliente.
        fecha_maxima_muestreo (str): fecha para filtrar y obtener solo
        muestreos mas antiguos.
        pool_proy_test (str): piscina de la cual se van a obtener los datos.
    Returns:
        Retorna el dataframe con los datos del evat
    """
    # CREDENCIALES
    print("Intentando conectarse a la base de datos")
    string_conection = (
        f'postgresql+pg8000://{st.secrets["USER"]}:{st.secrets["PASSWORD"]}@'
        f'{st.secrets["HOST"]}:5432/{st.secrets["DATABASE"]}'
    )
    # Crear el motor de SQLAlchemy
    engine = create_engine(string_conection)
    query = f"""
            select evat.nombre_campo as campo,
                evat.piscina,
                evat.fecha_siembra,
                evat.fecha_muestreo,
                evat.ha,
                evat.dias_cultivo,
                evat.densidad_siembra_cam_m2 as densidad_siembra_ind_m2,
                evat.peso_siembra_gr,
                evat.peso_actual_gr,
                evat.alimento_diario_total as kgab_dia,
                evat.sobrevivencia,
                evat.alimento_acumulado,
                evat.sobrevivencia_actual_campo as porcentaje_sob_campo,
                evat.crecimiento_gr_semana,
                evat.crecimiento_lineal_semanal,
                evat.crecimiento_ultimas_4_semanas,
                evat.fca_campo_sin_biomasa_inicial as fca_campo,
                evat.peso_raleo_1,
                evat.peso_raleo_2,
                evat.peso_raleo_3,
                evat.biomasa_raleo_lb_ha_1,
                evat.biomasa_raleo_lb_ha_2,
                evat.biomasa_raleo_lb_ha_3,
                evat.tipo_alimento_std,
                evat.costos_fijos as costo_fijo_ha_dia,
                evat.precio_mix as costo_mix_alimento_kg,
                evat.precio_larva as costo_millar_larva,
                evat.capacidad_de_carga_lbs_ha,
                evat.sobrevivencia_consumo,
                cl.razon_social as cliente
                from productivo.evat_calculado_vista as evat
            left join cliente.cliente as cl
                on evat.codigo_cliente = cl.codigo
            where UPPER(cl.razon_social) = '{client_name}'
                and evat.fecha_siembra >= '2024-01-01'
                and evat.fecha_muestreo <= '{fecha_maxima_muestreo}'
                and evat.piscina not like '%PRE%'
                and evat.piscina = '{pool_proy_test}'
                        """
    print("Conexión exitosa")
    data_df = pd.read_sql_query(query, engine)

    return data_df


def get_bw_data(sheet_name: str) -> pd.DataFrame:
    dir_actual = os.getcwd()
    # print("Ruta del directorio actual:", dir_actual)
    ruta_excel = os.path.join(
        dir_actual, "app", "static", "data", "Bw_proyecciones_de_cosecha.xlsx"
    )
    ##validamos el sheetname
    # tomamos aglipesca como valor por defecto para validar
    sheet_name_normalized = "Aglipesca"
    if sheet_name == "MATORRILLOS":
        sheet_name_normalized = "Matorrillos"
    data_df = pd.read_excel(ruta_excel, sheet_name=sheet_name_normalized)
    return data_df
