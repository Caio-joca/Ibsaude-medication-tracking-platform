# Plataforma de Controle de Medicamentos — IBSAÚDE

Projeto integrador desenvolvido durante a residência tecnológica do Programa Futuro Digital.

## Objetivo

Desenvolver uma plataforma digital para controle e rastreabilidade de medicamentos, acompanhando o processo desde a aquisição até a distribuição para as unidades de saúde.

## Funcionalidades desenvolvidas

- Cadastro de usuários
- Listagem e pesquisa de usuários
- Edição de usuários
- Exclusão de usuários
- Perfis de acesso:
  - Administrador
  - Farmacêutico
  - Gestor
  - Auditor

## Tecnologias utilizadas

- Python
- Flask
- SQLite
- HTML
- Bootstrap

## Como executar o projeto

### 1. Criar o ambiente virtual

```powershell
python -m venv .venv
```

### 2. Ativar o ambiente virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar as dependências

```powershell
python -m pip install -r requirements.txt
```

### 4. Inicializar o banco de dados

```powershell
python init_db.py
```

### 5. Executar o sistema

```powershell
python cadusuario.py
```

Depois, acesse:

http://127.0.0.1:5000

## Situação atual

O módulo inicial de usuários está em desenvolvimento. Os próximos módulos incluirão autenticação, medicamentos, fornecedores, aquisições, estoque, distribuição, auditoria e relatórios.