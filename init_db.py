from app import criar_app
from extensions import db


def inicializar_banco():
    app = criar_app()
    with app.app_context():
        db.create_all()
    print("Estrutura do banco criada com sucesso.")


if __name__ == "__main__":
    inicializar_banco()