from datetime import date
from decimal import Decimal

from extensions import db
from models import Distribuicao, DocumentoDistribuicao, Estoque, Movimentacao
from services.estoque import lotes_fefo
from utils.arquivos import validar_e_salvar


def criar_distribuicoes(dados, arquivo, usuario_id):
    try:
        quantidade = int(dados.get("quantidade", 0))
    except (TypeError, ValueError) as erro:
        raise ValueError("Informe uma quantidade inteira válida.") from erro
    if quantidade <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")

    id_medicamento = int(dados["id_medicamento"])
    id_destino = int(dados["id_destino"])
    id_liberador = int(dados["resp_liberacao"])
    recebimento = dados.get("resp_recebimento", "").strip()
    pedido = dados.get("pedido_referencia", "").strip()
    if not recebimento or not pedido:
        raise ValueError("Pedido e responsável pelo recebimento são obrigatórios.")

    lotes = lotes_fefo(id_medicamento)
    saldo = sum(lote.quantidade for lote in lotes)
    if saldo < quantidade:
        raise ValueError(f"Saldo insuficiente. Disponível: {saldo}.")

    restante = quantidade
    criadas = []
    arquivo_salvo = None
    try:
        for lote in lotes:
            if restante == 0:
                break
            retirar = min(restante, lote.quantidade)
            valor_saida = Decimal(lote.aquisicao.vlr_unitario) * retirar
            distribuicao = Distribuicao(
                id_medicamento=id_medicamento,
                id_destino=id_destino,
                id_estoque=lote.id_estoque,
                quantidade=retirar,
                lote=lote.lote,
                dt_validade=lote.dt_validade,
                resp_distribuicao=usuario_id,
                resp_liberacao=id_liberador,
                resp_recebimento=recebimento,
                vlr_saida=valor_saida,
                pedido_referencia=pedido,
            )
            lote.quantidade -= retirar
            db.session.add(distribuicao)
            db.session.flush()
            db.session.add(
                Movimentacao(
                    tipo_movimentacao="S",
                    quantidade=retirar,
                    id_medicamento=id_medicamento,
                    id_aquisicao=lote.id_aquisicao,
                    id_distribuicao=distribuicao.id_distribuicao,
                    id_estoque=lote.id_estoque,
                    id_usuario=usuario_id,
                    vlr_movimentacao=valor_saida,
                    justificativa=f"Distribuição para {distribuicao.unidade.nome if distribuicao.unidade else id_destino}",
                )
            )
            criadas.append(distribuicao)
            restante -= retirar

        arquivo_salvo = validar_e_salvar(arquivo)
        if arquivo_salvo:
            db.session.add(
                DocumentoDistribuicao(
                    id_distribuicao=criadas[0].id_distribuicao,
                    nome_original=arquivo_salvo["nome_original"],
                    nome_armazenado=arquivo_salvo["nome_armazenado"],
                    tipo=arquivo_salvo["tipo"],
                )
            )
        db.session.commit()
    except Exception:
        db.session.rollback()
        if arquivo_salvo:
            arquivo_salvo["caminho"].unlink(missing_ok=True)
        raise
    return criadas


def registrar_devolucao(distribuicao, quantidade, justificativa, usuario_id):
    try:
        quantidade = int(quantidade)
    except (TypeError, ValueError) as erro:
        raise ValueError("Informe uma quantidade inteira válida.") from erro
    disponivel = distribuicao.quantidade - distribuicao.quantidade_devolvida
    if quantidade <= 0 or quantidade > disponivel:
        raise ValueError(f"Quantidade de devolução inválida. Máximo: {disponivel}.")
    justificativa = (justificativa or "").strip()
    if len(justificativa) < 10:
        raise ValueError("Informe uma justificativa com pelo menos 10 caracteres.")

    estoque = distribuicao.estoque
    estoque.quantidade += quantidade
    distribuicao.quantidade_devolvida += quantidade
    valor = Decimal(estoque.aquisicao.vlr_unitario) * quantidade
    db.session.add(
        Movimentacao(
            tipo_movimentacao="D",
            quantidade=quantidade,
            id_medicamento=distribuicao.id_medicamento,
            id_aquisicao=estoque.id_aquisicao,
            id_distribuicao=distribuicao.id_distribuicao,
            id_estoque=estoque.id_estoque,
            id_usuario=usuario_id,
            vlr_movimentacao=valor,
            justificativa=justificativa,
        )
    )
    db.session.commit()
