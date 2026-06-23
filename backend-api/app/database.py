import os

from dotenv import load_dotenv

import asyncpg

load_dotenv()

DATABASE_URL = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT')}/{os.getenv('POSTGRES_DB')}"
)

pool = None

async def create_pool():
    global pool
    try:
        pool = await asyncpg.create_pool(
            DATABASE_URL, min_size=1, max_size=5, timeout=10, command_timeout=5
        )
        print('Pool de conexões criado')
    except Exception as e:
        print(f"Erro ao criar pool de conexões: {e}")
        raise

async def close_pool():
    global pool
    if pool:
        await pool.close()
        print("Pool de conexões fechado")

async def get_connection():
    if pool is None:
        raise RuntimeError("Pool de conexões não foi inicializado")
    return await pool.acquire()

async def release_connection(conn):
    await pool.release(conn)