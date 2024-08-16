import pandas as pd
from datetime import datetime, timedelta

DIAS_PROYECTO = 90
SOB_PROYECTO = 0.75
PESO_PROYECTO = 28.0
COSTO_MILLAR = 3.50
COSTO_MIX = 1.29
COSTO_FIJO = 30.0
RANGO_PROYECCION = 0
FARM_NAME = "CAMARONES NATURISA"  #
CLIENT_NAME_EVAT = "G. SIXTO EGUIGUREN"  # "G. NATURISA" | "G. PESFALAN" |
CLIENT_NAME_BENCH = "SIXTO EGUIGUREN"  # "NATURISA" | G. PESFALAN | 'SIXTO EGUIGUREN'
SOBREVIVENCIA_CAMPO = True
PORCENTAJE_SOB = 0
PORCENTAJE_AB = 0
# Crear un diccionario con los datos
prices = {
    "Precios": [3.60, 3.40, 3.25, 3.10, 2.70, 2.40, 2.30, 2.00, 1.80],
    "Tallas": [
        "20 - 30",
        "30 - 40",
        "40 - 50",
        "50 - 60",
        "60 - 70",
        "70 - 80",
        "80 - 100",
        "100-120",
        "120-140",
    ],
}

# Crear el DataFrame
PRICES_DF = pd.DataFrame(prices)
FECHA_ACTUAL = datetime.now() - timedelta(days=110)
# FECHA MINIMA DEL ULTIMO DATO: ES DECIR SI UNA PISCINA ESTá CON SU ULTIMO DATO
# MAS DE N DIAS DESACTUALIZADO, NO SE LO TOMA EN CUENTA A ESA PISCINA PARA LA PROY
# FECHA_MINIMA_ULTIMO_DATO = (FECHA_ACTUAL - timedelta(days=30)).strftime("%Y-%m-%d")
FECHA_MINIMA_ULTIMO_DATO = "2024-04-15"
MINIMO_DIAS_PROYECTO = 40
