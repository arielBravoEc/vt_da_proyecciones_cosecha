# Función para obtener el valor normalizado de un diccionario
def obtener_valor_normalizado(clave: str, diccionario: dict) -> str:
    """
    Esta ``función`` obtiene el valor normalizado de un diccionario

    Args:
        clave (str): clave a buscar en el diccionario.
        diccionario (dict): diccionario en donde se va a buscar

    Returns:
        Retorna str
    """
    if clave in diccionario:
        return diccionario[clave]
    else:
        return clave
