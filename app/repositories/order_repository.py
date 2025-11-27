from sqlalchemy.orm import Session
from app.models.order import Order

class OrderRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(Order).all()

    @staticmethod
    def get_by_id(db: Session, id: int):
        return db.query(Order).filter(Order.id == id).first()

    @staticmethod
    def save(db: Session, order: Order):
        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def delete(db: Session, id: int):
        obj = db.query(Order).filter(Order.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()