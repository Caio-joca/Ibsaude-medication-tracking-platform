from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Fabricante, Medicamento
from utils.seguranca import perfis_permitidos


medicamentos_bp = Blueprint("medicamentos", __name__, url_prefix="/medicamentos")


def aplicar_dados(medicamento):
    campos = ["nome", "classificacao", "codigo", "uso", "apresentacao", "principio_ativo"]
    valores = {campo: request.form.get(campo, "").strip() for campo in campos}
    if not all(valores.values()) or not request.form.get("id_fabricante"):
        raise ValueError("Preencha todos os campos obrigatórios.")
    for campo, valor in valores.items():
        setattr(medicamento, campo, valor)
    medicamento.id_fabricante = int(request.form["id_fabricante"])
    medicamento.id_usuario = g.usuario.id_usuario
    try:
        medicamento.estoque_minimo = int(request.form.get("estoque_minimo", 0))
    except ValueError as erro:
        raise ValueError("O estoque mínimo deve ser um número inteiro.") from erro
    if medicamento.estoque_minimo < 0:
        raise ValueError("O estoque mínimo não pode ser negativo.")


@medicamentos_bp.get("")
@perfis_permitidos("A", "F", "G", "U")
def listar():
    pesquisa = request.args.get("pesquisa", "").strip()
    consulta = Medicamento.query
    if pesquisa:
        termo = f"%{pesquisa}%"
        consulta = consulta.filter(or_(Medicamento.nome.ilike(termo), Medicamento.codigo.ilike(termo), Medicamento.principio_ativo.ilike(termo)))
    return render_template("medicamentos/lista.html", medicamentos=consulta.order_by(Medicamento.nome).all(), pesquisa=pesquisa)


@medicamentos_bp.route("/novo", methods=["GET", "POST"])
@perfis_permitidos("A", "F", "G")
def novo():
    medicamento = Medicamento()
    if request.method == "POST":
        try:
            aplicar_dados(medicamento)
            db.session.add(medicamento)
            db.session.commit()
            flash("Medicamento cadastrado com sucesso.", "success")
            return redirect(url_for("medicamentos.listar"))
        except ValueError as erro:
            flash(str(erro), "danger")
        except IntegrityError:
            db.session.rollback()
            flash("O código informado já pertence a outro medicamento.", "danger")
    return render_template("medicamentos/form.html", medicamento=None, fabricantes=Fabricante.query.filter_by(ativo=True).order_by(Fabricante.nome).all())


@medicamentos_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@perfis_permitidos("A", "F", "G")
def editar(id):
    medicamento = db.get_or_404(Medicamento, id)
    if request.method == "POST":
        try:
            aplicar_dados(medicamento)
            db.session.commit()
            flash("Medicamento atualizado com sucesso.", "success")
            return redirect(url_for("medicamentos.detalhe", id=id))
        except ValueError as erro:
            flash(str(erro), "danger")
        except IntegrityError:
            db.session.rollback()
            flash("O código informado já pertence a outro medicamento.", "danger")
    return render_template("medicamentos/form.html", medicamento=medicamento, fabricantes=Fabricante.query.filter_by(ativo=True).order_by(Fabricante.nome).all())


@medicamentos_bp.get("/<int:id>")
@perfis_permitidos("A", "F", "G", "U")
def detalhe(id):
    return render_template("medicamentos/detalhe.html", medicamento=db.get_or_404(Medicamento, id))


@medicamentos_bp.post("/inativar/<int:id>")
@perfis_permitidos("A", "F", "G")
def inativar(id):
    medicamento = db.get_or_404(Medicamento, id)
    medicamento.ativo = False
    db.session.commit()
    flash("Medicamento inativado; seu histórico foi preservado.", "success")
    return redirect(url_for("medicamentos.listar"))
