from flask import Blueprint, render_template, request
from app.utils.db import get_db

shop_bp = Blueprint("shop", __name__)

@shop_bp.route("/")
def home():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products LIMIT 3")
    products = cursor.fetchall()

    conn.close()

    return render_template("index.html", products=products)


@shop_bp.route("/shop")
def shop():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM categories ORDER BY category_name")
    categories = cursor.fetchall()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    conn.close()

    return render_template("shop.html", products=products, categories=categories)


@shop_bp.route("/product/<int:product_id>")
def product_details(product_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE product_id=?",
        (product_id,)
    )

    product = cursor.fetchone()

    conn.close()

    if not product:
        return "Product Not Found"

    return render_template("product_details.html", product=product)


@shop_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        return render_template(
            "contact.html",
            success=True,
            name=name
        )

    return render_template("contact.html", success=False)


@shop_bp.route("/about")
def about():
    return render_template("about.html")