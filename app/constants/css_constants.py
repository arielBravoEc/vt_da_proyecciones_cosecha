# Define el background de la app
BACKGROUND_COLOR = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: #F6F7FC; /* Aquí puedes poner el color que desees */
    background-image: none;
}
</style>
"""

# Define el CSS para las cards
CARD_CSS = """
<style>
.card {
    background-color: #ffffff; /* Color de fondo blanco */
    border-radius: 10px; /* Bordes redondeados */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Sombra */
    margin: 20px 0; /* Espaciado entre tarjetas */
    padding: 20px; /* Espaciado interno */
    transition: transform 0.2s; /* Transición suave */
}

.card:hover {
    transform: translateY(-10px); /* Efecto hover */
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2); /* Sombra más intensa al hacer hover */
}

.card-title {
    font-size: 24px; /* Tamaño del título */
    font-weight: bold; /* Negrita */
    margin-bottom: 10px; /* Espaciado inferior */
}

.card-content {
    font-size: 16px; /* Tamaño del contenido */
    color: #333; /* Color del texto */
}

.card-footer {
    display: flex; /* Flexbox para el pie de la tarjeta */
    justify-content: flex-end; /* Alinear al final */
    margin-top: 20px; /* Espaciado superior */
}

.card-button {
    padding: 10px 20px; /* Espaciado interno del botón */
    background-color: #007bff; /* Color de fondo del botón */
    color: #fff; /* Color del texto del botón */
    border: none; /* Sin bordes */
    border-radius: 5px; /* Bordes redondeados del botón */
    text-decoration: none; /* Sin subrayado */
    cursor: pointer; /* Cursor de puntero */
    transition: background-color 0.2s; /* Transición suave */
}

.card-button:hover {
    background-color: #0056b3; /* Color de fondo del botón al hacer hover */
}
</style>
"""

CARD_CSS_V2 = """
<style>
.card {
    background-color: #ffffff;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    padding: 20px;
    margin-bottom: 20px;
}

.card-title {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
}

.icon {
    width: 30px;
    height: 30px;
    margin-right: 10px;
}
</style>
"""

CONTAINER_CSS = """
<style>
/* Selector para el fondo del contenedor */
body {
    background-color: #f0f0f0 !important;  /* Color de fondo */
}
</style>
"""

PRIMARY_COLOR = "#884de3"
PRIMARY_COLOR_BACKGROUND = "rgba(136, 77, 227, 0.2)"

TABLE_STYLE = {
    ".ag-theme-streamlit .ag-row-hover": {
        "background-color": f"{PRIMARY_COLOR_BACKGROUND} !important"
    },
    ".ag-theme-streamlit .ag-menu-option:hover": {
        # Cambia este valor al color morado que desees para el hover del menú
        "background-color": f"{PRIMARY_COLOR_BACKGROUND} !important",
    },
    ".ag-header-cell-menu-button:hover": {"color": f"{PRIMARY_COLOR} !important"},
    ".ag-checkbox-input-wrapper.ag-checked:after": {
        # Cambia el color del borde del checkbox
        "color": f"{PRIMARY_COLOR} !important"
    },
    ".ag-tab-selected": {
        # Cambia el color del borde del checkbox
        "border-bottom-color": f"{PRIMARY_COLOR} !important"
    },
}
