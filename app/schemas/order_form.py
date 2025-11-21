from pydantic import BaseModel

class OrderForm(BaseModel):
    address: str
    credit_card: str