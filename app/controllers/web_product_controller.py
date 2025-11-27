from typing import Optional, List

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from pathlib import Path

from app.database.database import get_db
from app.services.product_service import ProductService
from app.schemas.product import ProductDto
from app.services.product_mapper import ProductMapper

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent   # .../app
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@router.get("/", response_class=HTMLResponse)
@router.get("/products", response_class=HTMLResponse)
def index(
    request: Request,
    priceRange: Optional[str] = Query(None, alias="priceRange"),
    country: Optional[str] = Query(None),
    manufacturer: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    products = service.filter_products(priceRange, country, manufacturer)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "products": products,
            "priceRange": priceRange,
            "country": country,
            "manufacturer": manufacturer,
            "user": request.state.user
        },
    )


@router.get("/test", response_model=List[ProductDto])
def test_products(db: Session = Depends(get_db)):
    service = ProductService(db)
    products = service.get_all_products()
    return [ProductMapper.to_dto(p) for p in products]