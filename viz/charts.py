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
    wants_line = any(k in question_lower for k in ["evolución", "tendencia", "tiempo", "histórico"])

    # Debug completo
    #print(f"DEBUG text_cols={text_cols}")
    #print(f"DEBUG num_cols={num_cols}")
    #print(f"DEBUG wants_pie={wants_pie}")
    if text_cols:
        print(f"DEBUG n_categorias={df[text_cols[0]].nunique()}")

    if date_cols and num_cols:
        print("DEBUG → line")
        return "line"
    if wants_line and num_cols:
        #print("DEBUG → line")
        return "line"
    if n_cols == 1 and num_cols:
        #print("DEBUG → histogram")
        return "histogram"
    if text_cols and num_cols:
        n_categorias = df[text_cols[0]].nunique()
        if wants_pie or n_categorias <= 2:
            #print("DEBUG → pie")
            return "pie"
        if n_categorias <= 6:
            #print("DEBUG → pie")
            return "pie"
        #print("DEBUG → bar")
        return "bar"
    if n_cols >= 2 and num_cols:
        #print("DEBUG → bar")
        return "bar"

    #print("DEBUG → table")
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

    #Si la única columna es PacienteID, es una lista de IDs — no graficar
    if cols == ["PacienteID"] or cols == ["pacienteid"]:
        return "none"

    chart_type = detect_chart_type(df, question)

    #print(f"DEBUG build_chart chart_type={chart_type}")

    text_cols = [c for c in cols if pd.api.types.is_string_dtype(df[c])
             or pd.api.types.is_object_dtype(df[c])]    
    num_cols   = [c for c in cols if pd.api.types.is_numeric_dtype(df[c])]
    date_cols  = [c for c in cols if any(k in c.lower() for k in ["fecha", "date"])]

    chart_title = title

    #print(f"DEBUG build_chart text_cols={text_cols} num_cols={num_cols}")

    if chart_type == "bar" and text_cols and num_cols:
        fig = px.bar(df,x=text_cols[0],y=num_cols[0],title=chart_title,color=text_cols[0],color_discrete_sequence=px.colors.qualitative.Set2)

    elif chart_type == "pie" and text_cols and num_cols:
        fig = px.pie(df,names=text_cols[0],values=num_cols[0],title=chart_title,color_discrete_sequence=px.colors.qualitative.Set2)

    elif chart_type == "line":
        x_col = date_cols[0] if date_cols else (text_cols[0] if text_cols else cols[0])
        fig = px.line(df,x=x_col,y=num_cols[0] if num_cols else cols[1],title=chart_title,markers=True)

    elif chart_type == "histogram" and num_cols:
        fig = px.histogram(df,x=num_cols[0],title=chart_title,color_discrete_sequence=["#636EFA"])

    else:
        # Fallback: tabla visual
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