from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.product import Product

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def save(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete_by_id(self, product_id: int) -> None:
        self.db.query(Product).filter(Product.id == product_id).delete()
        self.db.commit()

    def exists_by_id(self, product_id: int) -> bool:
        return (
            self.db.query(Product).filter(Product.id == product_id).count() > 0
        )

    def find_by_filters(
        self,
        min_price: int,
        max_price: int,
        country: Optional[str],
        manufacturer: Optional[str],
    ) -> List[Product]:
        q = self.db.query(Product).filter(
            Product.price >= min_price,
            Product.price <= max_price,
        )

        if country is not None:
            q = q.filter(Product.country == country)

        if manufacturer is not None:
            q = q.filter(Product.manufacturer == manufacturer)

        return q.all()