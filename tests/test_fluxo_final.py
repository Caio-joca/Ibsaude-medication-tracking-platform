from datetime import date, timedelta
from io import BytesIO

import pytest
from werkzeug.datastructures import FileStorage
from werkzeug.security import generate_password_hash

from app import criar_app
from extensions import db
from models import (
    Distribuicao,
    Estoque,
    Fabricante,
    Fornecedor,
    LogAuditoria,
    Medicamento,
    Movimentacao,
    UnidadeDestino,
    Usuario,
)
from services.aquisicoes import criar_aquisicao
from services.distribuicoes import criar_distribuicoes, registrar_devolucao
from services.estoque import ajustar_estoque, lotes_fefo
from utils.arquivos import validar_e_salvar


@pytest.fixture()
def ambiente():
    app = criar_app("testing")
    contexto = app.app_context()
    contexto.push()
    db.create_all()
    admin = Usuario(nome="Admin", cpf="52998224725", email="admin@teste.local", senha=generate_password_hash("SenhaSegura123"), perfil="A")
    auditor = Usuario(nome="Auditora", cpf="39053344705", email="auditor@teste.local", senha=generate_password_hash("SenhaSegura123"), perfil="U")
    fabricante = Fabricante(nome="Laboratório", cnpj="11222333000181", endereco="Rua A", email="lab@teste.local", telefone="51999999999")
    fornecedor = Fornecedor(nome="Fornecedor", cnpj="11444777000161", endereco="Rua B", email="fornecedor@teste.local", telefone="51888888888")
    unidade = UnidadeDestino(nome="UBS Central", cnpj="27865757000102", endereco="Rua C", email="ubs@teste.local", telefone="51777777777")
    db.session.add_all([admin, auditor, fabricante, fornecedor, unidade])
    db.session.commit()
    medicamento = Medicamento(nome="Medicamento A", classificacao="Comum", codigo="MED-A", uso="Oral", apresentacao="Caixa", principio_ativo="Ativo A", id_fabricante=fabricante.id_fabricante, id_usuario=admin.id_usuario, estoque_minimo=8)
    vencido = Medicamento(nome="Medicamento vencido", classificacao="Comum", codigo="MED-V", uso="Oral", apresentacao="Caixa", principio_ativo="Ativo V", id_fabricante=fabricante.id_fabricante, id_usuario=admin.id_usuario)
    db.session.add_all([medicamento, vencido])
    db.session.commit()

    def adquirir(med, quantidade, validade, nota, lote, valor="2.50"):
        return criar_aquisicao(
            {
                "id_medicamento": str(med.id_medicamento),
                "id_fornecedor": str(fornecedor.id_fornecedor),
                "dt_compra": (date.today() - timedelta(days=60)).isoformat(),
                "dt_validade": validade.isoformat(),
                "quantidade": str(quantidade),
                "vlr_unitario": valor,
                "notafiscal": nota,
                "lote": lote,
            },
            [],
            admin.id_usuario,
        )

    adquirir(medicamento, 5, date.today() + timedelta(days=20), "NF-1", "LOTE-CURTO")
    adquirir(medicamento, 10, date.today() + timedelta(days=120), "NF-2", "LOTE-LONGO")
    adquirir(vencido, 4, date.today() - timedelta(days=1), "NF-3", "LOTE-VENCIDO")
    cliente = app.test_client()
    yield app, cliente, admin, auditor, medicamento, vencido, unidade
    db.session.remove()
    db.drop_all()
    db.engine.dispose()
    contexto.pop()


def login(cliente, email="admin@teste.local"):
    return cliente.post("/login", data={"email": email, "senha": "SenhaSegura123"}, follow_redirects=True)


def test_fefo_saida_devolucao_e_ajuste(ambiente):
    _, _, admin, _, medicamento, _, unidade = ambiente
    lotes = lotes_fefo(medicamento.id_medicamento)
    assert [l.lote for l in lotes] == ["LOTE-CURTO", "LOTE-LONGO"]

    criadas = criar_distribuicoes(
        {
            "id_medicamento": medicamento.id_medicamento,
            "id_destino": unidade.id_destino,
            "resp_liberacao": admin.id_usuario,
            "resp_recebimento": "Maria da Unidade",
            "pedido_referencia": "PED-001",
            "quantidade": 7,
        },
        None,
        admin.id_usuario,
    )
    assert len(criadas) == 2
    assert [item.lote for item in criadas] == ["LOTE-CURTO", "LOTE-LONGO"]
    assert [item.quantidade for item in criadas] == [5, 2]
    assert Estoque.query.filter_by(lote="LOTE-CURTO").one().quantidade == 0
    assert Estoque.query.filter_by(lote="LOTE-LONGO").one().quantidade == 8

    registrar_devolucao(criadas[0], 2, "Devolução por pedido cancelado", admin.id_usuario)
    assert Estoque.query.filter_by(lote="LOTE-CURTO").one().quantidade == 2
    assert Movimentacao.query.filter_by(tipo_movimentacao="D").one().quantidade == 2

    lote_longo = Estoque.query.filter_by(lote="LOTE-LONGO").one()
    assert ajustar_estoque(lote_longo, 6, "Contagem física divergente", admin.id_usuario) == -2
    assert Movimentacao.query.filter_by(tipo_movimentacao="A").one().justificativa


def test_bloqueia_saldo_insuficiente_lote_vencido_e_devolucao_excedente(ambiente):
    _, _, admin, _, medicamento, vencido, unidade = ambiente
    dados = {"id_destino": unidade.id_destino, "resp_liberacao": admin.id_usuario, "resp_recebimento": "Maria", "pedido_referencia": "PED-002"}
    with pytest.raises(ValueError, match="Saldo insuficiente"):
        criar_distribuicoes({**dados, "id_medicamento": medicamento.id_medicamento, "quantidade": 99}, None, admin.id_usuario)
    with pytest.raises(ValueError, match="Saldo insuficiente"):
        criar_distribuicoes({**dados, "id_medicamento": vencido.id_medicamento, "quantidade": 1}, None, admin.id_usuario)

    distribuicao = criar_distribuicoes({**dados, "id_medicamento": medicamento.id_medicamento, "quantidade": 1}, None, admin.id_usuario)[0]
    with pytest.raises(ValueError, match="Máximo"):
        registrar_devolucao(distribuicao, 2, "Quantidade maior que a saída", admin.id_usuario)


def test_auditoria_guarda_identificador_e_eh_imutavel(ambiente):
    log = LogAuditoria.query.filter_by(acao="CRIAR", entidade="medicamentos").first()
    assert log is not None
    assert log.id_entidade is not None
    assert "MED-A" in (log.valores_novos or "")
    log.acao = "ALTERADO INDEVIDAMENTE"
    with pytest.raises(ValueError, match="imutáveis"):
        db.session.commit()
    db.session.rollback()


def test_perfis_xss_consultas_e_cabecalhos(ambiente):
    app, cliente, _, auditor, _, _, _ = ambiente
    login(cliente, auditor.email)
    resposta = cliente.post("/medicamentos/novo", data={"nome": "Não autorizado"}, follow_redirects=True)
    assert resposta.status_code == 200
    assert Medicamento.query.filter_by(nome="Não autorizado").first() is None

    fabricante = Fabricante(nome="<script>alert(1)</script>", cnpj="04252011000110", endereco="Rua X", email="x@teste.local", telefone="51000000000")
    db.session.add(fabricante)
    db.session.commit()
    cliente.post("/logout")
    login(cliente)
    resposta = cliente.get("/fabricantes?pesquisa=%27%20OR%201%3D1--")
    assert resposta.status_code == 200
    resposta = cliente.get("/fabricantes")
    assert b"<script>alert(1)</script>" not in resposta.data
    assert b"&lt;script&gt;alert(1)&lt;/script&gt;" in resposta.data
    assert resposta.headers["X-Content-Type-Options"] == "nosniff"
    assert resposta.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'self'" in resposta.headers["Content-Security-Policy"]
    assert resposta.headers["Cache-Control"] == "no-store, private"

    app.config["WTF_CSRF_ENABLED"] = True
    assert cliente.post("/logout").status_code == 400


def test_exportacoes_e_filtros(ambiente):
    _, cliente, _, _, _, _, _ = ambiente
    login(cliente)
    painel = cliente.get("/painel?inicio=2020-01-01&fim=2030-01-01")
    assert painel.status_code == 200
    assert "Painel gerencial" in painel.get_data(as_text=True)
    pdf = cliente.get("/relatorios/movimentacoes.pdf")
    excel = cliente.get("/relatorios/movimentacoes.xlsx")
    assert pdf.status_code == 200 and pdf.data.startswith(b"%PDF-")
    assert excel.status_code == 200 and excel.data.startswith(b"PK")


def test_upload_rejeita_extensao_disfarce_e_xml_perigoso(ambiente):
    arquivo = FileStorage(stream=BytesIO(b"nao e pdf"), filename="nota.pdf")
    with pytest.raises(ValueError, match="PDF.*válido"):
        validar_e_salvar(arquivo)
    arquivo = FileStorage(stream=BytesIO(b"conteudo"), filename="malware.exe")
    with pytest.raises(ValueError, match="PDF ou XML"):
        validar_e_salvar(arquivo)
    xml = b'<?xml version="1.0"?><!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]><x>&e;</x>'
    arquivo = FileStorage(stream=BytesIO(xml), filename="nota.xml")
    with pytest.raises(ValueError, match="XML"):
        validar_e_salvar(arquivo)
