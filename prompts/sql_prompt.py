#EL ESQUEMA DE NUESTRA DB PARA EVEITAR ALUCINACIONES
SCHEMA_DESCRIPTION = """"
Tienes acceso a una base de datos en DuckDB con 6 tablas de pacientes crónicos.
A continuación se describe el esquema EXACTO. Usa ÚNICAMENTE los nombres de tabla
y columna que aparecen aquí. No inventes columnas ni tablas.

TABLA: cohorte_pacientes
  - PacienteID     (BIGINT)   Identificador único del paciente
  - Genero         (VARCHAR)  Género del paciente
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
  - PacienteID               (BIGINT)  Identificador del paciente
  - "Fecha de inicio"        (DATE)    Fecha de prescripción
  - "Fecha de fin"           (DATE)    Fecha de fin (NULL si activa)
  - "Código"                 (VARCHAR) Código del medicamento
  - "Nombre"                 (VARCHAR) Nombre del medicamento
  - "Dosis"                  (VARCHAR) Dosis prescrita
  - "Frecuencia"             (VARCHAR) Frecuencia de administración
  - "Vía de administración"  (VARCHAR) Vía (oral, intravenosa, etc.)

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
2. Usa solo las tablas y columnas del esquema que te damos.
3. Las columnas con espacios en cohorte_medicaciones van siempre entre comillas dobles.
4. Para búsquedas de texto usa ILIKE con % para ser flexible (ej: ILIKE '%diabetes%').
5. Limita siempre los resultados con LIMIT 100 salvo que se pida explícitamente otro límite.
6. Si la pregunta es ambigua, genera la query más conservadora posible.
7. Para condiciones activas: Fecha_fin IS NULL indica que sigue activa.
8. Nunca uses DROP, DELETE, UPDATE, INSERT ni ninguna operación de escritura.
9. Si la pregunta NO puede responderse con estas tablas, devuelve exactamente: CANNOT_ANSWER
"""

#ESTO ES LO QUE LE VAMOS A PASAR AL LLM CUANDO NECESITEMOS ALGO
SQL_GENERATION_PROMPT = f"""{SCHEMA_DESCRIPTION}

{RULES}

Historial de la conversación (para contexto):
{{conversation_history}}

Pregunta del usuario: {{user_question}}

SQL:"""

#ESTA ES LA FORMA EN LA QUE NOS VA A CONTESTAR
ANSWER_GENERATION_PROMPT = """Eres un asistente médico especializado en análisis de cohortes de pacientes crónicos.

Se ha ejecutado la siguiente consulta SQL sobre los datos:
  Pregunta: {user_question}
  SQL ejecutado: {sql_query}
  Resultado ({row_count} filas): 
{query_result}

Responde en español de forma clara y concisa. Si el resultado está vacío, indícalo.
No menciones tecnicismos de SQL. Habla directamente de pacientes, condiciones y estadísticas.
Si hay datos numéricos relevantes, resáltalos. Máximo 4 oraciones."""