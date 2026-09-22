import unittest

from werkzeug.security import generate_password_hash

from app import criar_app
from extensions import db
from models import Aquisicao, Estoque, Fabricante, Fornecedor, Medicamento, Movimentacao, Usuario


class FluxoAteTarefa50Test(unittest.TestCase):
    def setUp(self):
        self.app = criar_app("testing")
        self.contexto = self.app.app_context()
        self.contexto.push()
        db.create_all()
        db.session.add(
            Usuario(
                nome="Administrador",
                cpf="52998224725",
                email="admin@ibsaude.test",
                senha=generate_password_hash("SenhaSegura123"),
                perfil="A",
            )
        )
        db.session.commit()
        self.cliente = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.contexto.pop()

    def login(self):
        return self.cliente.post(
            "/login",
            data={"email": "admin@ibsaude.test", "senha": "SenhaSegura123"},
            follow_redirects=True,
        )

    def test_paginas_privadas_exigem_login(self):
        resposta = self.cliente.get("/usuarios")
        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/login", resposta.location)

    def test_fluxo_completo_de_entrada(self):
        self.assertEqual(self.login().status_code, 200)

        resposta = self.cliente.post(
            "/fabricantes/novo",
            data={
                "nome": "Fabricante Teste",
                "cnpj": "11222333000181",
                "endereco": "Rua A",
                "email": "fabricante@example.com",
                "telefone": "51999999999",
            },
        )
        self.assertEqual(resposta.status_code, 302)

        resposta = self.cliente.post(
            "/fornecedores/novo",
            data={
                "nome": "Fornecedor Teste",
                "cnpj": "11444777000161",
                "endereco": "Rua B",
                "email": "fornecedor@example.com",
                "telefone": "51888888888",
            },
        )
        self.assertEqual(resposta.status_code, 302)

        fabricante = Fabricante.query.one()
        fornecedor = Fornecedor.query.one()
        resposta = self.cliente.post(
            "/medicamentos/novo",
            data={
                "nome": "Medicamento Teste",
                "classificacao": "Uso contínuo",
                "codigo": "MED-001",
                "uso": "Teste",
                "apresentacao": "Comprimido",
                "principio_ativo": "Substância teste",
                "id_fabricante": fabricante.id_fabricante,
            },
        )
        self.assertEqual(resposta.status_code, 302)

        medicamento = Medicamento.query.one()
        resposta = self.cliente.post(
            "/aquisicoes/nova",
            data={
                "id_medicamento": medicamento.id_medicamento,
                "id_fornecedor": fornecedor.id_fornecedor,
                "dt_compra": "2026-08-01",
                "dt_validade": "2027-08-01",
                "quantidade": "10",
                "vlr_unitario": "2.50",
                "notafiscal": "NF-001",
                "lote": "LOTE-001",
            },
        )
        self.assertEqual(resposta.status_code, 302)

        aquisicao = Aquisicao.query.one()
        self.assertEqual(float(aquisicao.vlr_total), 25.0)
        self.assertEqual(Estoque.query.one().quantidade, 10)
        movimentacao = Movimentacao.query.one()
        self.assertEqual(movimentacao.tipo_movimentacao, "E")
        self.assertEqual(movimentacao.quantidade, 10)

    def test_exclusao_de_usuario_nao_aceita_get(self):
        self.login()
        resposta = self.cliente.get("/usuarios/excluir/1")
        self.assertEqual(resposta.status_code, 405)


if __name__ == "__main__":
    unittest.main()
