from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)

class ProductUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=255)

class ProductResponse(BaseModel):
    id: str
    name: str

class MarketplaceLinkCreate(BaseModel):
    marketplace: str = Field(min_length=2, max_length=50)
    url: str = Field(min_length=5)

class MarketplaceLinkResponse(BaseModel):
    id: str
    product_id: str
    marketplace: str
    url: str
    created_at: str

class PriceHistoryCreate(BaseModel):
    price: float = Field(gt=0)
    is_available: bool = True

class PriceHistoryResponse(BaseModel):
    id: str
    link_id: str
    price: float
    is_available: bool
    captured_at: str