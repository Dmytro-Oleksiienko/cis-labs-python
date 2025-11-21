from app.models.product import Product

class CartItem:
    def __init__(self, product: Product, quantity: int):
        self.product = product
        self.quantity = quantity

    def get_total_price(self) -> float:
        return float(self.product.price) * self.quantity