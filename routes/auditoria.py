from flask import Blueprint, render_template, request

from models import Aquisicao, Distribuicao, LogAuditoria, Medicamento, Movimentacao
from utils.seguranca import perfis_permitidos


auditoria_bp = Blueprint("auditoria", __name__, url_prefix="/auditoria")


@auditoria_bp.get("")
@perfis_permitidos("A", "U")
def listar():
    entidade = request.args.get("entidade", "").strip()
    consulta = LogAuditoria.query
    if entidade:
        consulta = consulta.filter(LogAuditoria.entidade == entidade)
    return render_template("auditoria/lista.html", logs=consulta.order_by(LogAuditoria.criado_em.desc()).limit(1000).all(), entidade=entidade)


@auditoria_bp.get("/rastreabilidade")
@perfis_permitidos("A", "U")
def rastreabilidade():
    medicamento_id = request.args.get("medicamento", type=int)
    medicamento = Medicamento.query.get(medicamento_id) if medicamento_id else None
    aquisicoes = Aquisicao.query.filter_by(id_medicamento=medicamento_id).all() if medicamento_id else []
    distribuicoes = Distribuicao.query.filter_by(id_medicamento=medicamento_id).order_by(Distribuicao.dt_distribuicao).all() if medicamento_id else []
    movimentacoes = Movimentacao.query.filter_by(id_medicamento=medicamento_id).order_by(Movimentacao.dt_movimentacao).all() if medicamento_id else []
    return render_template(
        "auditoria/rastreabilidade.html",
        medicamentos=Medicamento.query.order_by(Medicamento.nome).all(),
        medicamento=medicamento,
        aquisicoes=aquisicoes,
        distribuicoes=distribuicoes,
        movimentacoes=movimentacoes,
    )
