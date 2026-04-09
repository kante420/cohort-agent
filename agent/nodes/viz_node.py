from viz.charts import build_chart

def viz_node(state: dict) -> dict:
    """
    Recibe el state tras sql_node y añade una figura Plotly si hay datos.
    Si no hay datos o la gráfica no aplica, devuelve chart=None.
    """
    df       = state.get("query_result", None) #Buscamos en state el resultado de la consulta SQL (DataFrame df)
    question = state.get("user_question", "") #Recupera la pregunta original del usuario -> Para saber que gráfico usar

    if df is None or df.empty: #Si el nodo anterior no encontró datos -> chart=None
        return {**state, "chart": None}

    fig = build_chart(df, question=question) #Pasamos la lógica a la función build_chart
    return {**state, "chart": fig}