import os
import sys
import asyncpg
import pytest_asyncio
from pathlib import Path
from dotenv import load_dotenv
from httpx import AsyncClient, ASGITransport

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

load_dotenv()

TEST_DB = "spyprice_db_test"
BASE_DB = os.getenv("POSTGRES_DB")


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def db_pool():
    dsn = (
        f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
        f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT')}/{BASE_DB}"
    )
    conn = await asyncpg.connect(dsn)
    exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", TEST_DB)
    if not exists:
        await conn.execute(f'CREATE DATABASE "{TEST_DB}"')
    await conn.close()

    test_dsn = (
        f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
        f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT')}/{TEST_DB}"
    )
    pool = await asyncpg.create_pool(test_dsn, min_size=1, max_size=2)

    schema = Path(__file__).resolve().parent.parent.parent / "db" / "init.sql"
    async with pool.acquire() as conn:
        await conn.execute(schema.read_text())

    yield pool

    await pool.close()
    conn = await asyncpg.connect(dsn)
    await conn.execute(f'DROP DATABASE IF EXISTS "{TEST_DB}" WITH (FORCE)')
    await conn.close()


@pytest_asyncio.fixture(autouse=True, loop_scope="session")
async def clean_db(db_pool):
    async with db_pool.acquire() as conn:
        await conn.execute("DELETE FROM price_history")
        await conn.execute("DELETE FROM marketplace_link")
        await conn.execute("DELETE FROM product")
    yield


@pytest_asyncio.fixture(loop_scope="session")
async def client(db_pool):
    import app.database

    app.database.pool = db_pool

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
