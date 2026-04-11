#EL ESQUEMA DE NUESTRA DB PARA EVEITAR ALUCINACIONES
SCHEMA_DESCRIPTION = """"
Tienes acceso a una base de datos en DuckDB con 6 tablas de pacientes crónicos.
A continuación se describe el esquema EXACTO. Usa ÚNICAMENTE los nombres de tabla
y columna que aparecen aquí. No inventes columnas ni tablas.

TABLA: cohorte_pacientes
  - PacienteID     (BIGINT)   Identificador único del paciente
  - Genero         (VARCHAR)  Género del paciente. Valores posibles: 'Masculino', 'Femenino'
                              Si el usuario dice 'hombre' o 'varón' usa 'Masculino'.
                              Si el usuario dice 'mujer' o 'femenina' usa 'Femenino'.
  - Edad           (BIGINT)   Edad en años
  - Provincia      (VARCHAR)  Provincia de residencia
  - Latitud        (DOUBLE)   Coordenada geográfica
  - Longitud       (DOUBLE)   Coordenada geográfica

TABLA: cohorte_condiciones
  - PacienteID     (BIGINT)    Identificador del paciente
  - Fecha_inicio   (TIMESTAMP) Fecha de inicio de la condición
  - Fecha_fin      (TIMESTAMP) Fecha de fin (NULL si activa)
  - Codigo_SNOMED  (VARCHAR)   Código SNOMED de la condición
  - Descripcion    (VARCHAR)   Nombre legible de la condición

TABLA: cohorte_encuentros
  - PacienteID      (BIGINT)  Identificador del paciente
  - Tipo_encuentro  (VARCHAR) Tipo de visita médica
  - Fecha_inicio    (DATE)    Fecha de inicio del encuentro
  - Fecha_fin       (DATE)    Fecha de fin del encuentro

TABLA: cohorte_medicaciones
  - PacienteID          (BIGINT)  Identificador del paciente
  - Fecha_inicio        (DATE)    Fecha de prescripción
  - Fecha_fin           (DATE)    Fecha de fin (NULL si activa)
  - Codigo              (VARCHAR) Código del medicamento
  - Nombre              (VARCHAR) Nombre del medicamento
  - Dosis               (VARCHAR) Dosis prescrita
  - Frecuencia          (VARCHAR) Frecuencia de administración
  - Via_administracion  (VARCHAR) Vía (oral, intravenosa, etc.)

TABLA: cohorte_alergias
  - PacienteID          (BIGINT)  Identificador del paciente
  - Fecha_diagnostico   (DATE)    Fecha de diagnóstico de la alergia
  - Codigo_SNOMED       (BIGINT)  Código SNOMED CT
  - Descripcion         (VARCHAR) Descripción de la alergia

TABLA: cohorte_procedimientos
  - PacienteID     (BIGINT)  Identificador del paciente
  - Fecha_inicio   (DATE)    Fecha de inicio del procedimiento
  - Fecha_fin      (DATE)    Fecha de fin
  - Codigo_SNOMED  (BIGINT)  Código SNOMED CT
  - Descripcion    (VARCHAR) Descripción del procedimiento

RELACIONES:
  Todas las tablas se unen con cohorte_pacientes mediante PacienteID.
"""
#ESTAS SON LAS CONDICIONES QUE IMPONEMOS A LA HORA DE GENERAR SQL
RULES = """
REGLAS ESTRICTAS para generar SQL:
1. Devuelve ÚNICAMENTE la query SQL, sin explicaciones, sin markdown, sin ```sql.
2. Usa solo las tablas y columnas del esquema anterior.
3. Las columnas con espacios en cohorte_medicaciones van siempre entre comillas dobles.
4. Para búsquedas de texto usa ILIKE con % para ser flexible (ej: ILIKE '%diabetes%').
5. Limita siempre los resultados con LIMIT 100 salvo que se pida explícitamente otro límite.
6. Si la pregunta es ambigua, genera la query más conservadora posible.
7. Fecha_fin IS NULL SOLO en cohorte_condiciones y cohorte_medicaciones para indicar
   registros activos. NUNCA uses Fecha_fin IS NULL en cohorte_procedimientos ni encuentros.
8. Nunca uses DROP, DELETE, UPDATE, INSERT ni ninguna operación de escritura.
9. CANNOT_ANSWER solo si la pregunta pide información que NO existe en ninguna de
   las 6 tablas. Preguntas sobre fechas, procedimientos, condiciones, medicaciones,
   encuentros o pacientes SIEMPRE tienen respuesta.
10. ILIKE y LIKE solo funcionan sobre columnas VARCHAR. Las columnas Codigo_SNOMED de
    cohorte_alergias y cohorte_procedimientos son BIGINT — NUNCA uses ILIKE sobre ellas.
    Para buscar por nombre usa SIEMPRE la columna Descripcion.
11. NUNCA uses Codigo_SNOMED para buscar por nombre. Usa siempre Descripcion con ILIKE.
12. Cuando uses alias en JOINs sé consistente. Si defines cohorte_condiciones AS cc,
    usa cc.columna en todo el resto de la query.
13. En los SELECT nunca incluyas Codigo_SNOMED salvo que el usuario lo pida explícitamente.
14. Las columnas de cohorte_medicaciones se llaman: Fecha_inicio, Fecha_fin, Codigo,
    Nombre, Dosis, Frecuencia, Via_administracion. Sin espacios ni caracteres especiales.
15. Si el historial contiene un [SQL ejecutado en la consulta anterior], úsalo como
    contexto para entender a qué datos se refiere la pregunta actual. Si la pregunta
    es una continuación (ej: "dame la media", "¿y los de Granada?"), reutiliza los
    mismos filtros WHERE del SQL anterior.
"""

#ESTO ES LO QUE LE VAMOS A PASAR AL LLM CUANDO NECESITEMOS ALGO
SQL_GENERATION_PROMPT = f"""{SCHEMA_DESCRIPTION}

{RULES}

EJEMPLOS DE CONSULTAS CORRECTAS:
Pregunta: ¿Cuál es la edad media de los pacientes con diabetes?
SQL: SELECT AVG(cp.Edad) AS Edad_Media FROM cohorte_pacientes cp JOIN cohorte_condiciones cc ON cp.PacienteID = cc.PacienteID WHERE cc.Descripcion ILIKE '%diabetes%'

Pregunta: ¿Cuántos pacientes tienen hipertensión?
SQL: SELECT COUNT(DISTINCT cp.PacienteID) FROM cohorte_pacientes cp JOIN cohorte_condiciones cc ON cp.PacienteID = cc.PacienteID WHERE cc.Descripcion ILIKE '%hipertensión%'

Pregunta: ¿Qué medicamentos toman los pacientes con asma?
SQL: SELECT DISTINCT m.Nombre FROM cohorte_medicaciones m JOIN cohorte_condiciones cc ON m.PacienteID = cc.PacienteID WHERE cc.Descripcion ILIKE '%asma%'

Pregunta: ¿Cuántos pacientes hay por provincia?
SQL: SELECT Provincia, COUNT(PacienteID) AS Total FROM cohorte_pacientes GROUP BY Provincia ORDER BY Total DESC

Pregunta: ¿Cuántos pacientes tienen diabetes y además hipertensión?
SQL: SELECT COUNT(DISTINCT cp.PacienteID) AS Total FROM cohorte_pacientes cp
     JOIN cohorte_condiciones cc1 ON cp.PacienteID = cc1.PacienteID
     JOIN cohorte_condiciones cc2 ON cp.PacienteID = cc2.PacienteID
     WHERE cc1.Descripcion ILIKE '%diabetes%'
     AND cc2.Descripcion ILIKE '%hipertensión%'

Pregunta: ¿Cuántos procedimientos ha tenido cada paciente?
SQL: SELECT cp.PacienteID, COUNT(pp.Descripcion) AS Total_Procedimientos FROM cohorte_pacientes cp LEFT JOIN cohorte_procedimientos pp ON cp.PacienteID = pp.PacienteID GROUP BY cp.PacienteID ORDER BY Total_Procedimientos DESC

Pregunta: ¿Qué porcentaje de pacientes masculinos tienen cáncer comparado con femeninos?
SQL: SELECT cp.Genero,
     ROUND(COUNT(DISTINCT cp.PacienteID) * 100.0 / 
     (SELECT COUNT(DISTINCT PacienteID) FROM cohorte_pacientes), 2) AS Porcentaje
     FROM cohorte_pacientes cp
     JOIN cohorte_condiciones cc ON cp.PacienteID = cc.PacienteID
     WHERE cc.Descripcion ILIKE '%cancer%'
     GROUP BY cp.Genero

Historial de la conversación (para contexto):
{{conversation_history}}

Pregunta del usuario: {{user_question}}

SQL:"""

ANSWER_GENERATION_PROMPT = """Eres un asistente médico especializado en análisis de cohortes de pacientes crónicos.

Se ha ejecutado la siguiente consulta SQL sobre los datos:
  Pregunta: {user_question}
  SQL ejecutado: {sql_query}
  Resultado ({row_count} filas): 
{query_result}

Responde en español de forma clara y concisa. Si el resultado está vacío, indícalo.
No menciones tecnicismos de SQL. Habla directamente de pacientes, condiciones y estadísticas.
Si hay datos numéricos relevantes, resáltalos. Máximo 4 oraciones.
IMPORTANTE: Lista TODOS los valores que aparecen en el resultado, no omitas ninguno."""