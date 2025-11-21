from pydantic import BaseModel

class ConfirmedOrderMessage(BaseModel):
    order_id: int
    username: str
    total: float