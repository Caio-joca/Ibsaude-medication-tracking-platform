import os

import click
from flask import Flask, g
from werkzeug.security import generate_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

from config import CONFIGURACOES
from extensions import csrf, db, migrate


def criar_app(configuracao=None):
    import services.auditoria  # registra os eventos imutáveis do ORM

    app = Flask(__name__)
    nome_configuracao = configuracao or os.getenv("FLASK_ENV", "development")
    classe_configuracao = CONFIGURACOES.get(nome_configuracao, CONFIGURACOES["development"])
    if hasattr(classe_configuracao, "validar"):
        classe_configuracao.validar()
    app.config.from_object(classe_configuracao)
    if nome_configuracao == "production":
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["BACKUP_FOLDER"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from models import Usuario
    from routes.aquisicoes import aquisicoes_bp
    from routes.auth import auth_bp
    from routes.cadastros import cadastros_bp
    from routes.medicamentos import medicamentos_bp
    from routes.principal import principal_bp
    from routes.estoque import estoque_bp
    from routes.distribuicoes import distribuicoes_bp
    from routes.auditoria import auditoria_bp
    from routes.relatorios import relatorios_bp
    from routes.usuarios import usuarios_bp

    app.register_blueprint(principal_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(cadastros_bp)
    app.register_blueprint(medicamentos_bp)
    app.register_blueprint(aquisicoes_bp)
    app.register_blueprint(estoque_bp)
    app.register_blueprint(distribuicoes_bp)
    app.register_blueprint(auditoria_bp)
    app.register_blueprint(relatorios_bp)

    @app.after_request
    def cabecalhos_seguranca(resposta):
        resposta.headers["X-Content-Type-Options"] = "nosniff"
        resposta.headers["X-Frame-Options"] = "DENY"
        resposta.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        resposta.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self' https://cdn.jsdelivr.net; "
            "script-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
        )
        if app.config.get("SESSION_COOKIE_SECURE"):
            resposta.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        if getattr(g, "usuario", None):
            resposta.headers["Cache-Control"] = "no-store, private"
        return resposta

    @app.cli.command("criar-admin")
    @click.option("--nome", prompt=True)
    @click.option("--cpf", prompt=True)
    @click.option("--email", prompt=True)
    @click.password_option("--senha", confirmation_prompt=True)
    def criar_admin(nome, cpf, email, senha):
        """Cria o primeiro administrador sem armazenar senha em texto aberto."""
        from utils.validacao import cpf_valido, email_valido, somente_digitos

        email = email.strip().lower()
        cpf = somente_digitos(cpf)
        if not cpf_valido(cpf):
            raise click.ClickException("Informe um CPF válido.")
        email = email_valido(email)
        if not email:
            raise click.ClickException("Informe um e-mail válido.")
        if len(senha) < 8:
            raise click.ClickException("A senha deve ter pelo menos 8 caracteres.")
        if Usuario.query.filter((Usuario.email == email) | (Usuario.cpf == cpf)).first():
            raise click.ClickException("Já existe um usuário com esse CPF ou e-mail.")

        administrador = Usuario(
            nome=nome.strip(),
            cpf=cpf,
            email=email,
            senha=generate_password_hash(senha),
            perfil="A",
        )
        db.session.add(administrador)
        db.session.commit()
        click.echo("Administrador criado com sucesso.")

    @app.cli.command("carregar-demo")
    @click.option(
        "--senha-demo",
        help="Senha comum para os usuários fictícios. Se omitida, uma senha segura será gerada.",
    )
    def carregar_demo(senha_demo):
        """Carrega dados fictícios e idempotentes para demonstração local."""
        import secrets

        from flask import g

        from scripts.dados_demo import carregar_dados_demo

        if nome_configuracao == "production":
            raise click.ClickException("A carga de demonstração é bloqueada em produção.")
        if senha_demo and len(senha_demo) < 8:
            raise click.ClickException("A senha de demonstração deve ter pelo menos 8 caracteres.")

        administrador = Usuario.query.filter_by(perfil="A", ativo=True).order_by(Usuario.id_usuario).first()
        if not administrador:
            raise click.ClickException("Crie primeiro um administrador com o comando criar-admin.")

        senha_gerada = not senha_demo
        senha_demo = senha_demo or secrets.token_urlsafe(12)
        with app.test_request_context("/cli/carregar-demo"):
            g.usuario = administrador
            resultado = carregar_dados_demo(administrador, senha_demo)

        click.echo("Carga de demonstração concluída.")
        for item, quantidade in resultado["criados"].items():
            click.echo(f"- {item}: {quantidade} novo(s)")
        if resultado["usuarios_criados"]:
            click.echo("Contas fictícias:")
            for email in resultado["emails_criados"]:
                click.echo(f"- {email}")
            click.echo(f"Senha comum: {senha_demo}")
            if senha_gerada:
                click.echo("Guarde a senha agora: ela não poderá ser recuperada do banco.")
        else:
            click.echo("Os usuários fictícios já existiam; suas senhas não foram alteradas.")

    return app


app = criar_app()


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
