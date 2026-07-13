from flask import Blueprint, render_template, request, redirect, session

from app.utils.db import get_db

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/profile", methods=["GET", "POST"])
def profile():
    if "customer_id" not in session:
        return redirect("/login")

    customer_id = session["customer_id"]

    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        cursor.execute("""
            UPDATE customers
            SET name=?, email=?
            WHERE customer_id=?
        """, (name, email, customer_id))

        session["customer_name"] = name

        conn.commit()

    cursor.execute("""
        SELECT * FROM customers
        WHERE customer_id=?
    """, (customer_id,))

    customer = cursor.fetchone()

    conn.close()

    return render_template("profile.html", customer=customer)


@profile_bp.route("/delete_account")
def delete_account():
    if "customer_id" not in session:
        return redirect("/login")

    customer_id = session["customer_id"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM cart WHERE customer_id=?", (customer_id,))
    cursor.execute("DELETE FROM wishlist WHERE customer_id=?", (customer_id,))
    cursor.execute("DELETE FROM customers WHERE customer_id=?", (customer_id,))

    conn.commit()
    conn.close()

    session.clear()

    return redirect("/")


if __name__ == "__main__":
    init_db()
    print(app.url_map)
    app.run(debug=True)