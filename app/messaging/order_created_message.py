from typing import List

class OrderCreatedMessage:
    def __init__(self,
                 order_id: int,
                 username: str,
                 items: List["Item"],
                 total: float):
        self.order_id = order_id
        self.username = username
        self.items = items
        self.total = total

    class Item:
        def __init__(self, product_name: str, quantity: int, price: float):
            self.product_name = product_name
            self.quantity = quantity
            self.price = price

        def __repr__(self):
            return f"Item(product_name={self.product_name}, quantity={self.quantity}, price={self.price})"

    def __repr__(self):
        return (
            f"OrderCreatedMessage(order_id={self.order_id}, "
            f"username={self.username}, total={self.total}, "
            f"items={self.items})"
        )