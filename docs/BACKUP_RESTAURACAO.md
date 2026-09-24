# Backup e restauração

## SQLite

`python scripts/backup.py` usa a API de backup do SQLite, permitindo cópia consistente. Depois, execute `python scripts/verificar_backup.py CAMINHO` e guarde uma cópia fora do computador.

Para restaurar, pare a aplicação e use `scripts/restaurar_sqlite.py ... --confirmar`. O script verifica o backup e copia o banco atual antes de substituí-lo.

## PostgreSQL

Com `FLASK_ENV=production`, `scripts/backup.py` chama `pg_dump` em formato custom. `verificar_backup.py` usa `pg_restore --list`. A restauração deve ocorrer primeiro em banco vazio de homologação, seguida de migrations, contagens e teste funcional.

## Política sugerida

- backup diário; retenção de 7 diários, 4 semanais e 6 mensais;
- cópia criptografada em local físico/provedor diferente;
- acesso restrito ao administrador de infraestrutura;
- teste de restauração trimestral com registro de data, responsável, duração e resultado;
- anexos e banco incluídos no mesmo plano de continuidade.

Um backup não verificado não deve ser considerado recuperável.
