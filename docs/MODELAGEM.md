# Modelagem de dados

## Entidades e relacionamentos

- `usuarios`: identidade, hash de senha, perfil, estado e data de criação.
- `fabricantes`, `fornecedores`, `unidades_destino`: cadastros institucionais.
- `medicamentos`: catálogo, fabricante, responsável e estoque mínimo.
- `aquisicoes`: entrada comercial por fornecedor, nota, medicamento, lote e validade.
- `documentos_aquisicao`: anexos PDF/XML de uma aquisição.
- `estoques`: saldo físico individual por aquisição/lote.
- `distribuicoes`: saídas por unidade, lote e três responsáveis.
- `documentos_distribuicao`: documento formal associado a uma saída.
- `movimentacoes`: razão de entradas (E), saídas (S), devoluções (D) e ajustes (A).
- `logs_auditoria`: alterações com autor, instante, entidade, chave e valores anteriores/novos.

Fluxo principal: `fornecedor → aquisição → estoque/lote → distribuição → unidade`. A movimentação aponta para medicamento, lote, aquisição ou distribuição correspondentes, permitindo rastrear origem e destino.

## Integridade

- CPF, e-mail, CNPJ e código do medicamento são únicos.
- Quantidades de aquisição, distribuição e movimentação devem ser positivas; saldo não pode ser negativo.
- Uma aquisição gera exatamente um registro de estoque.
- Fornecedor + nota fiscal + lote + medicamento impedem entrada duplicada.
- Perfis e tipos de movimentação usam listas fechadas.
- Usuários e medicamentos são inativados, preservando referências históricas.
- Atualizar ou excluir `LogAuditoria` é bloqueado pelo modelo.

O schema é versionado por Alembic em `migrations/` e utiliza tipos compatíveis com SQLite e PostgreSQL.
