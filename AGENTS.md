# AGENTS.md — SpyPrice

## Regras

- NUNCA criar/editar/deletar arquivos sem perguntar antes.
- Apos alteracao significativa, atualizar este arquivo.
- Ao preparar commit, mostrar mensagem completa ao usuario para validacao antes de executar.

## Projeto

Monitor de precos em marketplaces. CRUD completo de produtos implementado.

## Estrutura

- `backend-api/app/main.py` — FastAPI (CRUD completo: GET+POST+PUT+DELETE /produtos, GET /produtos/{id}). POST recebe JSON body (`ProductCreate`), paginacao com `limit`/`offset`.
- `backend-api/app/schemas.py` — Pydantic v2: ProductCreate, ProductUpdate, ProductResponse (Field, min_length=2)
- `backend-api/app/database.py` — asyncpg pool (min=1, max=5, timeout=10, command_timeout=5), `load_dotenv()` no modulo
- `backend-api/requirements.txt` — fastapi, uvicorn[standard], asyncpg, python-dotenv (pinned com `==`)
- `backend-api/Dockerfile` — python:3.13-slim, CMD sem `--reload`
- `backend-api/.dockerignore` — exclui `.venv/`, `.env`, `__pycache__/`
- `backend-scraper/` — vazio
- `frontend/` — vazio
- `db/init.sql` — schema PostgreSQL (3 tabelas)
- `scripts/notion.py` — CLI Notion, timeout=15s
- `.prettierrc` — prettier config

## .gitignore

`.venv/`, `__pycache__/`, `*.pyc`, `.env`, `postgres_data/`, `scripts/`, `docs/` nao sao trackeados.

## Comandos essenciais

```powershell
.venv\Scripts\Activate.ps1
docker compose up -d                    # postgres:5432, pgadmin:8080, api:8000
docker compose up -d --build            # reconstroi imagem da api
docker compose down -v                  # derruba + apaga volumes
docker compose logs backend-api         # logs do container api
python scripts/notion.py list
python scripts/notion.py read <page_id>
```

## Docker

- `DB_HOST` definido no compose (`postgres-db`); fallback para `localhost` fora do container.
- Volume PostgreSQL montado em `/var/lib/postgresql` (sem `/data`).
- Healthcheck no `postgres-db`; API espera `service_healthy`.
- Portas `5432` e `8080` vinculadas apenas ao `127.0.0.1`.
- Compose passa apenas envs necessarias (sem injetar `.env` inteiro).
- Bind mount `./backend-api/app:/app/app` + `WATCHFILES_FORCE_POLLING=true` para hot-reload no Windows.

## Banco

3 tabelas: `products` (id UUID, name), `marketplace_links` (id UUID, product_id FK UUID, marketplace, url), `price_history` (id UUID, link_id FK UUID, price, is_available, captured_at). Schema via `db/init.sql` montado em `/docker-entrypoint-initdb.d/`.

## Commits

Seguir `docs/commit-guide.md`. Tipo `docs:` não usa escopo.
