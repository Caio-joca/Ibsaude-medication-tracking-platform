# Arquitetura

## Visão geral

O navegador envia requisições HTTP ao Flask. Cada blueprint trata um módulo e delega regras de negócio aos serviços. Os serviços alteram entidades SQLAlchemy em transações únicas. O banco registra o estado operacional; a auditoria observa inclusões, alterações e exclusões e grava um histórico separado.

```text
Navegador → rotas/blueprints → services → SQLAlchemy → SQLite/PostgreSQL
                  ↓               ↓
              templates      logs de auditoria
                  ↓
            PDF / Excel / anexos
```

## Decisões

- Application factory (`criar_app`) permite configurações isoladas para desenvolvimento, teste e produção.
- Blueprints evitam concentrar toda a lógica em `app.py`.
- Regras transacionais ficam em `services/`, não nos templates.
- FEFO ordena lotes válidos pela menor validade e divide uma solicitação entre lotes quando necessário.
- Saída, redução do saldo e movimentação são confirmadas ou revertidas juntas.
- Arquivos recebem nome aleatório; extensão e conteúdo são validados.
- Flask-WTF oferece CSRF; Jinja escapa HTML; SQLAlchemy parametriza consultas.
- `ProxyFix`, cookies seguros, CSP, HSTS e cabeçalhos defensivos são ativados para produção.

## Execução

- Desenvolvimento: SQLite e servidor Flask.
- Teste: SQLite em memória, banco recriado por teste.
- Produção: PostgreSQL, Gunicorn atrás de proxy HTTPS e diretório persistente para anexos/backups.
