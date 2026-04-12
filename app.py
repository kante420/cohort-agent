import streamlit as st
from agent.graph import agent
from agent.memory import ConversationMemory
import os
import glob
from datetime import datetime
from agent.tools.duckdb_tool import DuckDBTool
from agent.nodes.sql_node import generate_answer

db_tool = DuckDBTool()

SQLS_RAPIDOS = {
    "Consultar medicación": """
        SELECT Nombre, Dosis, Frecuencia, "Vía_administración", Fecha_inicio, Fecha_fin
        FROM cohorte_medicaciones
        WHERE PacienteID = {id}
        ORDER BY Fecha_inicio DESC
    """,
    "Historial médico": """
        SELECT 'Condición' AS Tipo, Descripcion, Fecha_inicio::VARCHAR AS Fecha
        FROM cohorte_condiciones WHERE PacienteID = {id}
        UNION ALL
        SELECT 'Medicación', Nombre, Fecha_inicio::VARCHAR
        FROM cohorte_medicaciones WHERE PacienteID = {id}
        UNION ALL
        SELECT 'Procedimiento', Descripcion, Fecha_inicio::VARCHAR
        FROM cohorte_procedimientos WHERE PacienteID = {id}
        UNION ALL
        SELECT 'Encuentro', Tipo_encuentro, Fecha_inicio::VARCHAR
        FROM cohorte_encuentros WHERE PacienteID = {id}
        ORDER BY Fecha DESC
    """
}

MENSAJE_BIENVENIDA = """
👋 Bienvenido a **Síntoma SELECT**.

Puedo ayudarte a consultar y analizar la cohorte de pacientes crónicos mediante lenguaje natural. Algunos ejemplos:

- *¿Qué pacientes tienen diabetes e hipertensión?*
- *¿Cuál es la edad media por provincia?*
- *¿Qué medicamentos toma el paciente 5?*
- *¿Cuántos procedimientos se realizaron en 2024?*

También puedes usar las **Acciones Rápidas** del panel lateral para consultas directas por ID de paciente.
"""

# ── Configuración de la página ──────────────────────────────────────────────
st.set_page_config(
    page_title="Agente de Cohortes", #Nombre de la pestaña
    page_icon="logo_icon.png", #Icono de la pstaña
    layout="wide" #Que ocupe todo el ancho de la pantalla
)

#Logo superior
st.markdown("""
    <style>
    [data-testid="stStatusWidget"] {
        visibility: hidden;
        display: none;
    }
    header[data-testid="stHeader"] {
        background: none;
    }
    #MainMenu {
        visibility: hidden;
    }
    </style>
""", unsafe_allow_html=True)

st.image("text_logo.svg", width=400)
st.caption("Identificación y análisis de pacientes crónicos mediante lenguaje natural")

#Analizamos el estado de la sesiónm
if "memory" not in st.session_state: #memory -> Guarda el contexto de la conversación
    st.session_state.memory = ConversationMemory()

if "messages" not in st.session_state: #messages -> Array que guarda el historial de mensajes que vemos
    st.session_state.messages = [{
        "role": "assistant",
        "content": MENSAJE_BIENVENIDA,
        "is_welcome": True,
        "chart": None,
        "sql": None
    }]

if "last_df" not in st.session_state: #last_df -> Guarda el último DataFrame
    st.session_state.last_df = None  # último DataFrame para exportar

#Recorremos todos los mensajes guardados y los ponemos en pantalla
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("chart"):
            st.plotly_chart(msg["chart"], use_container_width=True, key=f"chart_history_{i}")
        if msg.get("sql"):
            with st.expander("SQL ejecutado"):
                st.code(msg["sql"], language="sql")

#Input del usuario
if prompt := st.chat_input("Escribe tu pregunta sobre la cohorte..."):

    #Muestra y guarda el mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    #Llamamos al grafo
    with st.chat_message("assistant"):
        with st.spinner("Analizando..."):
            state = {
                "user_question": prompt,
                "conversation_history": st.session_state.memory.get_history_as_str()
            }
            result = agent.invoke(state)

        answer = result.get("answer", "No se pudo generar una respuesta.")
        chart  = result.get("chart", None)
        sql    = result.get("sql", None)
        df     = result.get("query_result", None)

        #Mostramos la respuesta
        st.markdown(answer)

        #Mostramos la gráfica si existe
        if chart:
            st.plotly_chart(chart, use_container_width=True, key=f"chart_new_{len(st.session_state.messages)}")

        #Mostramos el SQL en un desplegable
        if sql and sql != "CANNOT_ANSWER":
            with st.expander("SQL ejecutado"):
                st.code(sql, language="sql")

        #Guardamos el DataFrame para poder exportarlo
        if df is not None and not df.empty:
            st.session_state.last_df = df

    #Actualizamos el historial
    st.session_state.messages.append({
        "role":    "assistant",
        "content": answer,
        "chart":   chart,
        "sql":     sql
    })
    st.session_state.memory.add_turn(prompt, answer)

#Sidebar
with st.sidebar:
    st.header("Acciones")

    #Acción de exportar último resultado a .csv (si hay datos last_df)
    if st.session_state.last_df is not None:
        csv = st.session_state.last_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Descargar último resultado (CSV)",
            data=csv,
            file_name="cohorte_exportada.csv",
            mime="text/csv"
        )
    else:
        st.caption("Realiza una consulta para habilitar la exportación.")

    st.divider()

    #Exportar conversación PDF
    if st.session_state.messages:
        from viz.export import conversation_to_pdf
        pdf_bytes = conversation_to_pdf(st.session_state.messages)
        st.download_button(
            label="Descargar conversación (PDF)",
            data=pdf_bytes,
            file_name=f"conversacion_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf"
        )
    else:
        st.caption("Inicia una conversación para exportar el informe.")

    st.divider()

    #Acción de limpiar conversación
    if st.button("Limpiar conversación"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": MENSAJE_BIENVENIDA,
            "is_welcome": True,
            "chart": None,
            "sql": None
        }]
        st.session_state.memory.clear()
        st.session_state.last_df = None
        st.rerun()

    st.divider()

    with st.expander("⚡ Acciones Rápidas"):
        accion = st.radio(
            "Selecciona una acción:",
            ["Consultar medicación", "Historial médico"],
            index=None,
            label_visibility="collapsed"
        )

        if accion:
            paciente_id_str = st.text_input(
            "ID del paciente:",
            placeholder="Escribe el ID del paciente"
            )
            paciente_id = int(paciente_id_str) if paciente_id_str.strip().isdigit() else None

            if paciente_id:
                if st.button("Consultar", key="btn_accion_rapida"):
                    sql = SQLS_RAPIDOS[accion].format(id=paciente_id)

                    with st.spinner("Analizando..."):
                        result = db_tool.execute_query(sql)

                    if result["success"] and not result["data"].empty:
                        df = result["data"]

                        if accion == "Consultar medicación":
                            st.markdown(f"**Medicación del paciente {paciente_id}:**")
                            for _, row in df.iterrows():
                                fecha_inicio = str(row['Fecha_inicio'])[:10]
                                fecha_fin = str(row['Fecha_fin'])[:10] if str(row['Fecha_fin']) != 'NaT' else "en curso"
                                st.markdown(f"""
                        - **{row['Nombre']}**  
                            Dosis: {row['Dosis']} | Frecuencia: {row['Frecuencia']}  
                            Vía: {row['Vía_administración']}  
                            Desde {fecha_inicio} hasta {fecha_fin}
                        """)
                        else:
                            st.markdown(f"**Historial del paciente {paciente_id}:**")
                            for _, row in df.iterrows():
                                st.markdown(f"- **{row['Tipo']}** — {row['Descripcion']} ({row['Fecha']})")
                    else:
                        st.warning(f"No se encontraron datos para el paciente {paciente_id}.")


    with st.expander("ℹ️ Sobre el proyecto"):
        st.image("logo_icon.png", width=300)
        st.markdown("""
        **Agente conversacional para cohortes de pacientes crónicos**

        Permite a profesionales de la salud consultar datos clínicos 
        mediante lenguaje natural, sin necesidad de conocer SQL.

        **Tecnologías:**
        - LangGraph — orquestación
        - Ollama + Qwen 2.5 Coder 7B — LLM local
        - DuckDB — motor de datos
        - Plotly — visualización
        - Streamlit — interfaz
                    
        Este proyecto ha sido desarrollado como solución para el reto prpuesto
        por Dedalus para su Dathathon en Castilla-La Mancha.
                    
        Desarrollado por:
        - Hugo Cantero Serrano - Estudiante de 2º de Ingeniería Informática en la ESIIAB
        - Diego Calcerrada Romero - Estudiante de 2º de Ingeniería Informática en la ESIICR
        """)

    with st.expander("📂 Archivos de datos"):
        st.markdown("Las respuestas se generan consultando estos archivos:")
        csv_files = glob.glob("./data/raw/*.csv")
        for f in sorted(csv_files):
            st.markdown(f"- `{os.path.basename(f)}`")

    with st.expander("❓ FAQ"):
        st.markdown("")