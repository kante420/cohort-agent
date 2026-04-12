import duckdb
from config import DB_PATH

con = duckdb.connect(DB_PATH, read_only=True)
df = con.execute("SELECT * FROM cohorte_medicaciones LIMIT 1").fetchdf()
print(df.columns.tolist())
con.close()