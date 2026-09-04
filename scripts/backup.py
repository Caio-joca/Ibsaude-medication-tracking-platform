"""Cria uma cópia datada do banco configurado e imprime o caminho final."""

import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

PASTA_PROJETO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PASTA_PROJETO))

from app import criar_app


def criar_backup():
    app = criar_app(os.getenv("FLASK_ENV", "development"))
    pasta = Path(app.config["BACKUP_FOLDER"])
    pasta.mkdir(parents=True, exist_ok=True)
    marca = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    url = app.config["SQLALCHEMY_DATABASE_URI"]

    if url.startswith("sqlite:///"):
        origem = Path(url.removeprefix("sqlite:///"))
        destino = pasta / f"ibsaude-{marca}.sqlite3"
        with sqlite3.connect(origem) as banco_origem, sqlite3.connect(destino) as banco_destino:
            banco_origem.backup(banco_destino)
        print(destino.resolve())
        return destino

    if url.startswith("postgresql"):
        destino = pasta / f"ibsaude-{marca}.dump"
        url_pg = url.replace("postgresql+psycopg://", "postgresql://", 1)
        subprocess.run(["pg_dump", "--format=custom", f"--file={destino}", url_pg], check=True)
        print(destino.resolve())
        return destino

    raise RuntimeError(f"Banco não suportado para backup: {urlparse(url).scheme}")


if __name__ == "__main__":
    criar_backup()
