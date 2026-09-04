from datetime import date, datetime, time, timedelta

from flask import Blueprint, g, redirect, render_template, request, url_for

from sqlalchemy import func

from extensions import db
from models import Aquisicao, Distribuicao, Estoque, Movimentacao, UnidadeDestino, Usuario
from services.estoque import alertas_estoque_baixo, alertas_validade
from utils.seguranca import login_obrigatorio


principal_bp = Blueprint("principal", __name__)


@principal_bp.route("/")
def home():
    if g.get("usuario"):
        return redirect(url_for("principal.painel"))
    return redirect(url_for("auth.login"))


@principal_bp.route("/painel")
@login_obrigatorio
def painel():
    total_lotes = Estoque.query.filter(Estoque.quantidade > 0).count()
    total_unidades = db.session.query(func.coalesce(func.sum(Estoque.quantidade), 0)).scalar()
    total_investido = db.session.query(func.coalesce(func.sum(Aquisicao.vlr_total), 0)).scalar()
    consulta = Movimentacao.query
    inicio = request.args.get("inicio", "")
    fim = request.args.get("fim", "")
    usuario_id = request.args.get("usuario", type=int)
    unidade_id = request.args.get("unidade", type=int)
    try:
        if inicio:
            consulta = consulta.filter(Movimentacao.dt_movimentacao >= date.fromisoformat(inicio))
        if fim:
            limite = datetime.combine(date.fromisoformat(fim) + timedelta(days=1), time.min)
            consulta = consulta.filter(Movimentacao.dt_movimentacao < limite)
    except ValueError:
        inicio = fim = ""
    if usuario_id:
        consulta = consulta.filter(Movimentacao.id_usuario == usuario_id)
    if unidade_id:
        consulta = consulta.join(Movimentacao.distribuicao).filter(Distribuicao.id_destino == unidade_id)
    movimentos = consulta.order_by(Movimentacao.dt_movimentacao.desc()).all()
    entradas = [m for m in movimentos if m.tipo_movimentacao == "E"]
    saidas = [m for m in movimentos if m.tipo_movimentacao == "S"]
    devolucoes = [m for m in movimentos if m.tipo_movimentacao == "D"]
    return render_template(
        "painel.html",
        total_lotes=total_lotes,
        total_unidades=int(total_unidades),
        total_investido=total_investido,
        baixos=alertas_estoque_baixo(),
        vencimentos=alertas_validade(),
        today=date.today(),
        entradas_qtd=sum(m.quantidade for m in entradas),
        entradas_valor=sum(m.vlr_movimentacao for m in entradas),
        saidas_qtd=sum(m.quantidade for m in saidas),
        saidas_valor=sum(m.vlr_movimentacao for m in saidas),
        devolucoes_qtd=sum(m.quantidade for m in devolucoes),
        movimentos_recentes=movimentos[:10],
        usuarios=Usuario.query.filter_by(ativo=True).order_by(Usuario.nome).all(),
        unidades=UnidadeDestino.query.filter_by(ativo=True).order_by(UnidadeDestino.nome).all(),
        filtros={"inicio": inicio, "fim": fim, "usuario": usuario_id, "unidade": unidade_id},
    )
