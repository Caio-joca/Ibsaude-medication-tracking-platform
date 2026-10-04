# Relatório de testes

A suíte automatizada cobre autenticação, proteção de páginas, aquisição transacional, duplicidade estrutural, FEFO, divisão entre lotes, saldo insuficiente, lote vencido, devolução, ajuste, auditoria imutável, perfis, XSS, consulta hostil, cabeçalhos, CSRF, upload seguro e exportações PDF/Excel.

Comando oficial: `python -m pytest -q --cov=. --cov-report=term`.

Além da automação, a homologação deve seguir `CHECKLIST_VALIDACAO.md` em ambiente PostgreSQL/HTTPS. O percentual de cobertura é um indicador técnico e não substitui validação institucional.
