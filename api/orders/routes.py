from flask import Blueprint, Response, abort, jsonify, request

from api import database
from api.models import Id
from api.orders.models import Order

orders = Blueprint("orders", __name__, url_prefix="/orders")


@orders.route("/", methods=["GET"])
def get_orders():
    product_id, status = Order.validate_args(request.args.get("productid"), request.args.get("status"))
    return Order.dump(database.search_orders(product_id, status))


@orders.route("/", methods=["POST"])
def add_order():
    order: Order = Order.new_order(request.json)
    if not database.get_product_by_id(order.productid):
        return abort(400, f"Cannot add Order, Product with ID {order.productid} was not found")
    order = database.add_order(order)
    return jsonify(id=order.id)


@orders.route("/<id>", methods=["GET"])
def get_order(id: str):  # noqa: A002
    params = Id.load(id)
    order = database.get_order_by_id_or_404(params.id)
    return Order.dump(order)


@orders.route("/<id>", methods=["POST"])
def update_order(id: str):  # noqa: A002
    params = Id.load(id)
    order = database.get_order_by_id_or_404(params.id)
    new_data: Order = Order.load(request.json)
    database.update_order(order, new_data)
    return Response("success", 200, mimetype="text/plain")


@orders.route("/<id>", methods=["DELETE"])
def delete_order(id: str):  # noqa: A002
    params = Id.load(id)
    order = database.get_order_by_id_or_404(params.id)
    database.delete_order(order)
    return Response("success", 200, mimetype="text/plain")
