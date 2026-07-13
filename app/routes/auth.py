from flask import Blueprint, render_template, request, redirect, session
import sqlite3
from app.utils.db import get_db
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO customers (name, email, password)
                VALUES (?, ?, ?)
            """, (name, email, password))

            conn.commit()
            conn.close()

            return redirect(url_for("auth.login"))

        except:
            conn.close()
            return "Email already exists"

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        # Get the user by email only
        cursor.execute("""
            SELECT * FROM customers
            WHERE email=?
        """, (email,))

        customer = cursor.fetchone()
        conn.close()

        # Verify the hashed password
        if customer and check_password_hash(customer["password"], password):
            session["customer_id"] = customer["customer_id"]
            session["customer_name"] = customer["name"]
            return redirect("/shop")

        return "Invalid email or password"

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")