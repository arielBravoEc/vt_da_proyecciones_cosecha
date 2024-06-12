
import pandas as pd
import numpy as np
import math
from constants.general import VARIABLES_INTERES
from fpdf import FPDF
import base64
### creamos id
def get_id(Campo, Ps, FechaSiembra):
    return Campo + "-" + str(Ps) + "-" + str(FechaSiembra)[0:10]
def get_id_ps(Campo, Ps):
    return Campo + "-" + str(Ps)


def generate_distribution_price_by_weight(
        data_df: pd.DataFrame,
        price_df: pd.DataFrame,
        distribution_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
            Esta ``función``  retorna el precio de venta del camaron basado en la
            distribución por peso

            Args:
                data_df (Pandas dataframe): Datos del bench.
                price_df (Pandas dataframe): Datos con el precio en kg por talla
                distribution_df (Pandas dataframe): Datos con información de
                cada peso, que porcentaje de talla le pertenece
                para calcular su precio ponderado
            Raises:
                ValueError: Si faltan columnas requeridas en el DataFrame.
            Returns:
                Retorna el dataframe con el precio en lbs y kgs  de acuerdo al
                peso del camaron
            Todo: Validar y obtener el precio de venta cuando se tengan raleos
        """
        price_df['Precios'] = price_df['Precios'].astype(float)
        # Verificar la presencia de las columnas necesarias
        required_columns = ["peso_raleo_1", 'peso_raleo_2', 'peso_raleo_3', 'Peso final proyectado (gr)']
        missing_columns = [
            col for col in required_columns if col not in data_df.columns
        ]
        if missing_columns:
            raise ValueError(
                f"Faltan las siguientes columnas requeridas: "
                f"{', '.join(missing_columns)}"
            )
        precio_ponderado_df = pd.DataFrame(columns=["GRAMOS", "Precio Ponderado $ Kg"])
        tallas = distribution_df.columns
        # Con este ciclo for iteramos y encontramos por cada gramo cual es su precio
        # ponderado
        # Esto basado en los precios actuales y la distribucion por cada gramo
        for index, ind in distribution_df.iterrows():
            Precio_ponderado_kg = 0
            # iteramos desde el index 1, debido a que el index 0 es para los gramos
            index_talla = 1
            # iteramos las tallas que se tiene en la data_df
            while index_talla < len(tallas):
                # mientras el index sea menor a la longitud del array
                if not (math.isnan(ind[index_talla])):
                    # si la talla  no es falsa (es decir existe el porcentaje):
                    # buscamos su precio actual
                    actual_price = price_df[price_df["Tallas"] == tallas[index_talla]]
                    
                    actual_price = actual_price.iloc[0]["Precios"]
                    # definimos como inicial 0 al actual porcentaje para la sumatoria
                    
                    actual_porcentage = 0
                    #print(type(actual_price))
                    #if type(actual_price) == int or type(actual_price) == float:
                        # si es que el precio actual es numero (existian casos con "-")
                        # el valor a agregar sería el precio por el porcentaje de la
                        # distribucion de tallas
                        #actual_porcentage = actual_price * ind[index_talla]
                    actual_porcentage = actual_price * ind[index_talla]
                        
                    # print(actual_porcentage)
                    # sumamos la distrribucion para obtener el ponderado en cada gramaje
                    Precio_ponderado_kg = Precio_ponderado_kg + actual_porcentage
                    # aumentamos el index para ver las demas tallas
                        
                index_talla = index_talla + 1
            # una vez revisamos el porcentaje de todas las tallas, agregamos
            # el ponderado al df final
            new_row = {
                "GRAMOS": [ind["GRAMOS"]],
                "Precio Ponderado $ Kg": Precio_ponderado_kg,
            }
            precio_ponderado_df = pd.concat(
                [precio_ponderado_df, pd.DataFrame(new_row)], ignore_index=True
            )
        #print(precio_ponderado_df)

        def find_closest_values(s, x):
            # con esta funcion obtenemos el valor entero mas cercano de un float
            idx = (np.abs(s - x)).argmin()
            return s[idx]

        def get_price(weight):
            # obtenemos el precio de venta en base a las funciones creadas
            if (weight == 0) or math.isnan(weight):
                # si no hay retornamos 0 => útil cuando se trabaja con raleos
                return 0
            else:
                closest_weight = find_closest_values(
                    pd.to_numeric(precio_ponderado_df["GRAMOS"]), weight
                )
                price = precio_ponderado_df[
                    precio_ponderado_df["GRAMOS"] == closest_weight
                ].iloc[0][1]
                return price

        data_df['Precio venta Raleo 1 ($/kg)'] = data_df['peso_raleo_1'].apply(get_price)
        data_df['Precio venta Raleo 2 ($/kg)'] = data_df['peso_raleo_2'].apply(get_price)
        data_df['Precio venta Raleo 3 ($/kg)'] = data_df['peso_raleo_3'].apply(get_price)
        data_df['Precio venta pesca final ($/kg)'] = data_df['Peso final proyectado (gr)'].apply(get_price)
        data_df['Precio venta Raleo 1 ($/lb)'] = data_df['Precio venta Raleo 1 ($/kg)']/2.2
        data_df['Precio venta Raleo 2 ($/lb)'] = data_df['Precio venta Raleo 2 ($/kg)']/2.2
        data_df['Precio venta Raleo 3 ($/lb)'] = data_df['Precio venta Raleo 3 ($/kg)']/2.2
        data_df['Precio venta pesca final ($/lb)'] = data_df['Precio venta pesca final ($/kg)']/2.2

        return data_df


def generate_proyection(data_df, project_survival, project_duration,price_df: pd.DataFrame,
        distribution_df: pd.DataFrame,dias_ciclo_finales = None):
    if not dias_ciclo_finales:
        data_df['Días restantes para cumplir proyecto'] = data_df['Días faltantes para lograr el peso del proyecto']
    data_df['Peso final proyectado (gr)'] = ((data_df['Días restantes para cumplir proyecto']/7)* data_df['crecimiento_ultimas_4_semanas']) + data_df['peso_actual_gr']
    data_df['Kilos AABB Totales para cumplir proyecto'] = (data_df['Días restantes para cumplir proyecto']*data_df['kgab_dia']) + data_df['alimento_acumulado']
    data_df['Mortalidad semanal'] = ((100 - (project_survival*100))/project_duration)*7
    data_df['Sobrevivencia final de ciclo proyecto (%)'] = (data_df['porcentaje_sob_campo']*100) - ((data_df['Días restantes para cumplir proyecto']/7)* data_df['Mortalidad semanal'])
    data_df['Biomasa proyecto (lb/ha)'] = (data_df['Sobrevivencia final de ciclo proyecto (%)']/100)*(data_df['densidad_siembra_ind_m2'])*data_df['Peso final proyectado (gr)']*22
    data_df['Biomas total proyecto (lb/ha)'] = data_df['Biomasa proyecto (lb/ha)'] + data_df['biomasa_raleo_lb_ha_1'] + data_df['biomasa_raleo_lb_ha_2'] + data_df['biomasa_raleo_lb_ha_3']
    data_df['Biomas total proyecto (lb)'] = data_df['Biomas total proyecto (lb/ha)']*data_df['ha']
    data_df['FCA Proyecto'] = data_df['Kilos AABB Totales para cumplir proyecto']/(data_df['Biomas total proyecto (lb)']/2.2046)
    if dias_ciclo_finales:
        data_df['Días de ciclo finales'] = data_df['Días de ciclo finales'] + dias_ciclo_finales
    else:
        data_df['Días de ciclo finales'] = data_df['Días restantes para cumplir proyecto'] + data_df['dias_cultivo']
    # eliminamos los ciclos donde el dia de cultivo sea mayor al dia de la proyeccion
    data_df = data_df[data_df['Días de ciclo finales'] > data_df['dias_cultivo']]
    data_df['Fecha estimada de cosecha'] = data_df['fecha_muestreo']  + pd.to_timedelta(data_df['Días restantes para cumplir proyecto'], unit='D')
    ## calculamos indicadores economicos para la proyeccion a cosecha
    data_df['Costo Fijo ($/Ha)'] = data_df['costo_fijo_ha_dia'] * data_df['Días de ciclo finales']
    data_df['Costo de Larva ($/Ha)'] = data_df['costo_millar_larva']* (data_df['densidad_siembra_ind_m2']*10)
    data_df['Costo Alimento ($/Ha/Ciclo)'] = (data_df['Kilos AABB Totales para cumplir proyecto']/data_df['ha'])*data_df['costo_mix_alimento_kg']
    data_df['Costo Total ($/Ha)'] = data_df['Costo Fijo ($/Ha)'] + data_df['Costo de Larva ($/Ha)'] + data_df['Costo Alimento ($/Ha/Ciclo)']
    # geenramos el precio ponderado por peso
    data_df = generate_distribution_price_by_weight(data_df,price_df,distribution_df)
    data_df['Rendimiento planta (%)'] = 0.95
    data_df['Ingreso Total ($/Ha)'] = ((data_df['Precio venta Raleo 1 ($/lb)']*data_df['biomasa_raleo_lb_ha_1']) + (data_df['Precio venta Raleo 2 ($/lb)']*data_df['biomasa_raleo_lb_ha_2']) +(data_df['Precio venta Raleo 3 ($/lb)']*data_df['biomasa_raleo_lb_ha_3'])+(data_df['Precio venta pesca final ($/lb)']*data_df['Biomasa proyecto (lb/ha)']))*data_df['Rendimiento planta (%)']
    data_df['Total Costo x Libra ($/lb) Proyecto'] = data_df['Costo Total ($/Ha)']/data_df['Biomas total proyecto (lb/ha)']
    data_df['UP ($/Ha) Proyecto'] = data_df['Ingreso Total ($/Ha)'] - data_df['Costo Total ($/Ha)']
    data_df['UP ($/Ha/Día) Proyecto'] = data_df['UP ($/Ha) Proyecto'] / data_df['Días de ciclo finales']
    data_df['ROI Proyecto'] = data_df['UP ($/Ha) Proyecto'] / data_df['Costo Total ($/Ha)']
    if not dias_ciclo_finales:
        data_df['tipo_proyeccion'] = 'fecha estimada de cosecha'
    return data_df


# Función para exportar el DataFrame a PDF
def export_df_to_pdf(df, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Ancho de las celdas
    col_width = pdf.w / (len(df.columns) + 1)
    
    # Agregar los nombres de las columnas
    for col in df.columns:
        pdf.cell(40, 10, col, 1)
    pdf.ln()
    
    
    # Agregar las filas del DataFrame
    for index, row in df.iterrows():
        for col in df.columns:
            pdf.cell(col_width, 10, str(row[col]), border=1)
        pdf.ln()
    
    # Guardar el PDF
    pdf.output(filename)

def export_df_to_pdfv2(df, filename):
    df_print = df.drop(columns=["IsMax", 'IsMax_Up', 'aguaje'])
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=8)
    # Ancho de las celdas
    col_width = pdf.w / (len(df_print.columns) + 1)
    
    # Agregar los nombres de las columnas
    for col in df_print.columns:
        pdf.cell(col_width, 10, col, 1)
    pdf.ln()
    
    # Agregar las filas del DataFrame
    for index, row in df_print.iterrows():
        for col in df_print.columns:
            pdf.cell(col_width, 10, str(row[col]), 1)
        pdf.ln()
    
    # Guardar el PDF en bytes
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    
    # Descargar el archivo usando base64
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Descargar PDF</a>'
    return href