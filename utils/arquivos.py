from pathlib import Path
from uuid import uuid4
from xml.etree import ElementTree

from flask import current_app
from werkzeug.utils import secure_filename


EXTENSOES_PERMITIDAS = {"pdf", "xml"}


def validar_e_salvar(arquivo):
    if not arquivo or not arquivo.filename:
        return None

    nome_original = secure_filename(arquivo.filename)
    extensao = Path(nome_original).suffix.lower().lstrip(".")
    if extensao not in EXTENSOES_PERMITIDAS:
        raise ValueError("Os anexos devem estar em formato PDF ou XML.")

    conteudo = arquivo.read()
    arquivo.seek(0)
    if extensao == "pdf" and not conteudo.startswith(b"%PDF-"):
        raise ValueError("O arquivo informado não é um PDF válido.")
    if extensao == "xml":
        if b"<!DOCTYPE" in conteudo.upper() or b"<!ENTITY" in conteudo.upper():
            raise ValueError("O XML contém declarações não permitidas.")
        try:
            ElementTree.fromstring(conteudo)
        except ElementTree.ParseError as erro:
            raise ValueError("O arquivo XML é inválido.") from erro

    nome_armazenado = f"{uuid4().hex}.{extensao}"
    destino = Path(current_app.config["UPLOAD_FOLDER"]) / nome_armazenado
    destino.write_bytes(conteudo)
    return {
        "nome_original": nome_original,
        "nome_armazenado": nome_armazenado,
        "tipo": extensao.upper(),
        "caminho": destino,
    }
