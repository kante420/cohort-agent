import duckdb
import pandas as pd
from config import DB_PATH

class DuckDBTool:
    def __init__(self):
        self.db_path = DB_PATH #Guardamos la DB_PATH dentro del objeto

    #Abrimos conexión con DuckDB evitando que, en el caso de que se nos cuele una query de escritura, la omita
    def _get_connection(self): 
        return duckdb.connect(self.db_path, read_only=True)

    """
        Ejecuta la query y devuelve un diccionario con:
          - success: bool
          - data: DataFrame (si éxito)
          - error: str (si fallo)
          - row_count: int
    """
    def execute_query(self, sql: str) -> dict:
        try:
            con = self._get_connection()
            df = con.execute(sql).fetchdf()
            con.close()
            return {
                "success": True,
                "data": df,
                "row_count": len(df),
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "data": pd.DataFrame(),
                "row_count": 0,
                "error": str(e)
            }

    """
        Valida que la query no contenga operaciones de escritura y que sea sintácticamente válida (EXPLAIN).
        Devuelve (es_valida, mensaje_error).
    """
    def validate_sql(self, sql: str) -> tuple[bool, str]:
        forbidden = ["drop", "delete", "update", "insert", "alter", "create", "truncate"]
        sql_lower = sql.lower()

        for keyword in forbidden:
            if keyword in sql_lower:
                return False, f"Operación no permitida detectada: {keyword.upper()}"

        try:
            con = self._get_connection()
            con.execute(f"EXPLAIN {sql}") #EXPLAIN -> Comando de DuckDB para analizar query sin ejecutarla (detectando errores de sintaxis)
            con.close()
            return True, ""
        except Exception as e:
            return False, str(e)
        
    #Convierte un DataFrame (de Pandas, que devuelve DuckDB) a string legible para el prompt
    def dataframe_to_str(self, df: pd.DataFrame, max_rows: int = 20) -> str:
        if df.empty:
            return "(sin resultados)"
        return df.head(max_rows).to_string(index=False)