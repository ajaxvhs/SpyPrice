from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_pool, close_pool, get_connection, release_connection
from app.schemas import ProductCreate, ProductUpdate, ProductResponse


app = FastAPI(title="SpyPrice API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await create_pool()


@app.on_event("shutdown")
async def shutdown():
    await close_pool()


@app.get("/produtos", summary='List all product')
async def list_product(
    limit: int = Query(default=50, ge=1, le=50),
    offset: int = Query(default=0, ge=0)
):
    conn = await get_connection()
    try:
        rows = await conn.fetch(
            "SELECT id, name FROM product ORDER BY created_at DESC LIMIT $1 OFFSET $2",
            limit, offset
        )
        return [dict(r) for r in rows]
    finally:
        await release_connection(conn)


@app.get("/produtos/{product_id}", summary='Get product by ID')
async def get_product(product_id: str):
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            "SELECT id, name FROM product WHERE id = $1", product_id
        )
        if not row:
            raise HTTPException(status_code=404, detail='Product not found')
        return dict(row)
    finally:
        await release_connection(conn)

@app.put("/produtos/{product_id}", summary='Update product by ID')
async def update_product(product_id: str, payload: ProductUpdate):
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            "SELECT id, name FROM product WHERE id = $1", product_id
        )
        if not row:
            raise HTTPException(status_code=404, detail='Product not found')
        return {'id': product_id, 'name': payload.name}
    finally:
        await release_connection(conn)

@app.post("/produtos", summary='Create product', status_code=201)
async def create_product(payload: ProductCreate):
    conn = await get_connection()
    try:
        product_id = await conn.fetchval(
            "INSERT INTO product (name) VALUES ($1) RETURNING id", payload.name
        )
        return {"id": str(product_id), "name": payload.name}
    finally:
        await release_connection(conn)

@app.delete("/produtos/{product_id}", summary='Delete product by ID', status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str):
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            "SELECT id, name FROM product WHERE id = $1", product_id
        )
        if not row:
            raise HTTPException(status_code=404, detail='Product not found')
        await conn.execute("DELETE FROM product WHERE id = $1", product_id)
    finally:
        await release_connection(conn)