import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from utils.data_generation_helper import export_df_to_pdf, export_to_csv, export_to_xlsx
from constants.graphs_constants import PLOT_MAPPING_VARIABLES_NAME


def show_modal() -> None:
    """
    Esta ``función`` muestra el contenido del modal
    cuando se haga click en abrir selección
    Args: None
    Raises:
        ValueError: Si faltan columnas requeridas en el DataFrame.
    Returns:
        Retorna None
    """
    # creamos una copia para trabaja en ella
    data_df_modal = st.session_state.selected_rows.copy()
    # eliminamos columnas que no necesitamos
    data_df_modal = data_df_modal.drop(
        [
            "aguaje",
            "IsMax",
            "IsMax_Up",
            "IsProjectWeight",
            "roi_proyecto",
            "capacidad_de_carga_lbs_ha",
            "IsLoadCapacity",
        ],
        axis=1,
    )
    # renombramos columnas para mostrar en la tabla y cuando guardamos
    existing_columns = {
        k: v
        for k, v in PLOT_MAPPING_VARIABLES_NAME.items()
        if k in data_df_modal.columns
    }
    data_df_modal = data_df_modal = data_df_modal.rename(columns=existing_columns)
    st.dataframe(data_df_modal)
    # creamos el buffer para exportar como pdf
    buffer = export_df_to_pdf(data_df_modal)
    dowload_button = st.columns(7)
    with dowload_button[0]:
        with stylable_container(
            key="container_with_border_button_pdf",
            css_styles=r"""
                    button p:before {
                        font-family: 'Font Awesome 5 Free';
                        content: '\f1c1';
                        display: inline-block;
                        padding-right: 3px;
                        padding-left: 3px;
                        vertical-align: middle;
                        font-weight: 900;
                    }
                    """,
        ):
            st.download_button(
                label="Descargar PDF",
                data=buffer,
                file_name="proyecciones.pdf",
                mime="application/pdf",
            )
    with dowload_button[1]:
        with stylable_container(
            key="container_with_border_button_csv",
            css_styles=r"""
                    button p:before {
                        font-family: 'Font Awesome 5 Free';
                        content: '\f6dd';
                        display: inline-block;
                        padding-right: 3px;
                        padding-left: 3px;
                        vertical-align: middle;
                        font-weight: 900;
                    }
                    """,
        ):
            st.download_button(
                label="Descargar CSV",
                data=export_to_csv(data_df_modal),
                file_name="proyecciones.csv",
                mime="text/csv",
            )
    with dowload_button[2]:
        with stylable_container(
            key="container_with_border_button_excel",
            css_styles=r"""
                    button p:before {
                        font-family: 'Font Awesome 5 Free';
                        content: '\f1c3';
                        display: inline-block;
                        padding-right: 3px;
                        padding-left: 3px;
                        vertical-align: middle;
                        font-weight: 900;
                    }
                    """,
        ):
            st.download_button(
                label="Descargar Excel",
                data=export_to_xlsx(data_df_modal),
                file_name="proyecciones.xlsx",
                mime="text/xlsx",
            )
