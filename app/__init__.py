from flask import Flask

from config import Config
from app.utils.db import init_db

from app.routes.auth import auth_bp
from app.routes.shop import shop_bp
from app.routes.cart import cart_bp
from app.routes.wishlist import wishlist_bp
from app.routes.profile import profile_bp
from app.routes.admin import admin_bp


def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    app.config.from_object(Config)

    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(wishlist_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)

    init_db()

    return app