from flask import Blueprint, Response, jsonify, request
from werkzeug.exceptions import HTTPException

from api import database
from api.models import Id
from api.products.models import Product

products = Blueprint("products", __name__, url_prefix="/products")


@products.route("/", methods=["GET"])
def get_products():
    p_type = Product.validate_args(request.args.get("type"))
    return Product.dump(database.search_products(p_type))


@products.route("/", methods=["POST"])
def add_product():
    product: Product = Product.new_product(request.json)
    product = database.add_product(product)
    return jsonify(id=product.id)


@products.route("<id>", methods=["GET"])
def get_product(id: str):  # noqa: A002
    params: Id = Id.load(id)
    product = database.get_product_by_id_or_404(params.id)
    return Product.dump(product)


@products.route("<id>", methods=["POST"])
def update_product(id: str):  # noqa: A002
    params: Id = Id.load(id)
    product = database.get_product_by_id_or_404(params.id)
    new_data: Product = Product.load(request.json)
    database.update_product(product, new_data)
    return Response("success", 200, mimetype="text/plain")


@products.route("<id>", methods=["DELETE"])
def delete_product(id: str):  # noqa: A002F
    params: Id = Id.load(id)
    product = database.get_product_by_id_or_404(params.id)
    database.delete_product(product)
    return Response("success", 200, mimetype="text/plain")


@products.route("<id>/image", methods=["PUT"])
def update_product_image(id: str):  # noqa: A002
    params: Id = Id.load(id)
    new_image = Product.validate_image(request.files.get("image"))
    try:
        product = database.get_product_by_id_or_404(params.id)
    except HTTPException:
        # TODO: Add example id in openAPI Specification on order_api_v3.yaml
        return jsonify(message="Product image updated successfully", productId=params.id)
    database.update_product_image(product, new_image)
    return jsonify(message="Product image updated successfully", productId=params.id)
