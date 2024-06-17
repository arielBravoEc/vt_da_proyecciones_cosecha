import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from utils.data_generation_helper import export_df_to_pdf, export_to_csv, export_to_xlsx


def show_modal():
    st.dataframe(
        st.session_state.selected_rows.drop(
            [
                "aguaje",
                "IsMax",
                "IsMax_Up",
                "IsProjectWeight",
                "ROI(%)",
                "capacidad_de_carga_lbs_ha",
                "IsLoadCapacity",
            ],
            axis=1,
        )
    )
    # Crear un botón para exportar el DataFrame a PDF
    # if st.button('Exportar a PDF'):
    # export_df_to_pdf(st.session_state.selected_rows, 'proyecciones.pdf')

    buffer = export_df_to_pdf(st.session_state.selected_rows)
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
                data=export_to_csv(
                    st.session_state.selected_rows.drop(
                        [
                            "IsMax",
                            "IsMax_Up",
                            "IsProjectWeight",
                            "ROI(%)",
                            "IsLoadCapacity",
                        ],
                        axis=1,
                    )
                ),
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
                data=export_to_xlsx(
                    st.session_state.selected_rows.drop(
                        [
                            "IsMax",
                            "IsMax_Up",
                            "IsProjectWeight",
                            "ROI(%)",
                            "IsLoadCapacity",
                        ],
                        axis=1,
                    )
                ),
                file_name="proyecciones.xlsx",
                mime="text/xlsx",
            )
