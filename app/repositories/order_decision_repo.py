from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.order_decision import OrderDecision


class OrderDecisionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, decision: OrderDecision) -> OrderDecision:
        self.db.add(decision)
        self.db.commit()
        self.db.refresh(decision)
        return decision

    def find_all(self) -> List[OrderDecision]:
        return (
            self.db.query(OrderDecision)
            .order_by(OrderDecision.id.desc())
            .all()
        )

    def find_by_id(self, decision_id: int) -> Optional[OrderDecision]:
        return (
            self.db.query(OrderDecision)
            .filter(OrderDecision.id == decision_id)
            .first()
        )