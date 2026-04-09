import pandas as pd
import os

def action_node(state: dict) -> dict:
    question = state.get("user_question", "").lower()
    df = state.get("query_result", None)

    #Comprobamos si existe el DataFrame de Pandas
    if df is None or df.empty: 
        return {**state, "answer": "No hay datos cargados para ejecutar esa acción. Primero realiza una consulta."}

    #Si la pregunta contiene {"exportar", "guardar" o "csv"} 
    if "exportar" in question or "guardar" in question or "csv" in question:
        os.makedirs("./exports", exist_ok=True) #Creamos el directorio
        path = "./exports/cohorte_exportada.csv" #Creamos el archivo
        df.to_csv(path, index=False) #Escribimos el archivo
        return {**state, "answer": f"Cohorte exportada correctamente a `{path}` con {len(df)} pacientes."}

    return {**state, "answer": "Acción no reconocida. Por ahora puedes pedirme exportar los datos a CSV."}