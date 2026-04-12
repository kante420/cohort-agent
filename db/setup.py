import duckdb
import os
from config import DB_PATH, TABLE_NAMES

CSV_DIR = "./data/raw" #Directorio donde se almacenan los .csv originales

#FUNCIÓN PARA CARGAR LOS .csv A LA DB
def load_csvs_to_duckdb():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True) #Crea el directorio donde estará la DB si no existe
    con = duckdb.connect(DB_PATH) #Abre una conexión a la DuckDB

    for key, table_name in TABLE_NAMES.items(): #Recorre el diccionario TABLE_NAMES
        csv_path = os.path.join(CSV_DIR, f"{table_name}.csv") #Construye una ruta al .csv correspondiente a cada tabla

        if not os.path.exists(csv_path): #En caso de que no exista el .csv
            print(f"  [!] No encontrado: {csv_path}")
            continue

        #Creamos/reemplazamos una tabla de DuckDB con el contendio del .csv
        #read_csv_auto -> Detecta automaticamente los tipos de datos
        #header=True -> Indicamos que la primera fila contiene los nombres de las columnas
        con.execute(f"""
            CREATE OR REPLACE TABLE {table_name} AS
            SELECT * FROM read_csv_auto('{csv_path}', header=True)
        """)

        #Cuenta cuantas filas se han cargado en la table
        count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]

        #Devuelve que la carga de datos fue exitosa
        print(f"  [ok] {table_name}: {count} filas cargadas")

    con.close() #Cierra la conexión con DuckDB

#FUNCIÓN PARA DEVOLVER ESQUEMA DE LAS TABLAS
def print_schema():
    con = duckdb.connect(DB_PATH) #Abrimos conexión con DuckDB
    print("\n--- Esquema de tablas ---")
    for table_name in TABLE_NAMES.values(): #Para cada tabla
        try:
            #Obtenemos información sobre las columnas de la table -> PRAGMA table_info devuelve nombre, tipo, ...
            cols = con.execute(f"PRAGMA table_info('{table_name}')").fetchdf()
            print(f"\n{table_name}:")
            #Recorremos cada columna, devolviendo nombre y tipo
            for _, row in cols.iterrows():
                print(f"  {row['name']:30s} {row['type']}")
        #En caso de que haya un error (ej. la tabla no existe)
        except Exception as e:
            print(f"  Error en {table_name}: {e}")
    con.close() #Cerramos la conexión con DuckDB

if __name__ == "__main__":
    print("Cargando CSVs en DuckDB...")
    load_csvs_to_duckdb()
    print_schema()