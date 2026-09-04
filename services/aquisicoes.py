from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from extensions import db
from models import Aquisicao, DocumentoAquisicao, Estoque, Movimentacao
from utils.arquivos import validar_e_salvar


def decimal_monetario(valor):
    try:
        numero = Decimal((valor or "").replace(",", ".")).quantize(Decimal("0.01"))
    except (InvalidOperation, AttributeError):
        raise ValueError("Informe um valor unitário válido.")
    if numero < 0:
        raise ValueError("O valor unitário não pode ser negativo.")
    return numero


def criar_aquisicao(dados, arquivos, usuario_id):
    try:
        quantidade = int(dados.get("quantidade", 0))
    except (TypeError, ValueError):
        raise ValueError("A quantidade deve ser um número inteiro.")
    if quantidade <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")

    nota_fiscal = dados.get("notafiscal", "").strip()
    lote = dados.get("lote", "").strip()
    if not nota_fiscal or not lote:
        raise ValueError("Nota fiscal e lote são obrigatórios.")

    valor_unitario = decimal_monetario(dados.get("vlr_unitario"))
    valor_total = valor_unitario * quantidade
    validade = date.fromisoformat(dados["dt_validade"])
    compra = date.fromisoformat(dados["dt_compra"])
    if validade <= compra:
        raise ValueError("A validade deve ser posterior à data da compra.")

    aquisicao = Aquisicao(
        dt_compra=compra,
        id_fornecedor=int(dados["id_fornecedor"]),
        quantidade=quantidade,
        vlr_unitario=valor_unitario,
        vlr_total=valor_total,
        notafiscal=nota_fiscal,
        id_usuario=usuario_id,
        id_medicamento=int(dados["id_medicamento"]),
        lote=lote,
        dt_validade=validade,
    )
    db.session.add(aquisicao)
    db.session.flush()

    db.session.add(
        Estoque(
            id_medicamento=aquisicao.id_medicamento,
            id_aquisicao=aquisicao.id_aquisicao,
            lote=aquisicao.lote,
            dt_validade=aquisicao.dt_validade,
            quantidade=quantidade,
        )
    )
    db.session.add(
        Movimentacao(
            tipo_movimentacao="E",
            quantidade=quantidade,
            id_medicamento=aquisicao.id_medicamento,
            id_aquisicao=aquisicao.id_aquisicao,
            id_usuario=usuario_id,
            vlr_movimentacao=valor_total,
        )
    )

    arquivos_salvos = []
    try:
        for arquivo in arquivos:
            if not arquivo or not arquivo.filename:
                continue
            salvo = validar_e_salvar(arquivo)
            if not salvo:
                continue
            arquivos_salvos.append(salvo["caminho"])
            db.session.add(
                DocumentoAquisicao(
                    id_aquisicao=aquisicao.id_aquisicao,
                    nome_original=salvo["nome_original"],
                    nome_armazenado=salvo["nome_armazenado"],
                    tipo=salvo["tipo"],
                )
            )
        db.session.commit()
    except Exception:
        db.session.rollback()
        for caminho in arquivos_salvos:
            caminho.unlink(missing_ok=True)
        raise

    return aquisicao
