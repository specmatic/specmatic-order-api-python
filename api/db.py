import pathlib
from itertools import count

from flask import abort
from werkzeug.datastructures import FileStorage

from api.orders.models import Order, OrderStatus
from api.products.models import Product, ProductType


class Database:
    def __init__(self, upload_folder: pathlib.Path) -> None:
        self.init_data()
        self.upload_folder = upload_folder

    def save_image(self, image: FileStorage, fallback_filename: str) -> str:
        file_name = image.filename or fallback_filename
        save_path = self.upload_folder / file_name
        image.save(save_path)
        return str(save_path)

    def all_products(self):
        return list(self._products.values())

    def get_product_by_id(self, product_id: int):
        return self._products.get(product_id)

    def get_product_by_id_or_404(self, product_id: int):
        product = self._products.get(product_id)
        if not product:
            abort(404, f"Product with ID {product_id} was not found")
        return product

    def search_products(self, product_type: ProductType | None):
        if not product_type:
            return self.all_products()
        return [product for product in self._products.values() if product.type == product_type]

    def add_product(self, product: Product):
        product.id = next(self.product_iter)
        self._products[product.id] = product
        return product

    def update_product(self, product: Product, new_data: Product):
        product.name = new_data.name
        product.type = new_data.type
        product.inventory = new_data.inventory

    def get_product_images(self, product: Product) -> list[str]:
        return self._product_images.get(product.id, [])

    def update_product_image(self, product: Product, new_image: FileStorage):
        save_path = self.save_image(new_image, fallback_filename=f"{product.id}.png")
        if not self._product_images.get(product.id):
            self._product_images[product.id] = []
        self._product_images[product.id].append(save_path)

    def delete_product(self, product: Product):
        if self._products.get(product.id):
            del self._products[product.id]

    def all_orders(self):
        return self._orders.values()

    def get_order_by_id(self, order_id: int):
        return self._orders.get(order_id)

    def get_order_by_id_or_404(self, order_id: int):
        order = self._orders.get(order_id)
        if not order:
            abort(404, f"Order with ID {order_id} was not found")
        return order

    def __order_filter(self, order: Order, product_id: int | None, status: OrderStatus | None):
        return (not product_id or order.productid == product_id) and (not status or order.status == status)

    def search_orders(self, product_id: int | None, status: OrderStatus | None):
        return [order for order in self._orders.values() if self.__order_filter(order, product_id, status)]

    def add_order(self, order: Order):
        order.id = next(self.order_iter)
        self._orders[order.id] = order
        return order

    def update_order(self, order: Order, new_data: Order):
        order.productid = new_data.productid
        order.count = new_data.count
        order.status = new_data.status

    def delete_order(self, order: Order):
        if self._orders.get(order.id):
            del self._orders[order.id]

    def init_data(self):
        self._products = {
            10: Product(name="XYZ Phone", type=ProductType.GADGET, inventory=10, id=10),
            20: Product(name="Gemini", type=ProductType.OTHER, inventory=10, id=20),
        }

        self._product_images = {
            10: ["https://picsum.photos/id/0/5000/3333"],
            20: ["https://picsum.photos/id/0/5000/3333"],
        }

        self._orders = {
            10: Order(productid=10, count=2, status=OrderStatus.PENDING, id=10),
            20: Order(productid=10, count=1, status=OrderStatus.PENDING, id=20),
        }

        self.product_iter = count((max(self._products) + 1) if self._products else 1)
        self.order_iter = count((max(self._orders) + 1) if self._orders else 1)

    def reset(self):
        self.init_data()
