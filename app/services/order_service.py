from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.order import Order
from app.models.order_item import OrderItem
from app.schemas.order_schemas import OrderCreateDto, OrderItemInput
from app.repositories.order_repository import OrderRepository


class OrderService:
    def __init__(self, db: Session):
        self.repo = OrderRepository(db)
        self.db = db

    def create(self, dto: OrderCreateDto) -> Order:
        order = Order(
            username=dto.username or "Guest",
            address=dto.address,
            credit_card=dto.credit_card
        )

        items = []
        for it in dto.items:
            item = OrderItem(
                product_name=it.product_name,
                quantity=it.quantity,
                price=it.price,
                order=order
            )
            items.append(item)

        order.items = items

        saved = self.repo.save(order)
        return saved

    def get_one(self, order_id: int) -> Order:
        order = self.repo.find_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order not found: {order_id}"
            )
        return order

    def get_all(self):
        return self.repo.find_all()