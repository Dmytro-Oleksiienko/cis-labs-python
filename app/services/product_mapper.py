from app.models.product import Product
from app.schemas.product import ProductDto, ProductCreateDto, ProductUpdateDto

class ProductMapper:
    @staticmethod
    def to_dto(p: Product) -> ProductDto:
        return ProductDto(
            id=p.id,
            name=p.name,
            manufacturer=p.manufacturer,
            country=p.country,
            color=p.color,
            price=p.price,
        )

    @staticmethod
    def from_create(d: ProductCreateDto) -> Product:
        p = Product(
            name=d.name,
            manufacturer=d.manufacturer,
            country=d.country,
            color=d.color,
            price=d.price,
        )

        if d.imageUrl is not None:
            p.image_url = d.imageUrl

        if d.storage is not None:
            p.storage = d.storage

        if d.screenSize is not None:
            p.screen_size = d.screenSize

        return p

    @staticmethod
    def apply_update(p: Product, d: ProductUpdateDto) -> None:
        if d.name is not None:
            p.name = d.name

        if d.manufacturer is not None:
            p.manufacturer = d.manufacturer

        if d.country is not None:
            p.country = d.country

        if d.color is not None:
            p.color = d.color

        if d.price is not None:
            p.price = d.price

        if d.imageUrl is not None:
            p.image_url = d.imageUrl

        if d.storage is not None:
            p.storage = d.storage

        if d.screenSize is not None:
            p.screen_size = d.screenSize