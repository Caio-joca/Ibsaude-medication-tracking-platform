# Rotas HTTP

O MVP fornece interface web renderizada no servidor. Não há API pública autenticada por token; as rotas abaixo usam sessão e CSRF.

| Módulo | Método e rota | Perfis | Finalidade |
|---|---|---|---|
| Autenticação | `GET/POST /login` | público | Entrar |
| Autenticação | `POST /logout` | autenticado | Encerrar sessão |
| Painel | `GET /painel` | todos | Indicadores e filtros |
| Usuários | `GET/POST /usuarios/...` | A | Listar, criar, editar e inativar |
| Cadastros | `GET/POST /fabricantes/...` | A/F/G | Fabricantes |
| Cadastros | `GET/POST /fornecedores/...` | A/F/G | Fornecedores |
| Cadastros | `GET/POST /unidades/...` | A/F/G | Unidades |
| Medicamentos | `GET /medicamentos` | A/F/G/U | Consulta |
| Medicamentos | `GET/POST /medicamentos/novo` | A/F/G | Inclusão |
| Medicamentos | `GET/POST /medicamentos/editar/<id>` | A/F/G | Alteração |
| Aquisições | `GET /aquisicoes` | A/F/G/U | Histórico |
| Aquisições | `GET/POST /aquisicoes/nova` | A/F/G | Entrada e estoque |
| Estoque | `GET /estoque` | A/F/G/U | Saldos e alertas |
| Estoque | `GET /estoque/movimentacoes` | A/F/G/U | Razão de estoque |
| Estoque | `GET/POST /estoque/ajustar/<id>` | A/F/G | Ajuste justificado |
| Distribuições | `GET /distribuicoes` | A/F/G/U | Histórico por unidade |
| Distribuições | `GET/POST /distribuicoes/nova` | A/F/G | Saída FEFO |
| Distribuições | `POST /distribuicoes/<id>/devolver` | A/F/G | Devolução |
| Auditoria | `GET /auditoria` | A/U | Logs |
| Auditoria | `GET /auditoria/rastreabilidade` | A/U | Cadeia completa |
| Relatórios | `GET /relatorios` | A/G/U | Consulta filtrada |
| Relatórios | `GET /relatorios/movimentacoes.pdf` | A/G/U | Exportação PDF |
| Relatórios | `GET /relatorios/movimentacoes.xlsx` | A/G/U | Exportação Excel |

Legenda: A Administrador, F Farmacêutico, G Gestor, U Auditor.
