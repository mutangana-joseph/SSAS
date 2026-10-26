
from app.routes.home import home_bp
from app.routes.varieties import varieties_bp
from app.routes.suppliers import suppliers_bp
from app.routes.feedback import feedback_bp
from app.routes.admin import admin_bp


def register_routes(app):
    app.register_blueprint(home_bp)
    app.register_blueprint(varieties_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(admin_bp)