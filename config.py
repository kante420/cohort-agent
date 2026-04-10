from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "./db/cohort.duckdb")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Nombres de tablas tal como quedarán en DuckDB
TABLE_NAMES = {
    "pacientes":      "cohorte_pacientes",
    "condiciones":    "cohorte_condiciones",
    "encuentros":     "cohorte_encuentros",
    "medicaciones":   "cohorte_medicaciones",
    "alergias":       "cohorte_alergias",
    "procedimientos": "cohorte_procedimientos",
}