from pydantic import BaseModel
from typing import Optional

class CancelledOrderMessage(BaseModel):
    order_id: int
    username: str
    total: float
    reason: Optional[str] = None
    lost_amount: float