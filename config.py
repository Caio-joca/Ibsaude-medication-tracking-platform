import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv


PASTA_PROJETO = Path(__file__).resolve().parent
load_dotenv(PASTA_PROJETO / ".env")


def normalizar_url_banco(url):
    if url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url and url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


class ConfiguracaoBase:
    SECRET_KEY = os.getenv("SECRET_KEY", "chave-apenas-para-desenvolvimento")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(PASTA_PROJETO / "uploads"))
    BACKUP_FOLDER = os.getenv("BACKUP_FOLDER", str(PASTA_PROJETO / "backups"))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)


class Desenvolvimento(ConfiguracaoBase):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = normalizar_url_banco(
        os.getenv("DATABASE_URL", f"sqlite:///{PASTA_PROJETO / 'database' / 'ibsaude.db'}")
    )


class Teste(ConfiguracaoBase):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class Producao(ConfiguracaoBase):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = "https"
    SQLALCHEMY_DATABASE_URI = normalizar_url_banco(os.getenv("DATABASE_URL"))

    @classmethod
    def validar(cls):
        if not os.getenv("SECRET_KEY") or len(os.getenv("SECRET_KEY", "")) < 32 or not cls.SQLALCHEMY_DATABASE_URI:
            raise RuntimeError("SECRET_KEY e DATABASE_URL são obrigatórias em produção.")


CONFIGURACOES = {
    "development": Desenvolvimento,
    "testing": Teste,
    "production": Producao,
}
