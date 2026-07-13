import sqlite3
import os
from config import Config
from werkzeug.security import generate_password_hash

DB_PATH = Config.DB_PATH

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs("database", exist_ok=True)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            image TEXT,
            description TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        total REAL NOT NULL,
        status TEXT DEFAULT 'Pending'
    )
    """)

    #below the first admin

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM admins")
    admin_count = cursor.fetchone()[0]

    if admin_count == 0:
        cursor.execute("""
        INSERT INTO admins (username, password)
        VALUES (?, ?)
    """, (
        "admin",
        generate_password_hash("admin123")
    ))

    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany("""
            INSERT INTO products (name, category, price, quantity, image, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            ("Golden Bracelet", "Bracelets", 25.00, 10, "bracelet.jpg", "Elegant gold bracelet for daily wear."),
            ("Silver Necklace", "Necklaces", 35.00, 8, "necklace.jpg", "Beautiful silver necklace for special occasions."),
            ("Luxury Ring", "Rings", 45.00, 5, "ring.jpg", "Premium luxury ring with modern design.")
        ])

        # Create categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT UNIQUE NOT NULL
        )
    """)


    cursor.execute("SELECT COUNT(*) FROM categories")
    category_count = cursor.fetchone()[0]

    if category_count == 0:
        cursor.executemany("""
            INSERT INTO categories (category_name)
            VALUES (?)
        """, [
            ("Bracelets",),
            ("Necklaces",),
            ("Rings",)
        ])


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wishlist (
        wishlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL
    )
    """)
    

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL
    )
    """)

    conn.commit()
    conn.close()
