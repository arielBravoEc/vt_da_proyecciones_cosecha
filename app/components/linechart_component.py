
import streamlit as st
import altair as alt
def plot_line_chart(data_df, variable):
    min_dia = data_df[data_df['Piscina'] == st.session_state.pool_selection]['Días'].min() - 1
    max_dia = data_df[data_df['Piscina'] == st.session_state.pool_selection]['Días'].max() + 1
    dias_values = list(range(min_dia, max_dia + 1))
    line_chart = alt.Chart(data_df[data_df['Piscina'] == st.session_state.pool_selection]).mark_line(size=3, color="#884DE3").encode(
    x=alt.X('Días', axis=alt.Axis(title='Días', values=dias_values, titleFontSize=18, labelFontSize=15)),
    y=alt.Y(variable, axis=alt.Axis(titleFontSize=18, labelFontSize=15)),
    tooltip=['Días', "UP($/ha/dia)", "ROI(%)", 'Costo lb/camaron']
    )
        # Agregar markers a la línea
    points = line_chart.mark_point(size=80, color="#884DE3", filled=True).encode(
    x='Días',
    y=variable
    )
    chart = (line_chart + points).interactive()
    cols_plot = st.columns([1])
    with cols_plot[0]:
        st.altair_chart(chart, use_container_width=True)
