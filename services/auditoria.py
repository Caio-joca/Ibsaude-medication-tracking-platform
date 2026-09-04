import json

from flask import g, has_request_context
from sqlalchemy import event, inspect
from sqlalchemy.orm import Session

from models import LogAuditoria


CAMPOS_SIGILOSOS = {"senha"}


def _seguro(dados):
    return {chave: "[PROTEGIDO]" if chave in CAMPOS_SIGILOSOS else valor for chave, valor in dados.items()}


def _json(dados):
    return json.dumps(_seguro(dados), ensure_ascii=False, default=str, sort_keys=True)


def registrar_log(acao, entidade, id_entidade=None, usuario_id=None, anteriores=None, novos=None):
    if usuario_id is None and has_request_context() and getattr(g, "usuario", None):
        usuario_id = g.usuario.id_usuario
    return LogAuditoria(
        id_usuario=usuario_id,
        acao=acao,
        entidade=entidade,
        id_entidade=id_entidade,
        valores_anteriores=_json(anteriores) if anteriores else None,
        valores_novos=_json(novos) if novos else None,
    )


@event.listens_for(Session, "before_flush")
def auditar_alteracoes(session, _flush_context, _instances):
    if session.info.get("ignorar_auditoria"):
        return

    usuario_id = None
    if has_request_context() and getattr(g, "usuario", None):
        usuario_id = g.usuario.id_usuario

    logs = []
    novos_pendentes = session.info.setdefault("auditoria_novos", [])
    for objeto in list(session.new):
        if isinstance(objeto, LogAuditoria):
            continue
        if not any(item[0] is objeto for item in novos_pendentes):
            novos_pendentes.append((objeto, usuario_id))

    for objeto in list(session.dirty):
        if isinstance(objeto, LogAuditoria) or not session.is_modified(objeto, include_collections=False):
            continue
        estado = inspect(objeto)
        anteriores, novos = {}, {}
        for atributo in estado.mapper.column_attrs:
            historico = estado.attrs[atributo.key].history
            if historico.has_changes():
                anteriores[atributo.key] = historico.deleted[0] if historico.deleted else None
                novos[atributo.key] = historico.added[0] if historico.added else None
        chave = estado.identity[0] if estado.identity else None
        logs.append(registrar_log("ALTERAR", objeto.__tablename__, chave, usuario_id, anteriores, novos))

    for objeto in list(session.deleted):
        if isinstance(objeto, LogAuditoria):
            continue
        estado = inspect(objeto)
        anteriores = {atributo.key: getattr(objeto, atributo.key) for atributo in estado.mapper.column_attrs}
        chave = estado.identity[0] if estado.identity else None
        logs.append(registrar_log("EXCLUIR", objeto.__tablename__, chave, usuario_id, anteriores=anteriores))

    session.add_all(logs)


@event.listens_for(Session, "after_flush_postexec")
def auditar_criacoes_com_identificador(session, _flush_context):
    """Registra inclusões somente depois de o banco atribuir suas chaves primárias."""
    pendentes = session.info.pop("auditoria_novos", [])
    logs = []
    for objeto, usuario_id in pendentes:
        if isinstance(objeto, LogAuditoria):
            continue
        estado = inspect(objeto)
        novos = {atributo.key: getattr(objeto, atributo.key) for atributo in estado.mapper.column_attrs}
        chave = estado.identity[0] if estado.identity else None
        logs.append(registrar_log("CRIAR", objeto.__tablename__, chave, usuario_id, novos=novos))
    if logs:
        session.add_all(logs)
