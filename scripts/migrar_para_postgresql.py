"""Copia os dados do SQLite do MVP para um PostgreSQL já migrado.

Antes de executar:
1. Configure POSTGRES_DATABASE_URL.
2. Aplique `flask db upgrade` nesse banco.
3. Faça backup dos dois bancos.
"""

import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, insert, select, text

PASTA_PROJETO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PASTA_PROJETO))

from models import db


SQLITE_URL = f"sqlite:///{PASTA_PROJETO / 'database' / 'ibsaude.db'}"
POSTGRES_URL = os.getenv("POSTGRES_DATABASE_URL", "").replace("postgresql://", "postgresql+psycopg://", 1)


def migrar():
    if not POSTGRES_URL:
        raise RuntimeError("Defina POSTGRES_DATABASE_URL antes de executar a migração.")

    origem = create_engine(SQLITE_URL)
    destino = create_engine(POSTGRES_URL)

    with origem.connect() as conexao_origem, destino.begin() as conexao_destino:
        for tabela in db.metadata.sorted_tables:
            registros = [dict(linha._mapping) for linha in conexao_origem.execute(select(tabela))]
            if registros:
                conexao_destino.execute(insert(tabela), registros)
                print(f"{tabela.name}: {len(registros)} registro(s) copiado(s)")

        for tabela in db.metadata.sorted_tables:
            colunas_pk = list(tabela.primary_key.columns)
            if len(colunas_pk) == 1 and str(colunas_pk[0].type).startswith("INTEGER"):
                nome_coluna = colunas_pk[0].name
                conexao_destino.execute(
                    text(
                        "SELECT setval(pg_get_serial_sequence(:tabela, :coluna), "
                        "COALESCE((SELECT MAX(" + nome_coluna + ") FROM " + tabela.name + "), 1), true)"
                    ),
                    {"tabela": tabela.name, "coluna": nome_coluna},
                )

    print("Migração concluída. Valide as contagens antes de trocar o DATABASE_URL.")


if __name__ == "__main__":
    migrar()
