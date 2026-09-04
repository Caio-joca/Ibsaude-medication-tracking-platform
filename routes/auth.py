from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from models import Usuario


auth_bp = Blueprint("auth", __name__)


@auth_bp.before_app_request
def carregar_usuario():
    usuario_id = session.get("usuario_id")
    from extensions import db

    g.usuario = db_usuario = db.session.get(Usuario, usuario_id) if usuario_id else None
    if db_usuario and not db_usuario.ativo:
        session.clear()
        g.usuario = None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if g.get("usuario"):
        return redirect(url_for("principal.painel"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        usuario = Usuario.query.filter_by(email=email, ativo=True).first()

        if usuario and check_password_hash(usuario.senha, senha):
            session.clear()
            session.permanent = True
            session["usuario_id"] = usuario.id_usuario
            proximo = request.args.get("proximo", "")
            if proximo.startswith("/") and not proximo.startswith("//"):
                return redirect(proximo)
            return redirect(url_for("principal.painel"))

        flash("E-mail ou senha inválidos.", "danger")

    return render_template("login.html")


@auth_bp.post("/logout")
def logout():
    session.clear()
    flash("Sessão encerrada.", "success")
    return redirect(url_for("auth.login"))
