# 📝 Guia de Commits — SpyPrice

Este guia define o padrão de mensagens de commit para manter o histórico do Git limpo, legível e organizado. Adotamos o padrão **Conventional Commits**.

---

## 🏗️ Estrutura do Commit

Toda mensagem de commit deve seguir a seguinte estrutura:

```text
<tipo>(<escopo>): <descrição curta em letras minúsculas>

[Corpo/descrição opcional: Detalhes adicionais sobre o que foi feito]

- <arquivo>: o que foi alterado
- <arquivo>: o que foi alterado
```

## 📋 Tipos Permitidos

| Tipo       | Quando usar                                        |
| ---------- | -------------------------------------------------- |
| `feat`     | Nova funcionalidade                                |
| `fix`      | Correção de bug                                    |
| `refactor` | Mudança na estrutura sem alterar comportamento     |
| `docs`     | Documentação (Notion, AGENTS.md, README)           |
| `chore`    | Tarefas internas (gitignore, dockerignore, config) |
| `style`    | Formatação, espaçamento, lint (sem mudar lógica)   |
| `perf`     | Melhoria de performance                            |
| `test`     | Adicionar ou corrigir testes                       |

## 🎯 Escopos do Projeto

| Escopo     | O que inclui                                                    |
| ---------- | --------------------------------------------------------------- |
| `api`      | backend-api/app/ (rotas, database, schemas)                     |
| `db`       | db/init.sql, schema, migrations                                 |
| `infra`    | docker-compose.yml, Dockerfile, .dockerignore, .env, .gitignore |
| `scraper`  | backend-scraper/                                                |
| `frontend` | frontend/                                                       |
| `notion`   | scripts/notion.py                                               |
| `docs`     | Arquivos em docs/ ou AGENTS.md                                  |

## ✅ Exemplos Reais

```text
feat(api): add get and post /produtos endpoints

- backend-api/app/main.py: add GET /produtos and POST /produtos routes
- POST uses query param (?nome=foo), not JSON body
```

```text
fix(db): change fk columns from integer to uuid

- db/init.sql: product_id and link_id now match uuid primary keys
```

```text
chore(infra): add healthcheck and bind ports to localhost

- docker-compose.yml: add pg_isready healthcheck to postgres-db
- docker-compose.yml: bind pgadmin and postgres ports to 127.0.0.1 only
- backend-api/docker-compose.yml: api depends_on service_healthy
```

```text
docs(notion): update infra page with current compose config

- scripts/notion.py: add 15s timeout to http calls
- .env.example: create with placeholder values
```

## ⚠️ Regras

- Mensagens **sempre em inglês**
- Usar **sempre** `tipo(escopo): descrição` (espaço depois dos dois pontos)
- Descrição em **minúsculas**, sem ponto final
- Imperativo: "add" não "added", "fix" não "fixed"
- Escopo opcional, mas preferível quando relevante
- Commits atômicos: um commit = uma mudança lógica
- O agente deve preparar a mensagem de commit e enviar para o usuário validar antes de executar o commit
