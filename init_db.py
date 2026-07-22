import sqlite3
import os

BANCO = "database/usuarios.db"

os.makedirs("database", exist_ok=True)
conn = sqlite3.connect(BANCO)

cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    senha TEXT NOT NULL,
    cpf TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    perfil CHAR(1) NOT NULL)""")
conn.commit()
conn.close()

print("Banco criado com sucesso!")



def conectar():
    conn = sqlite3.connect(BANCO)
    conn.row_factory = sqlite3.Row
    return conn