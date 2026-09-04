from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func

from extensions import db
from models import Estoque, Medicamento, Movimentacao


def lotes_fefo(id_medicamento, incluir_vencidos=False):
    consulta = Estoque.query.filter(Estoque.id_medicamento == id_medicamento, Estoque.quantidade > 0)
    if not incluir_vencidos:
        consulta = consulta.filter(Estoque.dt_validade >= date.today())
    return consulta.order_by(Estoque.dt_validade.asc(), Estoque.id_aquisicao.asc()).all()


def saldo_por_medicamento():
    return (
        db.session.query(Medicamento, func.coalesce(func.sum(Estoque.quantidade), 0).label("saldo"))
        .outerjoin(Estoque, Estoque.id_medicamento == Medicamento.id_medicamento)
        .group_by(Medicamento.id_medicamento)
        .order_by(Medicamento.nome)
        .all()
    )


def alertas_estoque_baixo():
    return [(medicamento, int(saldo)) for medicamento, saldo in saldo_por_medicamento() if medicamento.ativo and int(saldo) <= medicamento.estoque_minimo]


def alertas_validade(dias=90):
    limite = date.today() + timedelta(days=dias)
    return Estoque.query.filter(Estoque.quantidade > 0, Estoque.dt_validade <= limite).order_by(Estoque.dt_validade).all()


def ajustar_estoque(estoque, nova_quantidade, justificativa, usuario_id):
    try:
        nova_quantidade = int(nova_quantidade)
    except (TypeError, ValueError) as erro:
        raise ValueError("Informe uma quantidade inteira válida.") from erro
    justificativa = (justificativa or "").strip()
    if nova_quantidade < 0:
        raise ValueError("O estoque não pode ficar negativo.")
    if len(justificativa) < 10:
        raise ValueError("A justificativa deve ter pelo menos 10 caracteres.")

    diferenca = nova_quantidade - estoque.quantidade
    if diferenca == 0:
        raise ValueError("A quantidade informada é igual ao saldo atual.")

    valor_unitario = Decimal(estoque.aquisicao.vlr_unitario)
    estoque.quantidade = nova_quantidade
    db.session.add(
        Movimentacao(
            tipo_movimentacao="A",
            quantidade=abs(diferenca),
            id_medicamento=estoque.id_medicamento,
            id_aquisicao=estoque.id_aquisicao,
            id_estoque=estoque.id_estoque,
            id_usuario=usuario_id,
            vlr_movimentacao=valor_unitario * abs(diferenca),
            justificativa=f"{'Acréscimo' if diferenca > 0 else 'Redução'} de inventário: {justificativa}",
        )
    )
    db.session.commit()
    return diferenca
