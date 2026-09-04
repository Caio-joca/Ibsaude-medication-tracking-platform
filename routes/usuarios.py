from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from extensions import db
from models import Usuario
from utils.seguranca import perfis_permitidos
from utils.validacao import cpf_valido, email_valido, somente_digitos


usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


def validar_usuario(dados, exige_senha=False):
    erros = []
    nome = dados.get("nome", "").strip()
    cpf = somente_digitos(dados.get("cpf"))
    email = email_valido(dados.get("email"))
    perfil = dados.get("perfil")
    senha = dados.get("senha", "")

    if not nome:
        erros.append("O nome é obrigatório.")
    if not cpf_valido(cpf):
        erros.append("Informe um CPF válido.")
    if not email:
        erros.append("Informe um e-mail válido.")
    if perfil not in {"A", "F", "G", "U"}:
        erros.append("Selecione um perfil válido.")
    if exige_senha and len(senha) < 8:
        erros.append("A senha deve ter pelo menos 8 caracteres.")
    return erros, nome, cpf, email, perfil, senha


@usuarios_bp.get("")
@perfis_permitidos("A")
def listar():
    pesquisa = request.args.get("pesquisa", "").strip()
    consulta = Usuario.query
    if pesquisa:
        termo = f"%{pesquisa}%"
        consulta = consulta.filter(or_(Usuario.nome.ilike(termo), Usuario.cpf.ilike(termo), Usuario.email.ilike(termo)))
    return render_template("usuarios.html", usuarios=consulta.order_by(Usuario.nome).all(), pesquisa=pesquisa)


@usuarios_bp.route("/novo", methods=["GET", "POST"])
@perfis_permitidos("A")
def novo():
    if request.method == "POST":
        erros, nome, cpf, email, perfil, senha = validar_usuario(request.form, exige_senha=True)
        if not erros:
            db.session.add(Usuario(nome=nome, cpf=cpf, email=email, perfil=perfil, senha=generate_password_hash(senha)))
            try:
                db.session.commit()
                flash("Usuário cadastrado com sucesso.", "success")
                return redirect(url_for("usuarios.listar"))
            except IntegrityError:
                db.session.rollback()
                erros.append("Já existe um usuário com esse CPF ou e-mail.")
        for erro in erros:
            flash(erro, "danger")
    return render_template("usuario_form.html", usuario=None)


@usuarios_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@perfis_permitidos("A")
def editar(id):
    usuario = db.get_or_404(Usuario, id)
    if request.method == "POST":
        erros, nome, cpf, email, perfil, senha = validar_usuario(request.form)
        if senha and len(senha) < 8:
            erros.append("A nova senha deve ter pelo menos 8 caracteres.")
        if not erros:
            usuario.nome, usuario.cpf, usuario.email, usuario.perfil = nome, cpf, email, perfil
            usuario.ativo = request.form.get("ativo") == "1"
            if senha:
                usuario.senha = generate_password_hash(senha)
            try:
                db.session.commit()
                flash("Usuário atualizado com sucesso.", "success")
                return redirect(url_for("usuarios.listar"))
            except IntegrityError:
                db.session.rollback()
                erros.append("Já existe um usuário com esse CPF ou e-mail.")
        for erro in erros:
            flash(erro, "danger")
    return render_template("usuario_form.html", usuario=usuario)


@usuarios_bp.post("/excluir/<int:id>")
@perfis_permitidos("A")
def excluir(id):
    usuario = db.get_or_404(Usuario, id)
    if usuario.id_usuario == g.usuario.id_usuario:
        flash("Você não pode excluir a própria conta.", "danger")
    else:
        usuario.ativo = False
        db.session.commit()
        flash("Usuário inativado com segurança.", "success")
    return redirect(url_for("usuarios.listar"))
