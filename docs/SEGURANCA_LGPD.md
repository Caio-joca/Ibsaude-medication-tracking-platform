# Segurança e LGPD

## Controles implementados

- senhas com hash Werkzeug, nunca recuperáveis em texto;
- autorização no servidor por perfil, independentemente do menu exibido;
- CSRF em operações mutáveis;
- queries parametrizadas pelo ORM e escape HTML automático;
- upload limitado a 10 MB, PDF/XML, assinatura PDF e XML sem DTD/entidades;
- cookies `HttpOnly`, `SameSite=Lax` e `Secure` em produção;
- CSP, HSTS, `X-Frame-Options`, `nosniff`, política de referência e `no-store`;
- segredos e URLs fora do repositório, via variáveis de ambiente;
- log de alterações com conteúdo de senha protegido;
- inativação em vez de exclusão de registros com histórico.

## Aplicação dos princípios LGPD

- Finalidade: dados pessoais são usados apenas para identificar responsáveis e controlar acesso.
- Necessidade: o sistema armazena nome, CPF e e-mail; não coleta dados clínicos de pacientes.
- Acesso: cada perfil recebe somente as operações necessárias.
- Segurança: controles técnicos acima, backup verificado e HTTPS em produção.
- Prestação de contas: auditoria e rastreabilidade documentam ações.

## Responsabilidades institucionais antes de produção

1. Definir controlador, operador, encarregado e base legal.
2. Aprovar prazos de retenção e descarte para usuários, documentos e logs.
3. Publicar aviso de privacidade e canal do titular.
4. Formalizar resposta a incidente e restauração de backup.
5. Executar avaliação jurídica e farmacêutica documentada.

Nenhum documento deste repositório equivale a parecer jurídico ou regulatório.
