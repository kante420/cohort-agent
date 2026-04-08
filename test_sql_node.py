from agent.nodes.sql_node import sql_node

state = {
    "user_question": "¿Cuántos pacientes hay por provincia?",
    "conversation_history": ""
}

result = sql_node(state)
print("SQL generado:", result.get("sql"))
print("Respuesta:", result.get("answer"))
print("Filas:", len(result["query_result"]) if result.get("query_result") is not None else 0)