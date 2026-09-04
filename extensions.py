from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import event
from sqlalchemy.engine import Engine


db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()


@event.listens_for(Engine, "connect")
def habilitar_chaves_estrangeiras_sqlite(conexao, _):
    if conexao.__class__.__module__ == "sqlite3":
        cursor = conexao.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
