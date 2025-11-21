from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OrderDecisionDto(BaseModel):
    id: int
    order_id: int
    username: Optional[str] = None
    status: str
    total_amount: float
    lost_amount: Optional[float] = None
    cancel_reason: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True