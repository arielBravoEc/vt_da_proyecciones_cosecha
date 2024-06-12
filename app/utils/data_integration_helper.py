
def get_last(df):
    return df.iloc[-1]



def group_and_get_last_week_by_pool(data_df):
    data_df = data_df.sort_values(['id', 'fecha_muestreo'], ascending = [True, True])
    evat_ultima_semana_df = data_df.groupby('id').agg(
        { "campo": get_last, 
        "piscina": get_last,
        "fecha_siembra": get_last,
        "fecha_muestreo": get_last,
        "peso_siembra_gr": get_last,
        "dias_cultivo": get_last,
        "peso_actual_gr": get_last,
        "kgab_dia": get_last,
        "alimento_acumulado": get_last,
        "ha": get_last,
        "densidad_siembra_ind_m2": get_last,
        "porcentaje_sob_campo": get_last,
        "crecimiento_ultimas_4_semanas": get_last,
        "peso_raleo_1": 'max',
        "peso_raleo_2": 'max',
        "peso_raleo_3": 'max',
        "biomasa_raleo_lb_ha_1": 'max',
        "biomasa_raleo_lb_ha_2": 'max',
        "biomasa_raleo_lb_ha_3": 'max',
        "costo_fijo_ha_dia": get_last,
        "costo_mix_alimento_kg": get_last,
        "costo_millar_larva": get_last,
        'id_piscina': get_last,
        'tipo_alimento_std': get_last,
        'capacidad_de_carga_lbs_ha': get_last,
        })
    evat_ultima_semana_df = evat_ultima_semana_df.reset_index(drop=True)
    evat_ultima_semana_df = evat_ultima_semana_df.sort_values(['id_piscina', 'fecha_muestreo'], ascending = [True, True])
    evat_ultima_semana_df = evat_ultima_semana_df.groupby('id_piscina').agg(
        { 
        "campo": get_last, 
        "piscina": get_last,
        "fecha_siembra": get_last,
        "fecha_muestreo": get_last,
        "peso_siembra_gr": get_last,
        "dias_cultivo": get_last,
        "peso_actual_gr": get_last,
        "kgab_dia": get_last,
        "alimento_acumulado": get_last,
        "ha": get_last,
        "densidad_siembra_ind_m2": get_last,
        "porcentaje_sob_campo": get_last,
        "crecimiento_ultimas_4_semanas": get_last,
        "peso_raleo_1": get_last,
        "peso_raleo_2": get_last,
        "peso_raleo_3": get_last,
        "biomasa_raleo_lb_ha_1": get_last,
        "biomasa_raleo_lb_ha_2": get_last,
        "biomasa_raleo_lb_ha_3": get_last,
        "costo_fijo_ha_dia": get_last,
        "costo_mix_alimento_kg": get_last,
        "costo_millar_larva": get_last,
        'id_piscina': get_last,
        'tipo_alimento_std': get_last,
        'capacidad_de_carga_lbs_ha': get_last,
        })
    return evat_ultima_semana_df



