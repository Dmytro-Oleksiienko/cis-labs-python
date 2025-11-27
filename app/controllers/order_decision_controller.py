from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.order_decision import OrderDecision
from app.schemas.order_schemas import OrderDecisionDto

router = APIRouter(
    prefix="/api/order-decisions",
    tags=["order-decisions"],
)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/ping")
def ping():
    return {"message": "Controller is working ✅"}


@router.get("/", response_model=List[OrderDecisionDto])
def get_all(db: Session = Depends(get_db)):
    decisions = db.query(OrderDecision).all()
    return decisions


@router.get("/{order_id}", response_model=List[OrderDecisionDto])
def get_by_order_id(order_id: int, db: Session = Depends(get_db)):
    decisions = (
        db.query(OrderDecision)
        .filter(OrderDecision.order_id == order_id)
        .all()
    )
    return decisions