from flask import Blueprint, current_app, flash, g, redirect, render_template, request, send_from_directory, url_for
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Aquisicao, DocumentoAquisicao, Fornecedor, Medicamento
from services.aquisicoes import criar_aquisicao
from utils.seguranca import perfis_permitidos


aquisicoes_bp = Blueprint("aquisicoes", __name__, url_prefix="/aquisicoes")


@aquisicoes_bp.get("")
@perfis_permitidos("A", "F", "G", "U")
def listar():
    aquisicoes = Aquisicao.query.order_by(Aquisicao.dt_entrada.desc()).all()
    return render_template("aquisicoes/lista.html", aquisicoes=aquisicoes)


@aquisicoes_bp.route("/nova", methods=["GET", "POST"])
@perfis_permitidos("A", "F", "G")
def nova():
    if request.method == "POST":
        try:
            aquisicao = criar_aquisicao(request.form, request.files.getlist("documentos"), g.usuario.id_usuario)
            flash("Aquisição registrada; estoque e movimentação de entrada foram atualizados.", "success")
            return redirect(url_for("aquisicoes.detalhe", id=aquisicao.id_aquisicao))
        except (ValueError, KeyError) as erro:
            db.session.rollback()
            flash(str(erro), "danger")
        except IntegrityError:
            db.session.rollback()
            flash("Esta aquisição parece duplicada: confira fornecedor, nota fiscal, medicamento e lote.", "danger")

    return render_template(
        "aquisicoes/form.html",
        fornecedores=Fornecedor.query.filter_by(ativo=True).order_by(Fornecedor.nome).all(),
        medicamentos=Medicamento.query.filter_by(ativo=True).order_by(Medicamento.nome).all(),
    )


@aquisicoes_bp.get("/<int:id>")
@perfis_permitidos("A", "F", "G", "U")
def detalhe(id):
    return render_template("aquisicoes/detalhe.html", aquisicao=db.get_or_404(Aquisicao, id))


@aquisicoes_bp.get("/documentos/<int:id>")
@perfis_permitidos("A", "F", "G", "U")
def documento(id):
    documento = db.get_or_404(DocumentoAquisicao, id)
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        documento.nome_armazenado,
        as_attachment=True,
        download_name=documento.nome_original,
    )
