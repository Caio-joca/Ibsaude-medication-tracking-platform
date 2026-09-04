from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Fabricante, Fornecedor, UnidadeDestino
from utils.seguranca import perfis_permitidos
from utils.validacao import cnpj_valido, email_valido, somente_digitos


cadastros_bp = Blueprint("cadastros", __name__)


def dados_cadastro(modelo, titulo, endpoint, pesquisa=""):
    consulta = modelo.query
    if pesquisa:
        termo = f"%{pesquisa}%"
        consulta = consulta.filter(or_(modelo.nome.ilike(termo), modelo.cnpj.ilike(termo), modelo.email.ilike(termo)))
    return render_template("cadastros/lista.html", itens=consulta.order_by(modelo.nome).all(), titulo=titulo, endpoint=endpoint, pesquisa=pesquisa)


def salvar_cadastro(modelo, titulo, endpoint, objeto=None):
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        endereco = request.form.get("endereco", "").strip()
        cnpj = somente_digitos(request.form.get("cnpj"))
        email = email_valido(request.form.get("email"))
        telefone = request.form.get("telefone", "").strip()
        erros = []
        if not all((nome, endereco, telefone)):
            erros.append("Preencha todos os campos obrigatórios.")
        if not cnpj_valido(cnpj):
            erros.append("Informe um CNPJ válido.")
        if not email:
            erros.append("Informe um e-mail válido.")
        if not erros:
            objeto = objeto or modelo()
            objeto.nome, objeto.endereco, objeto.cnpj = nome, endereco, cnpj
            objeto.email, objeto.telefone = email, telefone
            db.session.add(objeto)
            try:
                db.session.commit()
                flash(f"{titulo} salvo com sucesso.", "success")
                return redirect(url_for(f"cadastros.{endpoint}_listar"))
            except IntegrityError:
                db.session.rollback()
                erros.append("Já existe um cadastro com esse CNPJ.")
        for erro in erros:
            flash(erro, "danger")
    return render_template("cadastros/form.html", item=objeto, titulo=titulo, endpoint=endpoint)


@cadastros_bp.get("/fabricantes")
@perfis_permitidos("A", "F", "G")
def fabricantes_listar():
    return dados_cadastro(Fabricante, "Fabricante", "fabricantes", request.args.get("pesquisa", "").strip())


@cadastros_bp.route("/fabricantes/novo", methods=["GET", "POST"])
@perfis_permitidos("A", "F", "G")
def fabricantes_novo():
    return salvar_cadastro(Fabricante, "Fabricante", "fabricantes")


@cadastros_bp.route("/fabricantes/editar/<int:id>", methods=["GET", "POST"])
@perfis_permitidos("A", "F", "G")
def fabricantes_editar(id):
    return salvar_cadastro(Fabricante, "Fabricante", "fabricantes", db.get_or_404(Fabricante, id))


@cadastros_bp.get("/fornecedores")
@perfis_permitidos("A", "F", "G")
def fornecedores_listar():
    return dados_cadastro(Fornecedor, "Fornecedor", "fornecedores", request.args.get("pesquisa", "").strip())


@cadastros_bp.route("/fornecedores/novo", methods=["GET", "POST"])
@perfis_permitidos("A", "F", "G")
def fornecedores_novo():
    return salvar_cadastro(Fornecedor, "Fornecedor", "fornecedores")


@cadastros_bp.route("/fornecedores/editar/<int:id>", methods=["GET", "POST"])
@perfis_permitidos("A", "F", "G")
def fornecedores_editar(id):
    return salvar_cadastro(Fornecedor, "Fornecedor", "fornecedores", db.get_or_404(Fornecedor, id))


@cadastros_bp.get("/unidades")
@perfis_permitidos("A", "F", "G")
def unidades_listar():
    return dados_cadastro(UnidadeDestino, "Unidade de destino", "unidades", request.args.get("pesquisa", "").strip())


@cadastros_bp.route("/unidades/novo", methods=["GET", "POST"])
@perfis_permitidos("A", "F", "G")
def unidades_novo():
    return salvar_cadastro(UnidadeDestino, "Unidade de destino", "unidades")


@cadastros_bp.route("/unidades/editar/<int:id>", methods=["GET", "POST"])
@perfis_permitidos("A", "F", "G")
def unidades_editar(id):
    return salvar_cadastro(UnidadeDestino, "Unidade de destino", "unidades", db.get_or_404(UnidadeDestino, id))
