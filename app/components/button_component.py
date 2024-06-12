from streamlit_extras.stylable_container import stylable_container
import streamlit as st

def get_button_with_icon(icon_title, icon_code=None):
    with stylable_container(
    key="container_with_border",
    css_styles=f"""
        button p:before {{
            font-family: 'Font Awesome 5 Free';
            content: {icon_code};
            display: inline-block;
            padding-right: 3px;
            padding-left: 3px;
            vertical-align: middle;
            font-weight: 900;
        }}
        """,
    ):
        a = st.button(icon_title)
        return a