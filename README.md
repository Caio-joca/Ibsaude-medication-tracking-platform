# IBSAÚDE

Sistema web para controle e rastreabilidade de medicamentos, da aquisição à distribuição. Desenvolvido em Flask, com estoque por lote, FEFO, devoluções, auditoria imutável, relatórios e acesso por perfil.

## Funcionalidades

- autenticação com senha em hash e sessões protegidas;
- perfis Administrador, Farmacêutico, Gestor e Auditor;
- usuários, fabricantes, fornecedores, unidades e medicamentos;
- aquisições com nota, lote, validade, valores e anexos PDF/XML;
- saldo por lote, estoque mínimo e alertas de validade;
- distribuição automática pelo lote que vence primeiro (FEFO);
- bloqueio de lote vencido e de estoque negativo;
- devoluções e ajustes com justificativa e histórico;
- rastreabilidade completa e log de auditoria imutável;
- painel gerencial filtrável e relatórios PDF/Excel.

## Instalação no Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m flask --app app db upgrade
python -m flask --app app criar-admin
python app.py
```

Acesse `http://127.0.0.1:5000`. No arquivo `.env`, use uma `SECRET_KEY` longa e aleatória. O administrador inicial deve ser criado pelo comando acima; nenhuma senha padrão fica no repositório.

Para carregar uma base fictícia de demonstração (bloqueada em produção), execute:

```powershell
python -m flask --app app carregar-demo
```

O comando cria os quatro perfis, cadastros, medicamentos, lotes, aquisições, distribuições, devolução, ajuste e documentos XML. Ele pode ser executado novamente sem duplicar os registros identificados como demonstração.

## Testes

```powershell
python -m pytest -q
python -m pytest --cov=. --cov-report=term-missing
```

## Backup

```powershell
python scripts/backup.py
python scripts/verificar_backup.py backups\NOME_DO_BACKUP.sqlite3
```

A restauração exige confirmação explícita e preserva uma cópia do banco atual:

```powershell
python scripts/restaurar_sqlite.py backups\NOME_DO_BACKUP.sqlite3 --confirmar
```

## Produção

O arquivo `render.yaml` descreve serviço web, PostgreSQL e armazenamento persistente. Configure `FLASK_ENV=production`, `DATABASE_URL`, `SECRET_KEY`, `UPLOAD_FOLDER` e `BACKUP_FOLDER`. O servidor usa `gunicorn wsgi:app`, aplica migrations antes de iniciar e respeita HTTPS encaminhado pelo proxy.

## Estrutura

- `app.py`: fábrica Flask, extensões, blueprints, comandos e cabeçalhos de segurança;
- `models.py`: entidades e integridade do domínio;
- `routes/`: controladores HTTP agrupados por módulo;
- `services/`: regras transacionais de aquisição, estoque, distribuição e auditoria;
- `utils/`: validação, autorização e anexos;
- `templates/` e `static/`: interface web;
- `migrations/`: evolução versionada do banco;
- `tests/`: testes automatizados;
- `scripts/`: migração PostgreSQL, backup, verificação e restauração;
- `docs/`: arquitetura, operação, segurança, API, manuais e validação.

Veja [docs/ARQUITETURA.md](docs/ARQUITETURA.md), [docs/MANUAL_USUARIOS.md](docs/MANUAL_USUARIOS.md) e [docs/STATUS_ENTREGA.md](docs/STATUS_ENTREGA.md).
