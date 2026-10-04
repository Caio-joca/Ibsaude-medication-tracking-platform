# Manual por perfil

## Administrador

1. Entre com a conta criada por `flask criar-admin`.
2. Cadastre usuários e atribua o menor perfil suficiente.
3. Mantenha fabricantes, fornecedores, unidades e medicamentos.
4. Acompanhe estoque, distribuições, relatórios e auditoria.
5. Não compartilhe contas; inative acessos desligados.

## Farmacêutico

1. Registre aquisições conferindo medicamento, fornecedor, nota, lote, validade, quantidade e valor.
2. Anexe PDF/XML quando houver documento digital.
3. Consulte alertas de validade e estoque mínimo.
4. Registre distribuição; o sistema escolhe os lotes por FEFO.
5. Registre devolução ou ajuste somente com justificativa verdadeira.

## Gestor

1. Use o painel para filtrar período, responsável e unidade.
2. Consulte totais adquiridos e distribuídos.
3. Exporte PDF/Excel com os mesmos filtros da tela.
4. Use ajustes apenas quando formalmente autorizado.

## Auditor

1. Consulte cadastros e movimentos sem permissão de alteração.
2. Em Auditoria, filtre entidade e confira autor, data e valores.
3. Em Rastreabilidade, escolha um medicamento para ligar aquisição, lote, saída, destino e devolução.
4. Exporte relatórios como evidência; preserve o arquivo original.

## Convenções

E = entrada, S = saída, D = devolução, A = ajuste. Lotes vencidos não entram no FEFO. Quando o saldo pedido excede o disponível, nenhuma parte da operação é gravada.
