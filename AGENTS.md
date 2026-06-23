# AGENTS.md — SpyPrice

## Regras

- NUNCA criar/editar/deletar arquivos sem perguntar antes.
- Antes de commitar: `python scripts/notion.py list` + `python scripts/notion.py read <id>`; verificar se codigo condiz com documentacao.
- Apos alteracao significativa, atualizar este arquivo.

## Projeto

Monitor de precos em marketplaces. Projeto em estagio inicial.

## Estrutura (committado)

- `db/init.sql` — schema PostgreSQL
- `docker-compose.yml` — orquestracao dos containers
- `.gitignore` — regras de ignorar arquivos

## .gitignore

`AGENTS.md`, `scripts/`, `docs/` na secao "Tests" — novos arquivos ai nao sao trackeados sem `git add -f`. Tambem ignora `.env`, `.venv/`, `__pycache__/`, `*.pyc`, `postgres_data/`.

## Comandos essenciais

```powershell
docker compose up -d                             # postgres:5432, pgadmin:8080
docker compose down -v                           # derruba + apaga volumes
docker compose logs postgres-db                  # logs do postgres
docker compose logs pgadmin                      # logs do pgadmin
python scripts/notion.py list
python scripts/notion.py read <page_id>
python scripts/notion.py read-all
```

## Docker

- Volume do PostgreSQL montado em `/var/lib/postgresql` (sem `/data`). PostgreSQL 18+ cria subdiretorio com a versao maior. Nao "corrigir" para `/data`.
- Healthcheck no `postgres-db` usando `pg_isready`.
- Portas `5432` e `8080` vinculadas apenas ao `127.0.0.1`.

## Banco

3 tabelas: `products` (id UUID, name), `marketplace_links` (id UUID, product_id FK UUID, marketplace, url), `price_history` (id UUID, link_id FK UUID, price, is_available, captured_at). Todos os IDs usam `gen_random_uuid()`. Schema via `db/init.sql` montado em `/docker-entrypoint-initdb.d/` — executa apenas na primeira criacao do volume.

## Notion

Pagina raiz: "Projeto SpyPrice" (`3842fa6bd5c0806f8974f3953edca0c9`). Subpaginas: Infraestrutura, Banco de Dados, Front-end, Back-end, Diario de desenvolvimento.

## Nao implementado (ainda)

Testes, lint, typecheck, CI, Pydantic schemas, routers separados, autenticacao, frontend, scraper, backend-api.

## Nao committado

- `backend-api/` — codigo da API (FastAPI), sera adicionado em commit futuro
- `docs/` — anotacoes pessoais e guias internos
- `scripts/` — utilitarios locais
