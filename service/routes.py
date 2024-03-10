from flask import jsonify, request, abort, url_for
from service.models import Product
from service.common import status
from . import app


@app.route("/health")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="OK"), status.HTTP_200_OK


@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


@app.route("/products", methods=["POST"])
def create_products():
    """
    Creates a Product
    This endpoint will create a Product based the data in the body that is posted
    """
    app.logger.info("Request to Create a Product...")
    check_content_type("application/json")

    data = request.get_json()
    app.logger.info("Processing: %s", data)
    product = Product()
    product.deserialize(data)
    product.create()
    app.logger.info("Product with new id [%s] saved!", product.id)

    message = product.serialize()
    location_url = url_for("get_products", product_id=product.id, _external=True)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


@app.route("/products/<int:product_id>", methods=["GET"])
def get_products(product_id):
    """
    Retrieve a single Product
    This endpoint will return a Product based on its id
    """
    app.logger.info("Request to Read a Product with id: %s", product_id)
    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id {product_id} was not found")
    return jsonify(product.serialize()), status.HTTP_200_OK


@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    """
    Update a Product
    This endpoint will update a Product based on its id and the data provided in the request body
    """
    app.logger.info("Request to Update a Product with id: %s", product_id)
    check_content_type("application/json")

    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id {product_id} was not found")

    data = request.get_json()
    app.logger.info("Processing: %s", data)
    product.deserialize(data)
    product.update()
    app.logger.info("Product with id [%s] updated!", product_id)

    return jsonify(product.serialize()), status.HTTP_200_OK


@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """
    Delete a Product
    This endpoint will delete a Product based on its id
    """
    app.logger.info("Request to Delete a Product with id: %s", product_id)

    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id {product_id} was not found")

    product.delete()
    app.logger.info("Product with id [%s] deleted!", product_id)

    return "", status.HTTP_204_NO_CONTENT


@app.route("/products", methods=["GET"])
def list_products():
    """
    List all Products
    This endpoint will return a list of all Products
    """
    app.logger.info("Request to List all Products")
    products = Product.all()
    return jsonify([product.serialize() for product in products]), status.HTTP_200_OK


