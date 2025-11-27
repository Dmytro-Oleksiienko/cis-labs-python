import datetime
from typing import Dict

from app.database.database import SessionLocal
from app.models.order_decision import OrderDecision
from app.repositories.order_decision_repo import OrderDecisionRepository
class CancelledOrdersListener:

    def __init__(self):
        self.db = SessionLocal()
        self.repo = OrderDecisionRepository(self.db)

    def handle_cancelled(self, msg: str):

        cleaned = msg.replace("CANCELLED |", "").strip()
        data = self.parse(cleaned)

        order_id = self.parse_long(data.get("ORDER_ID"))
        username = data.get("USER", "Guest")
        total = self.parse_double(data.get("TOTAL"))
        reason = data.get("REASON", "Not specified")
        lost = self.parse_double(data.get("LOST")) or total

        decision = OrderDecision(
            order_id=order_id,
            username=username,
            status="CANCELLED",
            total_amount=total,
            cancel_reason=reason,
            lost_amount=lost,
            created_at=datetime.datetime.now()
        )

        self.repo.save(decision)

        print(f"⚠️ [Quality Service] Saved cancelled order: {msg}")


    def parse(self, msg: str) -> Dict[str, str]:
        parts = msg.split(";")
        items = {}
        for part in parts:
            part = part.strip()
            if "=" in part:
                key, value = part.split("=", 2)
                items[key] = value
        return items

    def parse_long(self, v: str):
        try:
            return int(v.strip()) if v else None
        except:
            return None

    def parse_double(self, v: str):
        try:
            return float(v.strip()) if v else None
        except:
            return None