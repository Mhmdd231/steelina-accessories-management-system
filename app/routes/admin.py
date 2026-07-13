from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import check_password_hash
from app.utils.db import get_db

admin_bp = Blueprint("admin", __name__)


#Group_1:login/logout
@admin_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM admins
            WHERE username=?
        """, (username,))

        admin = cursor.fetchone()
        conn.close()

        if admin and check_password_hash(admin["password"], password):
            session["admin_id"] = admin["admin_id"]
            session["admin_username"] = admin["username"]
            return redirect("/admin/dashboard")

        return "Invalid admin username or password"

    return render_template("admin_login.html")


@admin_bp.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None)
    session.pop("admin_username", None)
    return redirect("/admin/login")



#Group_2:dashboard
@admin_bp.route("/admin/dashboard")
def admin_dashboard():
    if "admin_id" not in session:
        return redirect("/admin/login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM customers")
    total_customers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total) FROM orders")
    total_sales = cursor.fetchone()[0]

    if total_sales is None:
        total_sales = 0

    cursor.execute("""
        SELECT status, COUNT(*)
        FROM orders
        GROUP BY status
    """)
    order_status_data = cursor.fetchall()

    status_labels = []
    status_values = []

    for row in order_status_data:
        status_labels.append(row[0])
        status_values.append(row[1])

    conn.close()

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_customers=total_customers,
        total_orders=total_orders,
        total_sales=total_sales,
        status_labels=status_labels,
        status_values=status_values
    )

#Group_3:product management
@admin_bp.route("/admin/products")
def admin_products():

    if "admin_id" not in session:
        return redirect("/admin/login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products
        ORDER BY product_id DESC
    """)

    products = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_products.html",
        products=products
    )


@admin_bp.route("/admin/products/add", methods=["GET", "POST"])
def add_product():
    if "admin_id" not in session:
        return redirect("/admin/login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM categories ORDER BY category_name")
    categories = cursor.fetchall()

    if request.method == "POST":
        name = request.form["name"]
        category = request.form["category"]
        price = request.form["price"]
        quantity = request.form["quantity"]
        description = request.form["description"]

        cursor.execute("""
            INSERT INTO products
            (name, category, price, quantity, image, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            category,
            price,
            quantity,
            "default.jpg",
            description
        ))

        conn.commit()
        conn.close()

        return redirect("/admin/products")

    conn.close()

    return render_template(
        "add_product.html",
        categories=categories
    )


@admin_bp.route("/admin/products/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if "admin_id" not in session:
        return redirect("/admin/login")

    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        category = request.form["category"]
        price = request.form["price"]
        quantity = request.form["quantity"]
        description = request.form["description"]

        cursor.execute("""
            UPDATE products
            SET name=?, category=?, price=?, quantity=?, description=?
            WHERE product_id=?
        """, (
            name,
            category,
            price,
            quantity,
            description,
            product_id
        ))

        conn.commit()
        conn.close()

        return redirect("/admin/products")

    cursor.execute("""
        SELECT * FROM products
        WHERE product_id=?
    """, (product_id,))

    product = cursor.fetchone()

    cursor.execute("""
        SELECT * FROM categories
        ORDER BY category_name
    """)

    categories = cursor.fetchall()

    conn.close()

    return render_template(
        "edit_product.html",
        product=product,
        categories=categories
    )


@admin_bp.route("/admin/products/delete/<int:product_id>")
def delete_product(product_id):

    if "admin_id" not in session:
        return redirect("/admin/login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM products
        WHERE product_id=?
    """, (product_id,))

    conn.commit()
    conn.close()

    return redirect("/admin/products")



#Group_4: category management
@admin_bp.route("/admin/categories")
def admin_categories():
    if "admin_id" not in session:
        return redirect("/admin/login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM categories ORDER BY category_id DESC")
    categories = cursor.fetchall()

    conn.close()

    return render_template("admin_categories.html", categories=categories)


@admin_bp.route("/admin/categories/add", methods=["GET", "POST"])
def add_category():
    if "admin_id" not in session:
        return redirect("/admin/login")

    if request.method == "POST":
        category_name = request.form["category_name"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO categories (category_name)
            VALUES (?)
        """, (category_name,))

        conn.commit()
        conn.close()

        return redirect("/admin/categories")

    return render_template("add_category.html")


@admin_bp.route("/admin/categories/edit/<int:category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if "admin_id" not in session:
        return redirect("/admin/login")

    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        category_name = request.form["category_name"]

        cursor.execute("""
            UPDATE categories
            SET category_name=?
            WHERE category_id=?
        """, (category_name, category_id))

        conn.commit()
        conn.close()

        return redirect("/admin/categories")

    cursor.execute("SELECT * FROM categories WHERE category_id=?", (category_id,))
    category = cursor.fetchone()

    conn.close()

    return render_template("edit_category.html", category=category)


@admin_bp.route("/admin/categories/delete/<int:category_id>")
def delete_category(category_id):
    if "admin_id" not in session:
        return redirect("/admin/login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM categories WHERE category_id=?", (category_id,))

    conn.commit()
    conn.close()

    return redirect("/admin/categories")



#Group_5:customer management
@admin_bp.route("/admin/customers")
def admin_customers():
    if "admin_id" not in session:
        return redirect("/admin/login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM customers ORDER BY customer_id DESC")
    customers = cursor.fetchall()

    conn.close()

    return render_template("admin_customers.html", customers=customers)



@admin_bp.route("/admin/customers/delete/<int:customer_id>")
def delete_customer(customer_id):
    if "admin_id" not in session:
        return redirect("/admin/login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM customers WHERE customer_id=?", (customer_id,))

    conn.commit()
    conn.close()

    return redirect("/admin/customers")


#Group_6:orders management
@admin_bp.route("/admin/orders")
def admin_orders():

    if "admin_id" not in session:
        return redirect("/admin/login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT orders.*,
               customers.name
        FROM orders
        JOIN customers
        ON orders.customer_id = customers.customer_id
        ORDER BY order_id DESC
    """)

    orders = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_orders.html",
        orders=orders
    )


@admin_bp.route("/admin/orders/status/<int:order_id>/<status>")
def update_order_status(order_id, status):

    if "admin_id" not in session:
        return redirect("/admin/login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE orders
        SET status=?
        WHERE order_id=?
    """, (
        status,
        order_id
    ))

    conn.commit()
    conn.close()

    return redirect("/admin/orders")


@admin_bp.route("/admin/orders/details/<int:order_id>")
def order_details(order_id):
    if "admin_id" not in session:
        return redirect("/admin/login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT order_items.quantity,
               order_items.price,
               products.name
        FROM order_items
        JOIN products ON order_items.product_id = products.product_id
        WHERE order_items.order_id=?
    """, (order_id,))

    items = cursor.fetchall()

    conn.close()

    return render_template(
        "order_details.html",
        items=items,
        order_id=order_id
    )
