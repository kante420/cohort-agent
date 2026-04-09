import ollama
from agent.tools.duckdb_tool import DuckDBTool
from prompts.sql_prompt import SQL_GENERATION_PROMPT, ANSWER_GENERATION_PROMPT

MODEL = "qwen2.5-coder:7b"
db_tool = DuckDBTool()

def _call_llm(prompt: str) -> str:
    response = ollama.chat(
        model=MODEL,
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

"""
    Correcciones automáticas para errores frecuentes del modelo:
    1. ILIKE/LIKE sobre Codigo_SNOMED (BIGINT) → reemplaza por Descripcion
    2. Fecha_fin IS NULL en procedimientos y encuentros → lo elimina
    """
def fix_sql(sql: str) -> str:
    import re

    # Fix 1: ILIKE o LIKE sobre Codigo_SNOMED → usar Descripcion
    sql = re.sub(
        r'Codigo_SNOMED\s+(I?LIKE)\s+',
        r'Descripcion \1 ',
        sql,
        flags=re.IGNORECASE
    )

    # Fix 2: Codigo_SNOMED = número → alucinación de código SNOMED
    if re.search(r'Codigo_SNOMED\s*=\s*[\'"]?\d+[\'"]?', sql, flags=re.IGNORECASE):
        return "SNOMED_HALLUCINATION"

    # Fix 3: elimina Fecha_fin IS NULL en procedimientos y encuentros
    tablas_sin_activo = ["cohorte_procedimientos", "cohorte_encuentros"]
    for tabla in tablas_sin_activo:
        if tabla.lower() in sql.lower():
            sql = re.sub(r'AND\s+Fecha_fin\s+IS\s+NULL', '', sql, flags=re.IGNORECASE)
            sql = re.sub(r'Fecha_fin\s+IS\s+NULL\s+AND', '', sql, flags=re.IGNORECASE)
            sql = re.sub(r'WHERE\s+Fecha_fin\s+IS\s+NULL', 'WHERE 1=1', sql, flags=re.IGNORECASE)

    # Fix 4: aliases inconsistentes
    alias_map = {}
    for match in re.finditer(r'\b\w+\s+AS\s+(\w+)\b', sql, flags=re.IGNORECASE):
        alias_map[match.group(1).upper()] = match.group(1)
    for match in re.finditer(
        r'\b(cohorte_\w+)\s+(\w+)\b(?!\s*=)(?!\s*ON)(?!\s*JOIN)',
        sql, flags=re.IGNORECASE
    ):
        alias = match.group(2)
        if alias.upper() not in ('WHERE', 'ON', 'JOIN', 'LEFT', 'RIGHT', 'INNER',
                                  'GROUP', 'ORDER', 'LIMIT'):
            alias_map[alias.upper()] = alias

    used_prefixes = re.findall(r'\b([A-Za-z_]\w*)\.', sql)
    for prefix in set(used_prefixes):
        if prefix.upper() not in [k.upper() for k in alias_map.keys()]:
            candidates = [a for a in alias_map.keys()
                          if a.upper().startswith(prefix[0].upper())]
            if len(candidates) == 1:
                correct = alias_map[candidates[0]]
                sql = re.sub(rf'\b{re.escape(prefix)}\.', f'{correct}.', sql)

    # Fix 5: SELECT sin DISTINCT en JOINs → añade DISTINCT automáticamente
    if re.search(r'JOIN', sql, flags=re.IGNORECASE):
        sql = re.sub(r'\bSELECT\b(?!\s+DISTINCT)', 'SELECT DISTINCT', sql, flags=re.IGNORECASE)

    # Fix 6: LIKE → ILIKE
    sql = re.sub(
        r'\bLIKE\b(?!\s+ALL)(?!\s+ANY)',
        'ILIKE',
        sql,
        flags=re.IGNORECASE
    )

    # Fix 7: YEAR() → EXTRACT(YEAR FROM ...)
    sql = re.sub(
        r'\bYEAR\s*\(\s*(\w+\.\w+|\w+)\s*\)',
        r'EXTRACT(YEAR FROM \1)',
        sql,
        flags=re.IGNORECASE
    )

    # Fix 8: MONTH() → EXTRACT(MONTH FROM ...)
    sql = re.sub(
        r'\bMONTH\s*\(\s*(\w+\.\w+|\w+)\s*\)',
        r'EXTRACT(MONTH FROM \1)',
        sql,
        flags=re.IGNORECASE
    )

    # Fix 9: EncuentroID no existe → contar filas con COUNT(*)
    sql = re.sub(
        r'COUNT\s*\(\s*DISTINCT\s+\w+\.EncuentroID\s*\)',
        'COUNT(*)',
        sql,
        flags=re.IGNORECASE
    )
    sql = re.sub(
        r'COUNT\s*\(\s*\w+\.EncuentroID\s*\)',
        'COUNT(*)',
        sql,
        flags=re.IGNORECASE
    )

    # Fix 10: cp.Descripcion no existe en cohorte_pacientes → viene de cohorte_condiciones
    sql = re.sub(
        r'\bcp\.Descripcion\b',
        'cc.Descripcion',
        sql,
        flags=re.IGNORECASE
    )

    sql = re.sub(r'\s+', ' ', sql).strip()
    return sql


def sql_node(state: dict) -> dict:
    question = state.get("user_question", "")
    history  = state.get("conversation_history", "")

    sql = generate_sql(question, history)

    if sql.strip() == "CANNOT_ANSWER":
        return {**state, "answer": "No puedo responder esa pregunta con los datos disponibles.", "sql": sql, "query_result": None}

    sql = sql.replace("```sql", "").replace("```", "").strip() #Limpiamos markdown

    sql=fix_sql(sql) #Correciones automáticas antes de validar

    #Si el modelo usó un código SNOMED inventado -> lo rechazamos
    if sql == "SNOMED_HALLUCINATION":
        return {
            **state,
            "answer": "No he podido resolver esa consulta de forma segura. Intenta reformularla usando el nombre de la enfermedad o procedimiento en lugar de un código.",
            "sql": None,
            "query_result": None
        }

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