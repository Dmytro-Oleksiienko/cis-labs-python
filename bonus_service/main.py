from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Bonus Service")


class BonusRequest(BaseModel):
    total: float


class BonusResponse(BaseModel):
    bonus: int


@app.post("/bonus/calculate", response_model=BonusResponse)
def calculate_bonus(req: BonusRequest):

    raw_bonus = req.total * 0.05
    bonus = int(raw_bonus)

    if bonus < 0:
        bonus = 0

    return BonusResponse(bonus=bonus)