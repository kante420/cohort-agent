from agent.graph import agent
from agent.memory import ConversationMemory

memory = ConversationMemory()

preguntas = [
    "¿Cuántos pacientes hay por provincia?",
    "¿Cuál es la distribución de edades?",
    "¿Cuántos pacientes tiene cada condición crónica?",
]

for pregunta in preguntas:
    print(f"\nUsuario: {pregunta}")

    state = {
        "user_question": pregunta,
        "conversation_history": memory.get_history_as_str()
    }

    result = agent.invoke(state)

    print(f"Intent:   {result.get('intent')}")
    print(f"Gráfica:  {'Sí — ' + str(type(result.get('chart'))) if result.get('chart') else 'No'}")
    print(f"Respuesta: {result.get('answer')}")

    memory.add_turn(pregunta, result.get("answer", ""))