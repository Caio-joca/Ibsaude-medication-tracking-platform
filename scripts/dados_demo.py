"""Carga idempotente de dados inteiramente fictícios para demonstração local."""

from collections import Counter
from datetime import date, timedelta
from io import BytesIO

from werkzeug.datastructures import FileStorage
from werkzeug.security import generate_password_hash

from extensions import db
from models import (
    Aquisicao,
    Distribuicao,
    Estoque,
    Fabricante,
    Fornecedor,
    Medicamento,
    Movimentacao,
    UnidadeDestino,
    Usuario,
)
from services.aquisicoes import criar_aquisicao
from services.distribuicoes import criar_distribuicoes, registrar_devolucao
from services.estoque import ajustar_estoque


def _obter_ou_criar(modelo, criterio, valores, criados, nome_contagem):
    registro = modelo.query.filter_by(**criterio).first()
    if registro:
        return registro
    registro = modelo(**valores)
    db.session.add(registro)
    db.session.flush()
    criados[nome_contagem] += 1
    return registro


def _xml_demo(nome, categoria, referencia):
    conteudo = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<documento categoria="{categoria}" ambiente="demonstracao">\n'
        f"  <referencia>{referencia}</referencia>\n"
        "  <observacao>Documento ficticio sem valor fiscal ou institucional.</observacao>\n"
        "</documento>\n"
    ).encode("utf-8")
    return FileStorage(stream=BytesIO(conteudo), filename=nome, content_type="application/xml")


def carregar_dados_demo(administrador, senha_demo):
    criados = Counter()
    hoje = date.today()

    usuarios_definicoes = [
        {
            "nome": "Marina Farmacêutica — Demonstração",
            "cpf": "11144477735",
            "email": "farmaceutica.demo@example.com",
            "perfil": "F",
        },
        {
            "nome": "Carlos Gestor — Demonstração",
            "cpf": "39053344705",
            "email": "gestor.demo@example.com",
            "perfil": "G",
        },
        {
            "nome": "Renata Auditora — Demonstração",
            "cpf": "74185296355",
            "email": "auditor.demo@example.com",
            "perfil": "U",
        },
    ]
    usuarios_criados = 0
    emails_criados = []
    usuarios = {}
    for definicao in usuarios_definicoes:
        existente = Usuario.query.filter(
            (Usuario.email == definicao["email"]) | (Usuario.cpf == definicao["cpf"])
        ).first()
        if existente:
            usuarios[definicao["perfil"]] = existente
            continue
        usuario = Usuario(**definicao, senha=generate_password_hash(senha_demo))
        db.session.add(usuario)
        db.session.flush()
        usuarios[definicao["perfil"]] = usuario
        usuarios_criados += 1
        emails_criados.append(definicao["email"])
        criados["usuários"] += 1

    fabricantes_definicoes = [
        ("Farmacêutica Horizonte — Demo", "10000001000190", "Avenida das Ciências, 100"),
        ("Laboratório Vida Clara — Demo", "10000002000134", "Rua da Pesquisa, 220"),
        ("Indústria Saúde Brasil — Demo", "10000003000189", "Rodovia Industrial, 3500"),
    ]
    fabricantes = {}
    for nome, cnpj, endereco in fabricantes_definicoes:
        fabricantes[cnpj] = _obter_ou_criar(
            Fabricante,
            {"cnpj": cnpj},
            {
                "nome": nome,
                "cnpj": cnpj,
                "endereco": endereco,
                "email": f"contato{cnpj[:2]}@example.com",
                "telefone": "11900001000",
            },
            criados,
            "fabricantes",
        )

    fornecedores_definicoes = [
        ("Distribuidora Bem-Estar — Demo", "20000001000143", "Rua dos Estoques, 45"),
        ("Central de Medicamentos — Demo", "20000002000198", "Avenida Logística, 780"),
    ]
    fornecedores = {}
    for nome, cnpj, endereco in fornecedores_definicoes:
        fornecedores[cnpj] = _obter_ou_criar(
            Fornecedor,
            {"cnpj": cnpj},
            {
                "nome": nome,
                "cnpj": cnpj,
                "endereco": endereco,
                "email": f"fornecedor{cnpj[:2]}@example.com",
                "telefone": "11900002000",
            },
            criados,
            "fornecedores",
        )

    unidades_definicoes = [
        ("UBS Centro — Demo", "30000001000105", "Praça Central, 10"),
        ("UBS Norte — Demo", "30000002000141", "Rua das Flores, 250"),
        ("UBS Sul — Demo", "30000003000196", "Avenida do Parque, 600"),
        ("Pronto Atendimento Municipal — Demo", "30000004000130", "Rua da Saúde, 24"),
    ]
    unidades = {}
    for nome, cnpj, endereco in unidades_definicoes:
        unidades[cnpj] = _obter_ou_criar(
            UnidadeDestino,
            {"cnpj": cnpj},
            {
                "nome": nome,
                "cnpj": cnpj,
                "endereco": endereco,
                "email": f"unidade{cnpj[:2]}@example.com",
                "telefone": "11900003000",
            },
            criados,
            "unidades",
        )

    responsavel = usuarios.get("F", administrador)
    medicamentos_definicoes = [
        ("MED-DEMO-001", "Dipirona 500 mg — Demo", "Analgésico", "Uso oral", "Comprimido", "Dipirona monoidratada", "10000001000190", 100),
        ("MED-DEMO-002", "Amoxicilina 500 mg — Demo", "Antibiótico", "Uso oral", "Cápsula", "Amoxicilina", "10000002000134", 80),
        ("MED-DEMO-003", "Losartana 50 mg — Demo", "Anti-hipertensivo", "Uso oral", "Comprimido", "Losartana potássica", "10000003000189", 120),
        ("MED-DEMO-004", "Metformina 850 mg — Demo", "Antidiabético", "Uso oral", "Comprimido", "Cloridrato de metformina", "10000001000190", 100),
        ("MED-DEMO-005", "Omeprazol 20 mg — Demo", "Antiulceroso", "Uso oral", "Cápsula", "Omeprazol", "10000002000134", 60),
        ("MED-DEMO-006", "Soro fisiológico 0,9% — Demo", "Solução eletrolítica", "Uso externo ou intravenoso", "Frasco 500 ml", "Cloreto de sódio", "10000003000189", 40),
    ]
    medicamentos = {}
    for codigo, nome, classificacao, uso, apresentacao, principio, cnpj_fabricante, minimo in medicamentos_definicoes:
        medicamentos[codigo] = _obter_ou_criar(
            Medicamento,
            {"codigo": codigo},
            {
                "codigo": codigo,
                "nome": nome,
                "classificacao": classificacao,
                "uso": uso,
                "apresentacao": apresentacao,
                "principio_ativo": principio,
                "id_fabricante": fabricantes[cnpj_fabricante].id_fabricante,
                "id_usuario": responsavel.id_usuario,
                "estoque_minimo": minimo,
            },
            criados,
            "medicamentos",
        )

    db.session.commit()

    aquisicoes_definicoes = [
        ("NF-DEMO-001", "DIP-A-DEMO", "MED-DEMO-001", "20000001000143", 180, "0.32", 180),
        ("NF-DEMO-002", "DIP-B-DEMO", "MED-DEMO-001", "20000002000198", 220, "0.30", 420),
        ("NF-DEMO-003", "AMO-A-DEMO", "MED-DEMO-002", "20000001000143", 150, "0.75", 240),
        ("NF-DEMO-004", "LOS-A-DEMO", "MED-DEMO-003", "20000002000198", 300, "0.18", 540),
        ("NF-DEMO-005", "MET-A-DEMO", "MED-DEMO-004", "20000001000143", 250, "0.24", 400),
        ("NF-DEMO-006", "OME-A-DEMO", "MED-DEMO-005", "20000002000198", 120, "0.38", 300),
        ("NF-DEMO-007", "SOR-A-DEMO", "MED-DEMO-006", "20000001000143", 80, "4.60", 60),
    ]
    for nota, lote, codigo, cnpj_fornecedor, quantidade, valor, dias_validade in aquisicoes_definicoes:
        medicamento = medicamentos[codigo]
        fornecedor = fornecedores[cnpj_fornecedor]
        existente = Aquisicao.query.filter_by(
            id_fornecedor=fornecedor.id_fornecedor,
            notafiscal=nota,
            lote=lote,
            id_medicamento=medicamento.id_medicamento,
        ).first()
        if existente:
            continue
        criar_aquisicao(
            {
                "dt_compra": (hoje - timedelta(days=30)).isoformat(),
                "dt_validade": (hoje + timedelta(days=dias_validade)).isoformat(),
                "quantidade": str(quantidade),
                "vlr_unitario": valor,
                "notafiscal": nota,
                "lote": lote,
                "id_fornecedor": str(fornecedor.id_fornecedor),
                "id_medicamento": str(medicamento.id_medicamento),
            },
            [_xml_demo(f"{nota.lower()}.xml", "aquisicao", nota)],
            administrador.id_usuario,
        )
        criados["aquisições"] += 1

    liberador = responsavel
    distribuicoes_definicoes = [
        ("PED-DEMO-001", "MED-DEMO-001", "30000001000105", 230, "Joana Ribeiro — Demonstração"),
        ("PED-DEMO-002", "MED-DEMO-002", "30000002000141", 90, "Paulo Mendes — Demonstração"),
        ("PED-DEMO-003", "MED-DEMO-003", "30000003000196", 220, "Luciana Souza — Demonstração"),
        ("PED-DEMO-004", "MED-DEMO-004", "30000004000130", 40, "Roberto Lima — Demonstração"),
    ]
    for pedido, codigo, cnpj_unidade, quantidade, recebedor in distribuicoes_definicoes:
        if Distribuicao.query.filter_by(pedido_referencia=pedido).first():
            continue
        medicamento = medicamentos[codigo]
        unidade = unidades[cnpj_unidade]
        distribuicoes = criar_distribuicoes(
            {
                "quantidade": str(quantidade),
                "id_medicamento": str(medicamento.id_medicamento),
                "id_destino": str(unidade.id_destino),
                "resp_liberacao": str(liberador.id_usuario),
                "resp_recebimento": recebedor,
                "pedido_referencia": pedido,
            },
            _xml_demo(f"{pedido.lower()}.xml", "distribuicao", pedido),
            administrador.id_usuario,
        )
        criados["registros de distribuição"] += len(distribuicoes)

    devolucao = Distribuicao.query.filter_by(pedido_referencia="PED-DEMO-002").order_by(Distribuicao.id_distribuicao).first()
    if devolucao and devolucao.quantidade_devolvida == 0:
        registrar_devolucao(
            devolucao,
            10,
            "[DEMO] Retorno de unidades não utilizadas pela UBS.",
            administrador.id_usuario,
        )
        criados["devoluções"] += 1

    estoque_omeprazol = (
        Estoque.query.join(Medicamento)
        .filter(Medicamento.codigo == "MED-DEMO-005", Estoque.lote == "OME-A-DEMO")
        .first()
    )
    ajuste_existente = Movimentacao.query.filter(
        Movimentacao.tipo_movimentacao == "A",
        Movimentacao.justificativa.contains("[DEMO]"),
        Movimentacao.id_estoque == (estoque_omeprazol.id_estoque if estoque_omeprazol else -1),
    ).first()
    if estoque_omeprazol and not ajuste_existente:
        ajustar_estoque(
            estoque_omeprazol,
            estoque_omeprazol.quantidade - 3,
            "[DEMO] Divergência fictícia na contagem do inventário.",
            administrador.id_usuario,
        )
        criados["ajustes"] += 1

    totais = {
        "usuários": Usuario.query.count(),
        "fabricantes": Fabricante.query.count(),
        "fornecedores": Fornecedor.query.count(),
        "unidades": UnidadeDestino.query.count(),
        "medicamentos": Medicamento.query.count(),
        "aquisições": Aquisicao.query.count(),
        "lotes": Estoque.query.count(),
        "distribuições": Distribuicao.query.count(),
        "movimentações": Movimentacao.query.count(),
    }
    return {
        "criados": dict(criados),
        "totais": totais,
        "usuarios_criados": usuarios_criados,
        "emails_criados": emails_criados,
    }
