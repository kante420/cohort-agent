import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import Figure

#Decidimos que tipo de gráfica encaja mejor con los datos que tenemos
def detect_chart_type(df: pd.DataFrame, question: str = "") -> str:
    if df is None or df.empty:
        return "none"

    cols = df.columns.tolist()
    n_cols = len(cols)
    question_lower = question.lower()

    if len(df) == 1 and n_cols == 1:
        return "none"

    if cols == ["PacienteID"] or cols == ["pacienteid"]:
        return "none"

    text_cols = [c for c in cols if pd.api.types.is_string_dtype(df[c])
                 or pd.api.types.is_object_dtype(df[c])]
    num_cols  = [c for c in cols if pd.api.types.is_numeric_dtype(df[c])]
    date_cols = [c for c in cols if pd.api.types.is_datetime64_any_dtype(df[c])
                 or any(k in c.lower() for k in ["fecha", "date", "año", "mes"])]

    wants_pie  = any(k in question_lower for k in [
        "distribución", "proporción", "porcentaje", "%",
        "quesito", "tarta", "pie", "reparto"
    ])
    wants_hist = any(k in question_lower for k in [
        "distribución de edad", "distribución de las edad",
        "histograma", "rango de edad"
    ])
    wants_line = any(k in question_lower for k in [
        "evolución", "tendencia", "tiempo", "histórico", "por año", "por mes"
    ])

    if date_cols and num_cols:
        return "line"
    if wants_line and num_cols:
        return "line"

    # Histograma explícito
    if wants_hist and num_cols:
        return "histogram"

    if n_cols == 1 and num_cols:
        return "histogram"

    if text_cols and num_cols:
        n_categorias = df[text_cols[0]].nunique()

        #PieChart solo si se pide explícitamente o hay exactamente 2 categorías y la pregunta habla de porcentaje/distribución
        if wants_pie and n_categorias <= 6:
            return "pie"
        if n_categorias == 2 and wants_pie:
            return "pie"

        #BarChart para todo lo demás
        return "bar"

    if n_cols >= 2 and num_cols:
        return "bar"

    return "table"

#Una vez definido el tipo de gráfica -> Generamos la gráfica
def build_chart(df: pd.DataFrame, question: str = "", title: str = "") -> Figure | None:
    if df is None or df.empty:
        return None
    
    cols = df.columns.tolist()
    n_cols = len(cols)

    #Si solo hay una fila y una columna numérica, no tiene sentido hacer gráfica
    if len(df) == 1 and len(df.columns) == 1:
        return None

    #Si solo hay una fila y una columna, no tiene sentido graficar
    if len(df) == 1 and n_cols == 1:
        return "none"

    #Si la única columna es PacienteID, es una lista de IDs, no tiene sentido graficar
    if cols == ["PacienteID"] or cols == ["pacienteid"]:
        return "none"

    chart_type = detect_chart_type(df, question)

    text_cols = [c for c in cols if pd.api.types.is_string_dtype(df[c])
             or pd.api.types.is_object_dtype(df[c])]    
    num_cols   = [c for c in cols if pd.api.types.is_numeric_dtype(df[c])]
    date_cols  = [c for c in cols if any(k in c.lower() for k in ["fecha", "date"])]

    chart_title = title

    if chart_type == "bar" and text_cols and num_cols:
        fig = px.bar(
            df,
            x=text_cols[0],
            y=num_cols[0],
            title=chart_title,
            color=num_cols[0],                          #Color por valor
            color_continuous_scale="teal",              #Escala de color
            text=num_cols[0]                            #Valor encima de cada barra
        )
        fig.update_traces(textposition='outside')
        fig.update_yaxes(tickmode='linear', dtick=1)
        fig.update_layout(coloraxis_showscale=False)    #Oculta la barra de color lateral

    elif chart_type == "pie" and text_cols and num_cols:
        fig = px.pie(df,names=text_cols[0],values=num_cols[0],title=chart_title,color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_traces(textposition='inside', textinfo='percent+label', pull=[0.05] * len(df), rotation=45)

    elif chart_type == "line":
        #Detecta columna de año por nombre
        year_cols = [c for c in cols if any(k in c.lower() for k in ["año", "anio", "year", "fecha"])]
    
        if year_cols:
            x_col = year_cols[0]
            y_col = [c for c in num_cols if c != x_col][0] if len(num_cols) > 1 else num_cols[0]
        elif date_cols:
            x_col = date_cols[0]
            y_col = num_cols[0] if num_cols else cols[1]
        elif text_cols:
            x_col = text_cols[0]
            y_col = num_cols[0] if num_cols else cols[1]
        else:
            x_col = cols[0]
            y_col = cols[1] if len(cols) > 1 else cols[0]

        #Corrige etiqueta Año
        x_label = x_col.replace("Anio", "Año").replace("anio", "Año").replace("ano", "Año").replace("Ano", "Año")

        y_max = df[y_col].max()
        dtick_y = max(1, round(y_max / 8))

        fig = px.area(
            df,
            x=x_col,
            y=y_col,
            title=chart_title,
            markers=True,
            labels={x_col: x_label}
        )

        #Eje X — enteros si son años
        if pd.api.types.is_numeric_dtype(df[x_col]):
            fig.update_xaxes(tickmode='linear', dtick=1)

        #Eje Y — dtick automático - calculado con la función dtick_y
        fig.update_yaxes(tickmode='linear', dtick=dtick_y)

    elif chart_type == "histogram" and num_cols:
        fig = px.histogram(df,x=num_cols[0],title=chart_title,color_discrete_sequence=["#636EFA"])
        fig.update_yaxes(tickmode='linear', dtick=1)


    else:
        #Tabla visual
        fig = go.Figure(data=[go.Table(
            header=dict(values=list(df.columns),fill_color="#4A4AE8",font=dict(color="white", size=13),align="left"),
            cells=dict(values=[df[c].tolist() for c in df.columns],fill_color="white", font=dict(color="#1a1a2e", size=13),align="left"))])
        fig.update_layout(title=chart_title)

    #Estilo común para todas las gráficas
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial, sans-serif", size=13),
        margin=dict(t=50, b=40, l=40, r=40)
    )

    return fig