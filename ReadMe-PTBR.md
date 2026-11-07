# Smart Tag Hub

Backend e painel administrativo para centralizar URLs usadas em tags NFC. Grave uma URL curta na tag uma única vez e altere o destino pelo painel sempre que precisar.

*Read this in English: [README.md](README.md)*

## O que já está implementado

- Criação de links com slug aleatório ou personalizado.
- Listagem e busca por slug ou URL.
- Edição da URL de destino.
- Ativação e desativação sem apagar o histórico.
- Redirecionamento público temporário (`307`) em `/r/{slug}`.
- Compatibilidade com os links antigos no formato `/{slug}`.
- Página pública para links inexistentes ou desativados.
- Painel administrativo responsivo servido pelo próprio FastAPI.
- Acesso administrativo único com senha Argon2, sessão assinada, CSRF e limite de tentativas de login.
- API administrativa protegida pela mesma sessão.
- SQLite para desenvolvimento e suporte a PostgreSQL em produção.
- Migrações Alembic, health check, Dockerfile e CI com testes e Ruff.

O escopo atual é intencionalmente **mono-administrador**. Cadastro de clientes, permissões por usuário e analytics ficam para uma evolução posterior.

## Tecnologias

- Python 3.11+
- FastAPI, Starlette e Jinja2
- SQLAlchemy assíncrono
- SQLite/aiosqlite e PostgreSQL/asyncpg
- Alembic
- Pytest, HTTPX e Ruff
- Uvicorn e Docker

## Arquitetura

| Camada | Responsabilidade |
| --- | --- |
| `api/` | Rotas públicas, API, painel, autenticação, templates e configurações. |
| `domain/` | Entidade, regras de negócio, validações e contrato do repositório. |
| `infrastructure/` | Banco de dados, modelo ORM e repositório SQLAlchemy. |
| `migrations/` | Evolução versionada do schema com Alembic. |
| `tests/` | Testes unitários e de integração com SQLite em memória. |
| `docs/` | Documentação operacional e fluxogramas conceituais. |

O domínio não depende do banco de dados. A API e o painel utilizam o mesmo `LinkService`, evitando duplicação das regras.

## Executar localmente

### 1. Instalar

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements-dev.txt
```

### 2. Configurar o administrador

Copie `.env.example` para `.env`. Gere uma chave de sessão:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Use o resultado em `SECRET_KEY`. Depois gere o hash da senha, sem salvar a senha em texto puro:

```bash
python -m scripts.generate_password_hash
```

Copie o hash exibido para `ADMIN_PASSWORD_HASH` no `.env`, mantendo-o entre aspas simples.

### 3. Preparar o banco e iniciar

```bash
alembic upgrade head
pytest
uvicorn api.main:app --reload
```

Acesse:

- Painel: `http://localhost:8000/admin`
- Documentação da API em desenvolvimento: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/_health`
- URL para gravar na tag: `http://localhost:8000/r/{slug}`

Em produção, use o domínio HTTPS definitivo na URL gravada na tag.

### Bancos criados antes do Alembic

Uma base antiga que já possui a tabela `links`, mas não possui `alembic_version`, precisa ser marcada na migração inicial antes da atualização:

```bash
alembic stamp 0001
alembic upgrade head
```

Faça backup antes desse procedimento. Bancos novos precisam apenas de `alembic upgrade head`.

## API administrativa

Todas essas rotas exigem uma sessão obtida pelo login do painel. O `POST /links` original continua disponível como alias para criação; os demais endpoints administrativos ficam em `/api/links`:

| Método | Rota | Função |
| --- | --- | --- |
| `GET` | `/api/links?q=` | Listar e filtrar links. |
| `POST` | `/api/links` | Criar link. |
| `GET` | `/api/links/{slug}` | Consultar link. |
| `PATCH` | `/api/links/{slug}` | Alterar `target_url` e/ou `is_active`. |

Exemplo de atualização:

```json
{
  "target_url": "https://exemplo.com/novo-destino",
  "is_active": true
}
```

## Qualidade

```bash
pytest -q
ruff check .
ruff format --check .
pip-audit
```

O workflow em `.github/workflows/ci.yml` executa essas verificações com Python 3.12 em pushes na `main` e Pull Requests.

## Deploy

Consulte [docs/DEPLOY.md](docs/DEPLOY.md) para variáveis de produção, PostgreSQL, migrações, HTTPS, backups e checklist de publicação. Nenhum provedor é obrigatório: o Dockerfile permite executar em VPS ou serviços compatíveis com contêineres.

## Próximas evoluções

- Registro de acessos e analytics.
- Exportação de links pelo painel.
- Contas de clientes e propriedade individual das tags.
- Mais opções de administração e observabilidade.

## Autor

Renan Barbosa — [GitHub](https://github.com/renanbarbosaaa)
