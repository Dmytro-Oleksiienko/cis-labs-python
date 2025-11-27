import os
import httpx


class BonusClient:
    def __init__(self):
        self.base_url = os.getenv("BONUS_SERVICE_URL", "http://127.0.0.1:8001").rstrip("/")

    def calculate_bonus(self, total: float) -> int:
        try:
            resp = httpx.post(
                f"{self.base_url}/bonus/calculate",
                json={"total": total},
                timeout=2.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return int(data.get("bonus", 0))
        except Exception as e:
            print(f"[BonusClient] Помилка запиту до bonus_service: {e}")
            return 0