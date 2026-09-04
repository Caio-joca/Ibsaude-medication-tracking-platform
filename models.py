from datetime import datetime, timezone

from sqlalchemy import event

from extensions import db


def agora_utc():
    return datetime.now(timezone.utc)


class Usuario(db.Model):
    __tablename__ = "usuarios"
    __table_args__ = (
        db.CheckConstraint("perfil IN ('A', 'F', 'G', 'U')", name="ck_usuario_perfil"),
    )

    id_usuario = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(11), nullable=False, unique=True, index=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    perfil = db.Column(db.String(1), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    criado_em = db.Column(db.DateTime(timezone=True), nullable=False, default=agora_utc)

    medicamentos = db.relationship("Medicamento", back_populates="responsavel")
    aquisicoes = db.relationship("Aquisicao", back_populates="responsavel")


class Fabricante(db.Model):
    __tablename__ = "fabricantes"

    id_fabricante = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False, index=True)
    endereco = db.Column(db.String(255), nullable=False)
    cnpj = db.Column(db.String(14), nullable=False, unique=True, index=True)
    email = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    medicamentos = db.relationship("Medicamento", back_populates="fabricante")


class Fornecedor(db.Model):
    __tablename__ = "fornecedores"

    id_fornecedor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False, index=True)
    endereco = db.Column(db.String(255), nullable=False)
    cnpj = db.Column(db.String(14), nullable=False, unique=True, index=True)
    email = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    aquisicoes = db.relationship("Aquisicao", back_populates="fornecedor")


class UnidadeDestino(db.Model):
    __tablename__ = "unidades_destino"

    id_destino = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False, index=True)
    endereco = db.Column(db.String(255), nullable=False)
    cnpj = db.Column(db.String(14), nullable=False, unique=True, index=True)
    email = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)


class Medicamento(db.Model):
    __tablename__ = "medicamentos"

    id_medicamento = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False, index=True)
    classificacao = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(80), nullable=False, unique=True, index=True)
    uso = db.Column(db.String(255), nullable=False)
    apresentacao = db.Column(db.String(120), nullable=False)
    principio_ativo = db.Column(db.String(150), nullable=False)
    id_fabricante = db.Column(db.Integer, db.ForeignKey("fabricantes.id_fabricante"), nullable=False, index=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=False, index=True)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    estoque_minimo = db.Column(db.Integer, nullable=False, default=0)

    fabricante = db.relationship("Fabricante", back_populates="medicamentos")
    responsavel = db.relationship("Usuario", back_populates="medicamentos")
    aquisicoes = db.relationship("Aquisicao", back_populates="medicamento")


class Aquisicao(db.Model):
    __tablename__ = "aquisicoes"
    __table_args__ = (
        db.CheckConstraint("quantidade > 0", name="ck_aquisicao_quantidade_positiva"),
        db.CheckConstraint("vlr_unitario >= 0", name="ck_aquisicao_valor_positivo"),
        db.UniqueConstraint("id_fornecedor", "notafiscal", "lote", "id_medicamento", name="uq_aquisicao_duplicada"),
    )

    id_aquisicao = db.Column(db.Integer, primary_key=True)
    dt_compra = db.Column(db.Date, nullable=False)
    dt_entrada = db.Column(db.DateTime(timezone=True), nullable=False, default=agora_utc)
    id_fornecedor = db.Column(db.Integer, db.ForeignKey("fornecedores.id_fornecedor"), nullable=False, index=True)
    quantidade = db.Column(db.Integer, nullable=False)
    vlr_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    vlr_total = db.Column(db.Numeric(14, 2), nullable=False)
    notafiscal = db.Column(db.String(100), nullable=False, index=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=False, index=True)
    id_medicamento = db.Column(db.Integer, db.ForeignKey("medicamentos.id_medicamento"), nullable=False, index=True)
    lote = db.Column(db.String(100), nullable=False, index=True)
    dt_validade = db.Column(db.Date, nullable=False, index=True)

    fornecedor = db.relationship("Fornecedor", back_populates="aquisicoes")
    responsavel = db.relationship("Usuario", back_populates="aquisicoes")
    medicamento = db.relationship("Medicamento", back_populates="aquisicoes")
    documentos = db.relationship("DocumentoAquisicao", back_populates="aquisicao", cascade="all, delete-orphan")
    estoque = db.relationship("Estoque", back_populates="aquisicao", uselist=False)
    movimentacoes = db.relationship("Movimentacao", back_populates="aquisicao")


class Estoque(db.Model):
    __tablename__ = "estoques"
    __table_args__ = (
        db.CheckConstraint("quantidade >= 0", name="ck_estoque_nao_negativo"),
        db.UniqueConstraint("id_aquisicao", name="uq_estoque_aquisicao"),
    )

    id_estoque = db.Column(db.Integer, primary_key=True)
    id_medicamento = db.Column(db.Integer, db.ForeignKey("medicamentos.id_medicamento"), nullable=False, index=True)
    id_aquisicao = db.Column(db.Integer, db.ForeignKey("aquisicoes.id_aquisicao"), nullable=False, index=True)
    lote = db.Column(db.String(100), nullable=False, index=True)
    dt_validade = db.Column(db.Date, nullable=False, index=True)
    quantidade = db.Column(db.Integer, nullable=False)

    medicamento = db.relationship("Medicamento")
    aquisicao = db.relationship("Aquisicao", back_populates="estoque")


class Distribuicao(db.Model):
    __tablename__ = "distribuicoes"
    __table_args__ = (
        db.CheckConstraint("quantidade > 0", name="ck_distribuicao_quantidade"),
        db.CheckConstraint("quantidade_devolvida >= 0", name="ck_distribuicao_devolucao"),
    )

    id_distribuicao = db.Column(db.Integer, primary_key=True)
    id_medicamento = db.Column(db.Integer, db.ForeignKey("medicamentos.id_medicamento"), nullable=False)
    id_destino = db.Column(db.Integer, db.ForeignKey("unidades_destino.id_destino"), nullable=False)
    id_estoque = db.Column(db.Integer, db.ForeignKey("estoques.id_estoque"), nullable=False, index=True)
    quantidade = db.Column(db.Integer, nullable=False)
    lote = db.Column(db.String(100), nullable=False)
    dt_validade = db.Column(db.Date, nullable=False)
    dt_distribuicao = db.Column(db.DateTime(timezone=True), nullable=False, default=agora_utc)
    resp_distribuicao = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=False)
    resp_liberacao = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=False)
    resp_recebimento = db.Column(db.String(150), nullable=False)
    vlr_saida = db.Column(db.Numeric(14, 2), nullable=False)
    quantidade_devolvida = db.Column(db.Integer, nullable=False, default=0)
    pedido_referencia = db.Column(db.String(100), nullable=False, index=True)

    medicamento = db.relationship("Medicamento")
    unidade = db.relationship("UnidadeDestino")
    estoque = db.relationship("Estoque")
    distribuidor = db.relationship("Usuario", foreign_keys=[resp_distribuicao])
    liberador = db.relationship("Usuario", foreign_keys=[resp_liberacao])
    documentos = db.relationship("DocumentoDistribuicao", back_populates="distribuicao", cascade="all, delete-orphan")
    movimentacoes = db.relationship("Movimentacao", back_populates="distribuicao")


class Movimentacao(db.Model):
    __tablename__ = "movimentacoes"
    __table_args__ = (
        db.CheckConstraint("tipo_movimentacao IN ('E', 'S', 'D', 'A')", name="ck_movimentacao_tipo"),
        db.CheckConstraint("quantidade > 0", name="ck_movimentacao_quantidade"),
    )

    id_movimentacao = db.Column(db.Integer, primary_key=True)
    tipo_movimentacao = db.Column(db.String(1), nullable=False, index=True)
    dt_movimentacao = db.Column(db.DateTime(timezone=True), nullable=False, default=agora_utc, index=True)
    quantidade = db.Column(db.Integer, nullable=False)
    id_medicamento = db.Column(db.Integer, db.ForeignKey("medicamentos.id_medicamento"), nullable=False, index=True)
    id_aquisicao = db.Column(db.Integer, db.ForeignKey("aquisicoes.id_aquisicao"), nullable=True, index=True)
    id_distribuicao = db.Column(db.Integer, db.ForeignKey("distribuicoes.id_distribuicao"), nullable=True, index=True)
    id_estoque = db.Column(db.Integer, db.ForeignKey("estoques.id_estoque"), nullable=True, index=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=True, index=True)
    vlr_movimentacao = db.Column(db.Numeric(14, 2), nullable=False)
    justificativa = db.Column(db.String(500), nullable=True)

    medicamento = db.relationship("Medicamento")
    aquisicao = db.relationship("Aquisicao", back_populates="movimentacoes")
    distribuicao = db.relationship("Distribuicao", back_populates="movimentacoes")
    estoque = db.relationship("Estoque")
    usuario = db.relationship("Usuario")


class DocumentoAquisicao(db.Model):
    __tablename__ = "documentos_aquisicao"

    id_documento = db.Column(db.Integer, primary_key=True)
    id_aquisicao = db.Column(db.Integer, db.ForeignKey("aquisicoes.id_aquisicao"), nullable=False, index=True)
    nome_original = db.Column(db.String(255), nullable=False)
    nome_armazenado = db.Column(db.String(255), nullable=False, unique=True)
    tipo = db.Column(db.String(10), nullable=False)
    criado_em = db.Column(db.DateTime(timezone=True), nullable=False, default=agora_utc)

    aquisicao = db.relationship("Aquisicao", back_populates="documentos")


class DocumentoDistribuicao(db.Model):
    __tablename__ = "documentos_distribuicao"

    id_documento = db.Column(db.Integer, primary_key=True)
    id_distribuicao = db.Column(db.Integer, db.ForeignKey("distribuicoes.id_distribuicao"), nullable=False, index=True)
    nome_original = db.Column(db.String(255), nullable=False)
    nome_armazenado = db.Column(db.String(255), nullable=False, unique=True)
    tipo = db.Column(db.String(10), nullable=False)
    criado_em = db.Column(db.DateTime(timezone=True), nullable=False, default=agora_utc)

    distribuicao = db.relationship("Distribuicao", back_populates="documentos")


class LogAuditoria(db.Model):
    __tablename__ = "logs_auditoria"

    id_log = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=True, index=True)
    acao = db.Column(db.String(100), nullable=False, index=True)
    entidade = db.Column(db.String(100), nullable=False, index=True)
    id_entidade = db.Column(db.Integer, nullable=True)
    valores_anteriores = db.Column(db.Text, nullable=True)
    valores_novos = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime(timezone=True), nullable=False, default=agora_utc, index=True)

    usuario = db.relationship("Usuario")


@event.listens_for(LogAuditoria, "before_update")
@event.listens_for(LogAuditoria, "before_delete")
def impedir_alteracao_log(*_):
    raise ValueError("Registros de auditoria são imutáveis.")
