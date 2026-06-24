from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
from app.database import create_pool, close_pool, get_connection, release_connection
from app.schemas import ProductCreate, ProductUpdate, ProductResponse, MarketplaceLinkCreate, MarketplaceLinkResponse


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


@app.get("/produtos", summary='List all products', response_model=list[ProductResponse])
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
        return [ProductResponse(id=str(r["id"]), name=r["name"]) for r in rows]
    finally:
        await release_connection(conn)


@app.get("/produtos/{product_id}", summary='Get product by ID', response_model=ProductResponse)
async def get_product(product_id: str):
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            "SELECT id, name FROM product WHERE id = $1", product_id
        )
        if not row:
            raise HTTPException(status_code=404, detail='Product not found')
        return ProductResponse(id=str(row["id"]), name=row["name"])
    finally:
        await release_connection(conn)

@app.put("/produtos/{product_id}", summary='Update product by ID', response_model=ProductResponse)
async def update_product(product_id: str, payload: ProductUpdate):
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            "SELECT id, name FROM product WHERE id = $1", product_id
        )
        if not row:
            raise HTTPException(status_code=404, detail='Product not found')
        await conn.execute("UPDATE product SET name = $1 WHERE id = $2", payload.name, product_id)
        return ProductResponse(id=product_id, name=payload.name)
    finally:
        await release_connection(conn)

@app.post("/produtos", summary='Create product', status_code=201, response_model=ProductResponse)
async def create_product(payload: ProductCreate):
    conn = await get_connection()
    try:
        product_id = await conn.fetchval(
            "INSERT INTO product (name) VALUES ($1) RETURNING id", payload.name
        )
        return ProductResponse(id=str(product_id), name=payload.name)
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

@app.get("/produtos/{product_id}/links", summary='List links from product', response_model=list[MarketplaceLinkResponse])
async def list_links(product_id: str):
    conn = await get_connection()
    try:
        rows = await conn.fetch(
            "SELECT id, product_id, marketplace, url, created_at FROM marketplace_link WHERE product_id = $1",
            product_id
        )
        return [MarketplaceLinkResponse(id=str(r["id"]), product_id=str(r["product_id"]), marketplace=r["marketplace"], url=r["url"], created_at=str(r["created_at"])) for r in rows]
    finally:
        await release_connection(conn)

@app.post("/produtos/{product_id}/links", summary="Create link for product", status_code=201, response_model=MarketplaceLinkResponse)
async def create_link(product_id: str, payload: MarketplaceLinkCreate):
    conn = await get_connection()
    try:
        row = await conn.fetchrow('SELECT id FROM product WHERE id = $1', product_id)
        if not row:
            raise HTTPException(status_code=404, detail='Product not found')
        row = await conn.fetchrow(
            "INSERT INTO marketplace_link (product_id, marketplace, url) VALUES ($1, $2, $3) RETURNING id, created_at",
            product_id, payload.marketplace, payload.url
        )
        return MarketplaceLinkResponse(id=str(row["id"]), product_id=product_id, marketplace=payload.marketplace, url=payload.url, created_at=str(row["created_at"]))
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=409, detail='URL already exists for another product')
    finally:
        await release_connection(conn)

@app.delete("/links/{link_id}", summary='Delete link by ID', status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(link_id: str):
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            "SELECT id FROM marketplace_link WHERE id = $1", link_id
        )
        if not row:
            raise HTTPException(status_code=404, detail='Link not found')
        await conn.execute("DELETE FROM marketplace_link WHERE id = $1", link_id)
    finally:
        await release_connection(conn)