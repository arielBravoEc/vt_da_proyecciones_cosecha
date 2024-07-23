import streamlit as st
import altair as alt


def plot_line_chart(data_df, variable):
    min_dia = (
        data_df[data_df["Piscina"] == st.session_state.pool_selection]["Días"].min() - 1
    )
    max_dia = (
        data_df[data_df["Piscina"] == st.session_state.pool_selection]["Días"].max() + 1
    )
    dias_values = list(range(min_dia, max_dia + 1))
    line_chart = (
        alt.Chart(data_df[data_df["Piscina"] == st.session_state.pool_selection])
        .mark_line(size=3, color="#884DE3")
        .encode(
            x=alt.X(
                "Días",
                axis=alt.Axis(
                    title="Días", values=dias_values, titleFontSize=18, labelFontSize=15
                ),
            ),
            y=alt.Y(variable, axis=alt.Axis(titleFontSize=18, labelFontSize=15)),
            tooltip=["Días", "UP($/ha/dia)", "ROI(%)", "Costo lb/camaron"],
        )
    )
    # Agregar markers a la línea
    points = line_chart.mark_point(size=80, color="#884DE3", filled=True).encode(
        x="Días", y=variable
    )
    chart = (line_chart + points).interactive()
    cols_plot = st.columns([1])
    with cols_plot[0]:
        st.altair_chart(chart, use_container_width=True)

def plot_line_chart_with_two_axis(data_df, variable_axis_1, variable_axis2):
    min_dia = (
        data_df[data_df["Piscina"] == st.session_state.pool_selection]["Días"].min() - 1
    )
    max_dia = (
        data_df[data_df["Piscina"] == st.session_state.pool_selection]["Días"].max() + 1
    )
    dias_values = list(range(min_dia, max_dia + 1))
    
    base_chart = alt.Chart(data_df[data_df["Piscina"] == st.session_state.pool_selection]).encode(
        x=alt.X(
            "Días",
            axis=alt.Axis(
                title="Días", values=dias_values, titleFontSize=18, labelFontSize=15
            ),
        ),
        tooltip=["Días", "UP($/ha/dia)", "ROI(%)", "Costo lb/camaron"],
    )
    
    line_chart1 = base_chart.mark_line(size=3, color="#884DE3").encode(
        y=alt.Y(variable_axis_1, axis=alt.Axis(title=variable_axis_1, titleColor="#884DE3", titleFontSize=18, labelFontSize=15)),
    )

    points1 = line_chart1.mark_point(color="#884DE3", filled=True).encode(
        y=variable_axis_1,
        size=alt.Size('ROI(%)', legend=None)
    )

    line_chart2 = base_chart.mark_line(size=3, color="#0C3EE4").encode(
        y=alt.Y(variable_axis2, axis=alt.Axis(title=variable_axis2, titleColor="#0C3EE4", titleFontSize=18, labelFontSize=15, orient='right')),
        
    )

    points2 = line_chart2.mark_point( color="#0C3EE4", filled=True).encode(
        y=variable_axis2,
        size=alt.Size('ROI(%)', legend=None)
    )

    # Create separate charts and combine them
    chart1 = (line_chart1 + points1).properties()
    chart2 = (line_chart2 + points2).properties()

    # Use layer and adjust resolve to handle independent axes
    combined_chart = alt.layer(
        chart1, chart2
    ).resolve_scale(
        y='independent'
    ).interactive()
    
    cols_plot = st.columns([1])
    with cols_plot[0]:
        st.altair_chart(combined_chart, use_container_width=True)

