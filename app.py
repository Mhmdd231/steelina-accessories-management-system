from flask import Flask, render_template, request, redirect, session
from datetime import datetime
from app.utils.db import get_db, init_db
from app.routes.auth import auth_bp
from app.routes.shop import shop_bp
from app.routes.cart import cart_bp
from app.routes.wishlist import wishlist_bp
from app.routes.profile import profile_bp
from app.routes.admin import admin_bp

from config import Config

app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static"
)

app.register_blueprint(auth_bp)
app.register_blueprint(shop_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(wishlist_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(admin_bp)
app.config.from_object(Config)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)