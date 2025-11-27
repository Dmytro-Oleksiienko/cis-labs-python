from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String)
    manufacturer = Column(String)
    country = Column(String)
    color = Column(String)
    image_url = Column(String)
    price = Column(Float)
    storage = Column(String)
    screen_size = Column(String)

    def __init__(self, name: str, manufacturer: str = None, country: str = None,
                 color: str = None, price: float = None,
                 image_url: str = None, storage: str = None, screen_size: str = None):
        self.name = name
        self.manufacturer = manufacturer
        self.country = country
        self.color = color
        self.image_url = image_url
        self.price = price
        self.storage = storage
        self.screen_size = screen_size

    def __repr__(self):
        return f"<Product id={self.id} name={self.name} price={self.price}>"