from typing import Optional
from pydantic import BaseModel

class ProductBase(BaseModel):
    name: Optional[str] = None
    manufacturer: Optional[str] = None
    country: Optional[str] = None
    color: Optional[str] = None
    price: Optional[float] = None
    imageUrl: Optional[str] = None
    storage: Optional[str] = None
    screenSize: Optional[str] = None


class ProductCreateDto(ProductBase):
    name: str
    price: float


class ProductUpdateDto(ProductBase):

    pass


class ProductDto(BaseModel):
    id: int
    name: str
    manufacturer: Optional[str] = None
    country: Optional[str] = None
    color: Optional[str] = None
    price: float

    class Config:
        orm_mode = True