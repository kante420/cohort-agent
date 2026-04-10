import ollama
from config import OLLAMA_HOST

MODEL = "qwen2.5-coder:14b-instruct-q8_0"
client = ollama.Client(host=OLLAMA_HOST)

INTENT_PROMPT = """Clasifica la intención del mensaje del usuario en UNA de estas categorías:

- sql        → pregunta sobre datos concretos de pacientes (quién, cuántos, cuáles, listar)
- estadistica → pide resúmenes, medias, distribuciones, comparativas, gráficas
- accion     → quiere exportar datos, filtrar la cohorte, guardar resultados en un archivo
- fuera_scope → saludo, pregunta general, algo no relacionado con los datos

EJEMPLOS:
"¿Cuántos pacientes hay?" → sql
"¿Cuántos pacientes tienen diabetes?" → sql
"¿Cuántos pacientes han sido operados de apendicitis?" → sql
"¿Qué medicamentos toman los pacientes de Málaga?" → sql
"¿Cuál es la edad media?" → estadistica
"Muéstrame la distribución por provincia" → estadistica
"Exportar a CSV" → accion
"Guardar los resultados" → accion
"Descargar los datos" → accion
"Hola" → fuera_scope
"¿Qué puedes hacer?" → fuera_scope

Historial reciente:
{historial}

Mensaje del usuario: {mensaje}

Responde ÚNICAMENTE con una de estas palabras: sql, estadistica, accion, fuera_scope"""

def intent_node(state: dict) -> dict:
    mensaje   = state.get("user_question", "")
    historial = state.get("conversation_history", "Sin historial previo.")

    prompt = INTENT_PROMPT.format(historial=historial, mensaje=mensaje)

    response = client.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    intent = response["message"]["content"].strip().lower()
    intent = intent.split()[0] if intent.split() else "sql"
    intent = intent.strip(".,;:")

    valid_intents = {"sql", "estadistica", "accion", "fuera_scope"}
    if intent not in valid_intents:
        intent = "sql"

    return {**state, "intent": intent}