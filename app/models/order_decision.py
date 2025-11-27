from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database.database import Base


class OrderDecision(Base):
    __tablename__ = "order_decisions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, index=True, nullable=False)

    username = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)

    total_amount = Column(Float, nullable=False)
    lost_amount = Column(Float, nullable=True)

    cancel_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<OrderDecision id={self.id} order_id={self.order_id} status={self.status}>"