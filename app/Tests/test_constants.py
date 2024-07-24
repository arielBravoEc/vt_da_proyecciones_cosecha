import pandas as pd
from datetime import datetime, timedelta
DIAS_PROYECTO = 90
SOB_PROYECTO = 0.60
PESO_PROYECTO = 30.0
COSTO_MILLAR = 5.0
COSTO_MIX = 1.12
COSTO_FIJO = 30.0
RANGO_PROYECCION = 21
FARM_NAME = "CAMARONES NATURISA" # 
CLIENT_NAME_EVAT = "G. PESFALAN" # "G. NATURISA" | "G. PESFALAN"
CLIENT_NAME_BENCH = "G. PESFALAN" # "NATURISA" | G. PESFALAN
SOBREVIVENCIA_CAMPO=True
PORCENTAJE_SOB = 0
PORCENTAJE_AB  = 0
# Crear un diccionario con los datos
prices = {
    'Precios': [3.60, 3.30, 3.10, 3.05,2.70,2.40,2.30,2.00,1.80],
    'Tallas': ['20 - 30', '30 - 40', '40 - 50', '50 - 60', '60 - 70', '70 - 80', '80 - 100', '100-120', '120-140' ],
}

# Crear el DataFrame
PRICES_DF = pd.DataFrame(prices)
FECHA_ACTUAL = datetime.now() - timedelta(days=90)
# FECHA MINIMA DEL ULTIMO DATO: ES DECIR SI UNA PISCINA ESTá CON SU ULTIMO DATO
# MAS DE N DIAS DESACTUALIZADO, NO SE LO TOMA EN CUENTA A ESA PISCINA PARA LA PROY
FECHA_MINIMA_ULTIMO_DATO = (FECHA_ACTUAL - timedelta(days=30)).strftime("%Y-%m-%d")

MINIMO_DIAS_PROYECTO = 40