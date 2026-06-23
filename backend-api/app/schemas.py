from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)

class ProductUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=255)

class ProductResponse(BaseModel):
    id: str
    name: str