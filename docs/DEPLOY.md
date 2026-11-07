# Deploy e operação

Este documento descreve o processo de publicação do MVP mono-administrador. A escolha do provedor, o domínio e as credenciais externas não fazem parte do repositório.

## 1. Requisitos

- Domínio curto e certificado HTTPS.
- Uma instância da aplicação para o MVP.
- PostgreSQL gerenciado ou persistente; SQLite também funciona em baixo volume se estiver em disco persistente.
- Backups automáticos e um local externo para armazená-los.
- Proxy reverso ou plataforma que encerre HTTPS e encaminhe requisições ao Uvicorn.

A URL pública gravada nas tags deve seguir o formato:

```text
https://api.seudominio.com.br/r/abc123
```

O formato antigo `/{slug}` continua disponível para tags já gravadas.

## 2. Variáveis de produção

```dotenv
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://usuario:senha_codificada@host:5432/smart_tag_hub
SECRET_KEY=
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=''
ALLOWED_HOSTS=api.seudominio.com.br
SESSION_SECURE_COOKIE=true
```

Gere os valores localmente:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
python -m scripts.generate_password_hash
```

Não envie `.env` para o Git nem para a imagem Docker. Cadastre essas variáveis no cofre de segredos do provedor. Se a senha do banco tiver caracteres especiais, use sua forma codificada para URL na `DATABASE_URL`.

`DATABASE_URL` é obrigatória em produção. Para SQLite, use um caminho absoluto em um volume persistente, como `sqlite+aiosqlite:////app/data/smart_tag_hub.db`; caminhos relativos e bancos em memória são recusados na inicialização.

Em produção a aplicação valida as configurações essenciais e desabilita `/docs` e `/openapi.json`. O health check permanece em `/_health`.

## 3. Docker

Construir e executar:

```bash
docker build -t smart-tag-hub .
docker run --rm --env-file .env -p 8000:8000 smart-tag-hub
```

A imagem usa Python 3.12, dependências fixadas, usuário não root e health check. Ela não contém banco SQLite, `.env`, testes ou backups. Para SQLite, monte um volume em `/app/data`. O health check envia o primeiro host de `ALLOWED_HOSTS`, evitando bloqueio pelo `TrustedHostMiddleware`.

Se o proxy estiver em outro host/container, configure `FORWARDED_ALLOW_IPS` somente com os IPs confiáveis desse proxy. Não use encaminhamento de headers de origem desconhecida.

## 4. Migrações

Faça backup e execute as migrações antes de publicar uma versão que altere o schema:

```bash
alembic upgrade head
```

Com a imagem Docker:

```bash
docker run --rm --env-file .env smart-tag-hub alembic upgrade head
```

Para uma base antiga que já tinha `links` antes do Alembic, valide o schema, faça backup e execute uma única vez:

```bash
alembic stamp 0001
alembic upgrade head
```

Não execute `stamp` em um banco novo ou em uma base já controlada pelo Alembic.

## 5. Backups

### PostgreSQL

Prefira snapshots e backups automáticos do provedor. Para um backup lógico manual:

```bash
pg_dump "$DATABASE_URL_SYNC" --format=custom --file=smart_tag_hub.dump
```

Use uma variável separada com a URL no formato aceito pelo `pg_dump` (`postgresql://`, sem `+asyncpg`). Teste a restauração em um banco separado com `pg_restore`; um backup nunca testado não garante recuperação.

### SQLite

Use um volume persistente e o mecanismo de backup online do SQLite, em vez de copiar o arquivo durante escritas. A recuperação deve preservar o arquivo no caminho definido por `DATABASE_URL`.

## 6. Publicação

1. Executar `ruff check .`, `ruff format --check .`, `pip-audit` e `pytest -q`.
2. Construir a imagem e testar a configuração em homologação.
3. Confirmar que o backup atual foi concluído.
4. Aplicar `alembic upgrade head`.
5. Publicar a aplicação com `ENVIRONMENT=production`.
6. Verificar `/_health` e o certificado HTTPS.
7. Entrar em `/admin`, criar um link de teste e copiar sua URL curta.
8. Confirmar o redirecionamento `307` e editar o destino.
9. Ler a mesma tag NFC novamente, sem regravá-la, e confirmar o novo destino.
10. Testar link desativado, slug inexistente, logout e acesso anônimo à API.
11. Monitorar logs e remover o link de teste ou desativá-lo.

Para rollback, restaure a versão anterior compatível com o schema. Se a migração não for reversível de forma segura, preserve o schema e faça rollback apenas do código; restauração do banco deve considerar dados criados depois do backup.

## 7. Operação contínua

- Configure alerta externo para indisponibilidade de `/_health`.
- Acompanhe erros do Uvicorn e da plataforma.
- Teste restaurações periodicamente.
- Mantenha dependências atualizadas após executar a suíte de testes.
- Use uma instância no MVP: o limite de login em memória é por processo.
- Antes de escalar horizontalmente, use um limitador compartilhado e revise a estratégia de sessões e banco.

## 8. Fora do escopo deste deploy

Analytics, cadastro de clientes, múltiplos administradores, cobrança e gerenciamento multiusuário não são necessários para este primeiro lançamento.
