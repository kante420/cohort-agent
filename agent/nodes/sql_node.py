import ollama
from agent.tools.duckdb_tool import DuckDBTool
from prompts.sql_prompt import SQL_GENERATION_PROMPT, ANSWER_GENERATION_PROMPT

db_tool = DuckDBTool()

def _call_llm(prompt: str) -> str:
    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"].strip()

def generate_sql(user_question: str, conversation_history: str = "") -> str:
    prompt = SQL_GENERATION_PROMPT.format(
        conversation_history=conversation_history or "Sin historial previo.",
        user_question=user_question
    )
    return _call_llm(prompt)

def generate_answer(user_question: str, sql: str, result_str: str, row_count: int) -> str:
    prompt = ANSWER_GENERATION_PROMPT.format(
        user_question=user_question,
        sql_query=sql,
        row_count=row_count,
        query_result=result_str
    )
    return _call_llm(prompt)

def sql_node(state: dict) -> dict:
    question = state.get("user_question", "")
    history  = state.get("conversation_history", "")

    sql = generate_sql(question, history)

    if sql == "CANNOT_ANSWER":
        return {**state, "answer": "No puedo responder esa pregunta con los datos disponibles.", "sql": sql, "query_result": None}

    sql = sql.replace("```sql", "").replace("```", "").strip()

    is_valid, validation_error = db_tool.validate_sql(sql)
    if not is_valid:
        return {**state, "answer": f"La consulta generada no es válida: {validation_error}", "sql": sql, "query_result": None}

    result = db_tool.execute_query(sql)
    if not result["success"]:
        return {**state, "answer": f"Error al ejecutar la consulta: {result['error']}", "sql": sql, "query_result": None}

    result_str = db_tool.dataframe_to_str(result["data"])
    answer = generate_answer(question, sql, result_str, result["row_count"])

    return {
        **state,
        "sql": sql,
        "query_result": result["data"],
        "answer": answer,
        "error": None
    }