# Deploy de produção

## Preparação existente

`render.yaml` provisiona aplicação Python, PostgreSQL e disco persistente. O build instala dependências, o pre-deploy aplica Alembic e o processo web inicia Gunicorn. O provedor termina TLS; `ProxyFix` faz o Flask reconhecer HTTPS.

## Procedimento

1. Criar conta/projeto no provedor e conectar o repositório.
2. Revisar região, plano, domínio e custo.
3. Aplicar o blueprint `render.yaml`.
4. Confirmar `SECRET_KEY`, `DATABASE_URL`, `UPLOAD_FOLDER` e `BACKUP_FOLDER`.
5. Criar o administrador com shell seguro: `flask --app app criar-admin`.
6. Conferir `/login`, cabeçalhos HTTPS, anexos e migrations.
7. Executar o roteiro de homologação de `CHECKLIST_VALIDACAO.md`.
8. Programar backup PostgreSQL e cópia externa dos anexos.

## Migração de dados SQLite

Depois de migrar o schema no PostgreSQL e fazer backup dos dois lados, defina `POSTGRES_DATABASE_URL` e execute `python scripts/migrar_para_postgresql.py`. Valide contagens e amostras antes de trocar o `DATABASE_URL`.

Publicação, domínio e credenciais dependem da autorização do proprietário da infraestrutura e não podem ser executados automaticamente sem essa conta.
