from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)

    order_id = Column(Integer, ForeignKey("orders.id"))
    order = relationship("Order", back_populates="items")

    def set_product(self, product):
        if product:
            self.product_name = product.name
            self.price = product.price