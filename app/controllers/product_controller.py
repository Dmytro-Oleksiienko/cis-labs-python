from fastapi import APIRouter, Depends, Query
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.product import ProductDto, ProductCreateDto, ProductUpdateDto
from app.services.product_service import ProductService

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.get("", response_model=List[ProductDto])
def list_products(
    priceRange: Optional[str] = Query(None, alias="priceRange"),
    country: Optional[str] = None,
    manufacturer: Optional[str] = None,
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.list(priceRange, country, manufacturer)


@router.get("/{id}", response_model=ProductDto)
def get_one(id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.get_one(id)

@router.post("", response_model=ProductDto, status_code=201)
def create_product(dto: ProductCreateDto, db: Session = Depends(get_db)):
    service = ProductService(db)
    saved = service.create(dto)
    return saved



@router.put("/{id}", response_model=ProductDto)
def update_product(id: int, dto: ProductUpdateDto, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.put_update(id, dto)


@router.patch("/{id}", response_model=ProductDto)
def patch_product(
    id: int,
    fields: Dict[str, Any],
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.patch_update(id, fields)



@router.delete("/{id}", status_code=204)
def delete_product(id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    service.delete(id)
    return None