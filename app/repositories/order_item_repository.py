from sqlalchemy.orm import Session
from app.models.order_item import OrderItem

class OrderItemRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(OrderItem).all()

    @staticmethod
    def get_by_id(db: Session, id: int):
        return db.query(OrderItem).filter(OrderItem.id == id).first()

    @staticmethod
    def save(db: Session, item: OrderItem):
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete(db: Session, id: int):
        obj = db.query(OrderItem).filter(OrderItem.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()