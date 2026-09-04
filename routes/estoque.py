from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from extensions import db
from models import Estoque, Movimentacao
from services.estoque import ajustar_estoque, alertas_estoque_baixo, alertas_validade, saldo_por_medicamento
from utils.seguranca import perfis_permitidos


estoque_bp = Blueprint("estoque", __name__, url_prefix="/estoque")


@estoque_bp.get("")
@perfis_permitidos("A", "F", "G", "U")
def listar():
    lotes = Estoque.query.order_by(Estoque.dt_validade, Estoque.lote).all()
    return render_template(
        "estoque/lista.html",
        lotes=lotes,
        saldos=saldo_por_medicamento(),
        baixos=alertas_estoque_baixo(),
        vencimentos=alertas_validade(),
    )


@estoque_bp.get("/movimentacoes")
@perfis_permitidos("A", "F", "G", "U")
def movimentacoes():
    tipo = request.args.get("tipo", "")
    consulta = Movimentacao.query
    if tipo in {"E", "S", "D", "A"}:
        consulta = consulta.filter_by(tipo_movimentacao=tipo)
    return render_template("estoque/movimentacoes.html", movimentacoes=consulta.order_by(Movimentacao.dt_movimentacao.desc()).all(), tipo=tipo)


@estoque_bp.route("/ajustar/<int:id>", methods=["GET", "POST"])
@perfis_permitidos("A", "F", "G")
def ajustar(id):
    estoque = db.get_or_404(Estoque, id)
    if request.method == "POST":
        try:
            ajustar_estoque(estoque, request.form.get("quantidade"), request.form.get("justificativa"), g.usuario.id_usuario)
            flash("Ajuste registrado no inventário e no histórico.", "success")
            return redirect(url_for("estoque.listar"))
        except ValueError as erro:
            db.session.rollback()
            flash(str(erro), "danger")
    return render_template("estoque/ajuste.html", estoque=estoque)
