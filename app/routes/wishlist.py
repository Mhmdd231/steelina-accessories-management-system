from flask import Blueprint, render_template, redirect, session

from app.utils.db import get_db

wishlist_bp = Blueprint("wishlist", __name__)

@wishlist_bp.route("/add_to_wishlist/<int:product_id>")
def add_to_wishlist(product_id):
    if "customer_id" not in session:
        return redirect("/login")

    customer_id = session["customer_id"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM wishlist
        WHERE customer_id=? AND product_id=?
    """, (customer_id, product_id))

    item = cursor.fetchone()

    if not item:
        cursor.execute("""
            INSERT INTO wishlist (customer_id, product_id)
            VALUES (?, ?)
        """, (customer_id, product_id))

    conn.commit()
    conn.close()

    return redirect("/wishlist")


@wishlist_bp.route("/wishlist")
def wishlist():
    if "customer_id" not in session:
        return redirect("/login")

    customer_id = session["customer_id"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT wishlist.wishlist_id,
            products.product_id,
            products.name,
            products.price,
            products.description,
            products.image
        FROM wishlist
        JOIN products ON wishlist.product_id = products.product_id
        WHERE wishlist.customer_id=?
    """, (customer_id,))

    wishlist_items = cursor.fetchall()

    conn.close()

    return render_template("wishlist.html", wishlist_items=wishlist_items)


@wishlist_bp.route("/remove_from_wishlist/<int:wishlist_id>")
def remove_from_wishlist(wishlist_id):
    if "customer_id" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM wishlist
        WHERE wishlist_id=?
    """, (wishlist_id,))

    conn.commit()
    conn.close()

    return redirect("/wishlist")
