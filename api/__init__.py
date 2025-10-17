import json
import pathlib
from datetime import UTC, datetime

from flask import Flask, jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

from api.db import Database

app = Flask(__name__)
basedir = pathlib.Path(__file__).parent
app.config["UPLOAD_FOLDER"] = basedir / "static" / "uploads"
app.url_map.strict_slashes = False
database = Database(app.config["UPLOAD_FOLDER"])


@app.errorhandler(ValidationError)
def handle_marshmallow_validation_error(e: "ValidationError"):
    # NOTE:API SPEC V3 specifies that message should be a string not an object / array
    return jsonify(
        timestamp=datetime.now(tz=UTC).isoformat(),
        status=400,
        error="Bad Request",
        message=json.dumps(e.messages),
    ), 400


@app.errorhandler(HTTPException)
def http_error_handler(e: "HTTPException"):
    return jsonify(
        timestamp=datetime.now(tz=UTC).isoformat(),
        status=e.code,
        error=e.name,
        message=e.description,
    ), e.code or 500


from api.orders.routes import orders  # noqa: E402
from api.products.routes import products  # noqa: E402

app.register_blueprint(products)
app.register_blueprint(orders)
