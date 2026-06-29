# AGENTS.md — SpyPrice

Monitor de precos em marketplaces.

## Rules

- Ask before creating/editing/deleting any file.
- Show full commit message for user validation before executing.
- Critically analyze each request: identify problems, ambiguities, and risks before acting. Do not follow instructions blindly.
- Implement the simplest thing that works. Do not add abstractions not explicitly requested.

## Quick start

```powershell
.venv\Scripts\Activate.ps1
docker compose up -d                    # postgres:5432, pgadmin:8080, api:8000
docker compose up -d --build            # rebuild api image
docker compose down -v                  # teardown + delete volumes
docker compose logs backend-api         # api container logs
python local/scripts/notion.py list
python local/scripts/notion.py read <page_id>
python local/scripts/notion.py append <page_id> <arquivo.md> --dry-run
python local/scripts/notion.py append-text <page_id> 'texto' --dry-run
python local/scripts/notion.py update-text <page_id> "old" "new" --dry-run
python local/scripts/notion.py create-page <parent_page_id> "Titulo" --dry-run
```

Notion script: `local/scripts/notion.py`. See `local/docs/notion.md` for full reference.

## API (`backend-api/app/main.py`)

FastAPI with asyncpg. CORS allows only `http://localhost:5173`. Port 8000.

| Endpoint | Method | Notes |
|---|---|---|
| `/produtos` | GET | Pagination: `limit` (max 50), `offset` |
| `/produtos` | POST | JSON `ProductCreate` body |
| `/produtos/{id}` | GET/PUT/DELETE | `ProductUpdate` on PUT |
| `/produtos/{id}/links` | GET/POST | 409 on duplicate URL |
| `/links/{id}` | PUT/DELETE | |
| `/links/{id}/precos` | GET/POST | |

DB pool: `min_size=1, max_size=5, timeout=10, command_timeout=5`. Retries 5x with 3s sleep on startup.

## Database (`db/init.sql`)

3 tables — `product`, `marketplace_link`, `price_history`. UUID PKs, `ON DELETE CASCADE`. Schema mounted at `/docker-entrypoint-initdb.d/`.

## Docker quirks

- `DB_HOST=postgres-db` inside compose; fallback `localhost` outside.
- API waits for `service_healthy` on postgres (pg_isready healthcheck).
- Ports 5432 and 8080 bound to `127.0.0.1` only.
- Bind mount `./backend-api/app:/app/app` + `WATCHFILES_FORCE_POLLING=true` for hot-reload on Windows.
- Compose injects only required env vars (no `.env` dump).

## Commits

Conventional Commits (`feat`, `fix`, `refactor`, `docs`, `chore`, `style`, `perf`, `test`). Scopes: `api`, `db`, `infra`, `scraper`, `frontend`, `notion`. Messages in English, imperative mood. See `docs/commit-guide.md`.

## State

- `backend-scraper/`, `frontend/` — empty.
- Test suite: 31 tests passing (pytest, pytest-asyncio, httpx). See `backend-api/tests/`.
- Lifespan pattern replaces deprecated `@app.on_event("startup"/"shutdown")`.
- `.env` is gitignored; copy `.env.example` to get started.
