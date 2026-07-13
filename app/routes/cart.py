from flask import Blueprint, render_template, redirect, session, url_for
from datetime import datetime

from app.utils.db import get_db

cart_bp = Blueprint("cart", __name__)


@cart_bp.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    if "customer_id" not in session:
        return redirect(url_for("auth.login"))

    customer_id = session["customer_id"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM cart
        WHERE customer_id=? AND product_id=?
    """, (customer_id, product_id))

    item = cursor.fetchone()

    if item:
        cursor.execute("""
            UPDATE cart
            SET quantity = quantity + 1
            WHERE customer_id=? AND product_id=?
        """, (customer_id, product_id))
    else:
        cursor.execute("""
            INSERT INTO cart (customer_id, product_id, quantity)
            VALUES (?, ?, 1)
        """, (customer_id, product_id))

    conn.commit()
    conn.close()

    return redirect("/cart")


@cart_bp.route("/cart")
def cart():
    if "customer_id" not in session:
        return redirect(url_for("auth.login"))

    customer_id = session["customer_id"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT cart.cart_id, cart.quantity,
               products.name, products.price, products.product_id
        FROM cart
        JOIN products ON cart.product_id = products.product_id
        WHERE cart.customer_id=?
    """, (customer_id,))

    cart_items = cursor.fetchall()

    total = 0
    for item in cart_items:
        total += item["price"] * item["quantity"]

    conn.close()

    return render_template("cart.html", cart_items=cart_items, total=total)


@cart_bp.route("/remove_from_cart/<int:cart_id>")
def remove_from_cart(cart_id):
    if "customer_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM cart
        WHERE cart_id=?
    """, (cart_id,))

    conn.commit()
    conn.close()

    return redirect("/cart")


@cart_bp.route("/checkout")
def checkout():
    if "customer_id" not in session:
        return redirect(url_for("auth.login"))

    customer_id = session["customer_id"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT cart.quantity,
               products.product_id,
               products.price
        FROM cart
        JOIN products ON cart.product_id = products.product_id
        WHERE cart.customer_id=?
    """, (customer_id,))

    cart_items = cursor.fetchall()

    if not cart_items:
        conn.close()
        return redirect("/cart")

    total = 0
    for item in cart_items:
        total += item["price"] * item["quantity"]

    cursor.execute("""
        INSERT INTO orders (customer_id, date, total, status)
        VALUES (?, ?, ?, ?)
    """, (
        customer_id,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total,
        "Pending"
    ))

    order_id = cursor.lastrowid

    for item in cart_items:
        cursor.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (?, ?, ?, ?)
        """, (
            order_id,
            item["product_id"],
            item["quantity"],
            item["price"]
        ))

        cursor.execute("""
            UPDATE products
            SET quantity = quantity - ?
            WHERE product_id = ?
        """, (
            item["quantity"],
            item["product_id"]
        ))

    cursor.execute("""
        DELETE FROM cart
        WHERE customer_id=?
    """, (customer_id,))

    conn.commit()
    conn.close()

    return render_template("checkout.html", total=total)
