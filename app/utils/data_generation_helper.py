import pandas as pd
import numpy as np
import math
from fpdf import FPDF
import io
import datetime
import pytz


# creamos id
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
    """
    price_df["Precios"] = price_df["Precios"].astype(float)
    # Verificar la presencia de las columnas necesarias
    required_columns = [
        "peso_raleo_1",
        "peso_raleo_2",
        "peso_raleo_3",
        "Peso final proyectado (gr)",
    ]
    missing_columns = [col for col in required_columns if col not in data_df.columns]
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
                # if type(actual_price) == int or type(actual_price) == float:
                # si es que el precio actual es numero (existian casos con "-")
                # el valor a agregar sería el precio por el porcentaje de la
                # distribucion de tallas
                # actual_porcentage = actual_price * ind[index_talla]
                actual_porcentage = actual_price * ind[index_talla]
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

    data_df["Precio venta Raleo 1 ($/kg)"] = data_df["peso_raleo_1"].apply(get_price)
    data_df["Precio venta Raleo 2 ($/kg)"] = data_df["peso_raleo_2"].apply(get_price)
    data_df["Precio venta Raleo 3 ($/kg)"] = data_df["peso_raleo_3"].apply(get_price)
    data_df["Precio venta pesca final ($/kg)"] = data_df[
        "Peso final proyectado (gr)"
    ].apply(get_price)
    data_df.loc[:, "Precio venta Raleo 1 ($/lb)"] = (
        data_df["Precio venta Raleo 1 ($/kg)"] / 2.2
    )
    data_df.loc[:, "Precio venta Raleo 2 ($/lb)"] = (
        data_df["Precio venta Raleo 2 ($/kg)"] / 2.2
    )
    data_df.loc[:, "Precio venta Raleo 3 ($/lb)"] = (
        data_df["Precio venta Raleo 3 ($/kg)"] / 2.2
    )
    data_df.loc[:, "Precio venta pesca final ($/lb)"] = (
        data_df["Precio venta pesca final ($/kg)"] / 2.2
    )

    return data_df


def generate_proyection(
    data_df,
    project_survival,
    project_duration,
    price_df: pd.DataFrame,
    distribution_df: pd.DataFrame,
    dias_ciclo_finales=None,
    is_using_lineal_feed=True,
    percentage_dynamical_feed=None,
):
    if not dias_ciclo_finales:
        data_df["Días restantes para cumplir proyecto"] = data_df[
            "Días faltantes para lograr el peso del proyecto"
        ]
    data_df["Peso final proyectado (gr)"] = (
        (data_df["Días restantes para cumplir proyecto"] / 7)
        * data_df["crecimiento_ultimas_4_semanas"]
    ) + data_df["peso_actual_gr"]
    if is_using_lineal_feed:
        data_df["Kilos AABB Totales para cumplir proyecto"] = (
            data_df["Días restantes para cumplir proyecto"] * data_df["kgab_dia"]
        ) + data_df["alimento_acumulado"]
    else:
        data_df["Kilos AABB Totales para cumplir proyecto"] = (
            data_df["Días restantes para cumplir proyecto"]
            * (data_df["kgab_dia"] * (1.0 + (percentage_dynamical_feed / 100)))
        ) + data_df["alimento_acumulado"]
    data_df["Mortalidad semanal"] = (
        (100 - (project_survival * 100)) / project_duration
    ) * 7
    data_df["Sobrevivencia final de ciclo proyecto (%)"] = (
        data_df["porcentaje_sob_campo"] * 100
    ) - (
        (data_df["Días restantes para cumplir proyecto"] / 7)
        * data_df["Mortalidad semanal"]
    )
    data_df["Biomasa proyecto (lb/ha)"] = (
        (data_df["Sobrevivencia final de ciclo proyecto (%)"] / 100)
        * (data_df["densidad_siembra_ind_m2"])
        * data_df["Peso final proyectado (gr)"]
        * 22
    )
    data_df["Biomas total proyecto (lb/ha)"] = (
        data_df["Biomasa proyecto (lb/ha)"]
        + data_df["biomasa_raleo_lb_ha_1"]
        + data_df["biomasa_raleo_lb_ha_2"]
        + data_df["biomasa_raleo_lb_ha_3"]
    )
    data_df["Biomas total proyecto (lb)"] = (
        data_df["Biomas total proyecto (lb/ha)"] * data_df["ha"]
    )
    data_df["FCA Proyecto"] = data_df["Kilos AABB Totales para cumplir proyecto"] / (
        data_df["Biomas total proyecto (lb)"] / 2.2046
    )
    if dias_ciclo_finales:
        data_df["Días de ciclo finales"] = (
            data_df["Días de ciclo finales"] + dias_ciclo_finales
        )
    else:
        data_df["Días de ciclo finales"] = (
            data_df["Días restantes para cumplir proyecto"] + data_df["dias_cultivo"]
        )
    # eliminamos los ciclos donde el dia de cultivo sea mayor al dia de la proyeccion
    data_df = data_df[data_df["Días de ciclo finales"] > data_df["dias_cultivo"]]
    data_df["Fecha estimada de cosecha"] = data_df["fecha_muestreo"] + pd.to_timedelta(
        data_df["Días restantes para cumplir proyecto"], unit="D"
    )
    # calculamos indicadores economicos para la proyeccion a cosecha
    data_df["Costo Fijo ($/Ha)"] = (
        data_df["costo_fijo_ha_dia"] * data_df["Días de ciclo finales"]
    )
    data_df["Costo de Larva ($/Ha)"] = data_df["costo_millar_larva"] * (
        data_df["densidad_siembra_ind_m2"] * 10
    )
    data_df["Costo Alimento ($/Ha/Ciclo)"] = (
        data_df["Kilos AABB Totales para cumplir proyecto"] / data_df["ha"]
    ) * data_df["costo_mix_alimento_kg"]
    data_df["Costo Total ($/Ha)"] = (
        data_df["Costo Fijo ($/Ha)"]
        + data_df["Costo de Larva ($/Ha)"]
        + data_df["Costo Alimento ($/Ha/Ciclo)"]
    )
    # geenramos el precio ponderado por peso
    data_df = generate_distribution_price_by_weight(data_df, price_df, distribution_df)
    data_df["Rendimiento planta (%)"] = 0.95
    data_df["Ingreso Total ($/Ha)"] = (
        (data_df["Precio venta Raleo 1 ($/lb)"] * data_df["biomasa_raleo_lb_ha_1"])
        + (data_df["Precio venta Raleo 2 ($/lb)"] * data_df["biomasa_raleo_lb_ha_2"])
        + (data_df["Precio venta Raleo 3 ($/lb)"] * data_df["biomasa_raleo_lb_ha_3"])
        + (
            data_df["Precio venta pesca final ($/lb)"]
            * data_df["Biomasa proyecto (lb/ha)"]
        )
    ) * data_df["Rendimiento planta (%)"]
    data_df["Total Costo x Libra ($/lb) Proyecto"] = (
        data_df["Costo Total ($/Ha)"] / data_df["Biomas total proyecto (lb/ha)"]
    )
    data_df["UP ($/Ha) Proyecto"] = (
        data_df["Ingreso Total ($/Ha)"] - data_df["Costo Total ($/Ha)"]
    )
    data_df["UP ($/Ha/Día) Proyecto"] = (
        data_df["UP ($/Ha) Proyecto"] / data_df["Días de ciclo finales"]
    )
    data_df["ROI Proyecto"] = (
        data_df["UP ($/Ha) Proyecto"] / data_df["Costo Total ($/Ha)"]
    )
    if not dias_ciclo_finales:
        data_df["tipo_proyeccion"] = "fecha estimada de cosecha"
    return data_df


class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "PROYECCIONES DE COSECHA", 0, 1, "C")

    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, 0, 1, "L")
        self.ln(10)

    def add_dataframe(self, df, col_widths_dict):
        self.set_font("Arial", size=8)
        # Obtener los nombres de las columnas y sus anchos
        columns = list(df.columns)
        col_widths = [
            col_widths_dict[col] if col in col_widths_dict else 30 for col in columns
        ]
        row_height = self.font_size * 1.5

        # Configuración de colores y estilos solo para el encabezado
        self.set_fill_color(200, 220, 255)  # color de fondo para el encabezado (RGB)
        self.set_text_color(0, 0, 0)  # color de texto para el encabezado (RGB)
        self.set_font("Arial", "B", 10)

        # Agregar los encabezados del DataFrame
        for i, col in enumerate(df.columns):
            self.cell(col_widths[i], row_height, col, border=1, fill=True, align="C")
        self.ln(row_height)

        # Restaurar colores y estilos por defecto para el contenido de las celdas
        self.set_fill_color(255, 255, 255)  # color de fondo blanco para el contenido
        self.set_text_color(0, 0, 0)  # color de texto negro para el contenido
        self.set_font("Arial", "", 8)

        # Agregar las filas del DataFrame
        for row in df.itertuples(index=False):
            for i, cell in enumerate(row):
                self.cell(col_widths[i], row_height, str(cell), border=1, align="C")
            self.ln(row_height)

    def calculate_col_widths(self, df):
        max_width = self.w - 2 * self.l_margin
        num_cols = len(df.columns)
        col_widths = []

        for col in df.columns:
            col_width = max_width / num_cols
            col_widths.append(col_width)

        return col_widths


# Función para exportar el DataFrame a PDF
def export_df_to_pdf(df):
    df_print = df.drop(
        columns=[
            "IsMax",
            "IsMax_Up",
            "aguaje",
            "tipo_proyeccion",
            "IsProjectWeight",
            "ROI(%)",
            "Precio venta pesca final ($/Kg)",
            "capacidad_de_carga_lbs_ha",
            "IsLoadCapacity",
        ]
    )
    df_print.rename(
        columns={
            "Fecha Estimada Cosecha": "Fecha Cosecha",
            "Sobrevivencia final": "Sob. Final",
            "Precio venta pesca final ($/Kg)": "Precio venta",
            "Piscina": "PS.",
        },
        inplace=True,
    )
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page(orientation="L")  # Establecer orientación horizontal ('L'andscape)
    ecuador_timezone = pytz.timezone("America/Guayaquil")
    # Obtener la fecha y hora actual en UTC
    now_utc = datetime.datetime.now(tz=pytz.utc)
    # Convertir la fecha y hora a la zona horaria de Ecuador
    now_ecuador = now_utc.astimezone(ecuador_timezone)
    # Obtener el nombre del mes en español
    nombre_mes = now_ecuador.strftime("%B")

    fecha_formateada = f"{now_ecuador.day} de {nombre_mes} {now_ecuador.year} a las {now_ecuador.strftime('%H:%M')}"
    pdf.chapter_title(fecha_formateada)
    col_widths_dict = {
        "Campo": 38,
        "PS.": 12,
        "ha": 16,
        "Fecha Cosecha": 28,
        "Días": 13,
        "Peso (gr)": 18,
        "Biomasa (lb/ha)": 29,
        "Biomasa Total (LB)": 34,
        "Sob. Final": 20,
        "FCA": 12,
        "Costo lb/camaron": 32,
        "UP($/ha/dia)": 25,
        # 'Precio venta final': 25
        # Añadir más columnas según sea necesario
    }
    pdf.add_dataframe(df_print, col_widths_dict)

    # Guardar el PDF en un buffer
    buffer = io.BytesIO()
    pdf_output = pdf.output(dest="S").encode("latin1")
    buffer.write(pdf_output)
    buffer.seek(0)
    return buffer


def export_to_csv(datos_df):
    # Convertir el DataFrame a CSV
    csv = datos_df.to_csv(index=False).encode("latin1")
    return csv


def to_excel(df):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, index=False, sheet_name="proyecciones")
    workbook = writer.book
    worksheet = writer.sheets["proyecciones"]
    format1 = workbook.add_format({"num_format": "0.00"})
    worksheet.set_column("A:A", None, format1)
    writer.close()
    processed_data = output.getvalue()
    return processed_data


def export_to_xlsx(datos_df):
    # Convertir el DataFrame a CSV
    excel = to_excel(datos_df)
    return excel
