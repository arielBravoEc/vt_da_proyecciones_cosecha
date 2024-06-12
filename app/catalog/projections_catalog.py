import psycopg2
import pandas as pd
import os



def get_evat_data(farm_name):
    #CREDENCIALES
    print("Intentando conectarse a la base de datos")
    conexion = psycopg2.connect(host="35.237.206.192", database="db-vtp-nic-prd", user="analytics_read", password="ufG!4%#8R$") # conexion remota
    print("Conexión exitosa")
    data_df = pd.read_sql_query(f"""
            select evat.nombre_campo as campo,
                evat.piscina,
                evat.fecha_siembra,
                evat.fecha_muestreo,
                evat.ha,
                evat.dias_cultivo,
                evat.densidad_siembra_cam_m2 as densidad_siembra_ind_m2,
                evat.peso_siembra_gr,
                evat.peso_actual_gr,
                evat.kg_ab_ha_campo as kgab_dia,
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
                cl.razon_social as cliente
                from productivo.evat_calculado_vista as evat  
			left join cliente.cliente as cl 
	   			on evat.codigo_cliente = cl.codigo
            where UPPER(evat.nombre_campo) = '{farm_name}'
                and evat.fecha_siembra >= '2024-01-01' 
                and evat.piscina not like '%PRE%'
                        """
        , con=conexion) 
    return data_df


def get_excel_data(sheet_name=None, skiprows=None, usecols=None):
    dir_actual = os.getcwd()
    print("Ruta del directorio actual:", dir_actual)
    ruta_excel = os.path.join(dir_actual, "app", "static", "data", "datos_evatv2.xlsm")
    data_df = pd.read_excel(ruta_excel, sheet_name=sheet_name, skiprows=skiprows, usecols=usecols)
    return data_df
