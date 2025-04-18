import sqlite3

# Conectar a la base de datos (se creará automáticamente si no existe)
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Crear una tabla de ejemplo
cursor.execute("""
    CREATE TABLE IF NOT EXISTS test (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT
    )
""")

conn.commit()
conn.close()

print("✅ SQLite está funcionando correctamente.")