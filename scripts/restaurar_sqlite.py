"""Restaura um backup SQLite após confirmação explícita e guarda uma cópia do banco atual."""

import argparse
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

PASTA_PROJETO = Path(__file__).resolve().parents[1]
BANCO_PADRAO = PASTA_PROJETO / "database" / "ibsaude.db"


def restaurar(backup, destino, confirmar):
    if not confirmar:
        raise RuntimeError("Use --confirmar depois de revisar os caminhos.")
    backup = Path(backup).resolve()
    destino = Path(destino).resolve()
    if not backup.is_file() or backup.suffix != ".sqlite3":
        raise ValueError("Informe um backup .sqlite3 existente.")
    with sqlite3.connect(f"file:{backup}?mode=ro", uri=True) as conexao:
        if conexao.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("O backup não passou na verificação de integridade.")
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists():
        marca = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        seguranca = destino.with_name(f"{destino.stem}-antes-restauracao-{marca}{destino.suffix}")
        shutil.copy2(destino, seguranca)
        print(f"Cópia de segurança do banco anterior: {seguranca}")
    shutil.copy2(backup, destino)
    print(f"Banco restaurado em: {destino}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("backup")
    parser.add_argument("--destino", default=str(BANCO_PADRAO))
    parser.add_argument("--confirmar", action="store_true")
    args = parser.parse_args()
    restaurar(args.backup, args.destino, args.confirmar)
