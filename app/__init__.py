from flask import Flask
def create_app():
    app = Flask(__name__)

    from app.routes import main
    from app.routes.admin_route import admin_bp
    app.register_blueprint(main)
    app.register_blueprint(admin_bp)

    return app