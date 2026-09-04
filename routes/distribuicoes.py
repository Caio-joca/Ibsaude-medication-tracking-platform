from flask import Blueprint, current_app, flash, g, redirect, render_template, request, send_from_directory, url_for

from extensions import db
from models import Distribuicao, DocumentoDistribuicao, Medicamento, UnidadeDestino, Usuario
from services.distribuicoes import criar_distribuicoes, registrar_devolucao
from utils.seguranca import perfis_permitidos


distribuicoes_bp = Blueprint("distribuicoes", __name__, url_prefix="/distribuicoes")


@distribuicoes_bp.get("")
@perfis_permitidos("A", "F", "G", "U")
def listar():
    unidade_id = request.args.get("unidade", type=int)
    consulta = Distribuicao.query
    if unidade_id:
        consulta = consulta.filter_by(id_destino=unidade_id)
    return render_template(
        "distribuicoes/lista.html",
        distribuicoes=consulta.order_by(Distribuicao.dt_distribuicao.desc()).all(),
        unidades=UnidadeDestino.query.order_by(UnidadeDestino.nome).all(),
        unidade_id=unidade_id,
    )


@distribuicoes_bp.route("/nova", methods=["GET", "POST"])
@perfis_permitidos("A", "F", "G")
def nova():
    if request.method == "POST":
        try:
            criadas = criar_distribuicoes(request.form, request.files.get("documento"), g.usuario.id_usuario)
            flash(f"Distribuição realizada em {len(criadas)} lote(s), seguindo FEFO.", "success")
            return redirect(url_for("distribuicoes.listar"))
        except (ValueError, KeyError) as erro:
            db.session.rollback()
            flash(str(erro), "danger")
    liberadores = Usuario.query.filter(Usuario.ativo.is_(True), Usuario.perfil.in_(["A", "F", "G"])).order_by(Usuario.nome).all()
    return render_template(
        "distribuicoes/form.html",
        medicamentos=Medicamento.query.filter_by(ativo=True).order_by(Medicamento.nome).all(),
        unidades=UnidadeDestino.query.filter_by(ativo=True).order_by(UnidadeDestino.nome).all(),
        liberadores=liberadores,
    )


@distribuicoes_bp.get("/<int:id>")
@perfis_permitidos("A", "F", "G", "U")
def detalhe(id):
    return render_template("distribuicoes/detalhe.html", distribuicao=db.get_or_404(Distribuicao, id))


@distribuicoes_bp.post("/<int:id>/devolver")
@perfis_permitidos("A", "F", "G")
def devolver(id):
    distribuicao = db.get_or_404(Distribuicao, id)
    try:
        registrar_devolucao(distribuicao, request.form.get("quantidade"), request.form.get("justificativa"), g.usuario.id_usuario)
        flash("Devolução registrada e saldo do lote recomposto.", "success")
    except ValueError as erro:
        db.session.rollback()
        flash(str(erro), "danger")
    return redirect(url_for("distribuicoes.detalhe", id=id))


@distribuicoes_bp.get("/documentos/<int:id>")
@perfis_permitidos("A", "F", "G", "U")
def documento(id):
    documento = db.get_or_404(DocumentoDistribuicao, id)
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], documento.nome_armazenado, as_attachment=True, download_name=documento.nome_original)
