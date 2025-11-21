from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.product_repository import ProductRepository

class ProductService:
    def __init__(self, db: Session):
        self.repo = ProductRepository(db)

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.repo.find_by_id(product_id)

    def get_all_products(self) -> List[Product]:
        return self.repo.find_all()

    def filter_products(
        self,
        price_range: Optional[str],
        country: Optional[str],
        manufacturer: Optional[str],
    ) -> List[Product]:

        min_price = 0
        max_price = 2**31 - 1

        if price_range and "-" in price_range:
            try:
                a, b = price_range.split("-")
                min_price = int(a)
                max_price = int(b)
            except ValueError:
                pass

        return self.repo.find_by_filters(
            min_price,
            max_price,
            country if country and country.strip() else None,
            manufacturer if manufacturer and manufacturer.strip() else None,
        )