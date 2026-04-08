from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_PATH = os.getenv("DB_PATH", "./db/cohort.duckdb")


# Nombres de tablas tal como quedarán en DuckDB
TABLE_NAMES = {
    "pacientes":      "cohorte_pacientes",
    "condiciones":    "cohorte_condiciones",
    "encuentros":     "cohorte_encuentros",
    "medicaciones":   "cohorte_medicaciones",
    "alergias":       "cohorte_alergias",
    "procedimientos": "cohorte_procedimientos",
}