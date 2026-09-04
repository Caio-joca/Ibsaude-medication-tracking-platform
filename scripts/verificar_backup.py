"""Valida a integridade de um backup SQLite ou a estrutura de um dump PostgreSQL."""

import sqlite3
import subprocess
import sys
from pathlib import Path


def verificar(caminho):
    arquivo = Path(caminho).resolve()
    if not arquivo.is_file():
        raise FileNotFoundError(arquivo)
    if arquivo.suffix == ".sqlite3":
        with sqlite3.connect(f"file:{arquivo}?mode=ro", uri=True) as conexao:
            resultado = conexao.execute("PRAGMA integrity_check").fetchone()[0]
            if resultado != "ok":
                raise RuntimeError(resultado)
            tabelas = conexao.execute("SELECT count(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
        print(f"Backup SQLite íntegro: {arquivo} ({tabelas} tabelas)")
        return
    if arquivo.suffix == ".dump":
        subprocess.run(["pg_restore", "--list", str(arquivo)], check=True, stdout=subprocess.DEVNULL)
        print(f"Dump PostgreSQL íntegro: {arquivo}")
        return
    raise ValueError("Extensão esperada: .sqlite3 ou .dump")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python scripts/verificar_backup.py CAMINHO")
    verificar(sys.argv[1])
