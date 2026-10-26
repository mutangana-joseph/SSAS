from flask import Flask
from config import Config
from app.extensions import db
from app.routes import register_routes


from app.models.crop import Crop
from app.models.district import District
from app.models.sector import Sector
from app.models.variety import Variety
from app.models.district_variety import DistrictVariety
from app.models.growing_guide import GrowingGuide
from app.models.guide_step import GuideStep
from app.models.supplier import Supplier
from app.models.supplier_variety import SupplierVariety
from app.models.feedback import Feedback


def create_app():
    app = Flask(__name__)

    # Load application configuration
    app.config.from_object(Config)

    # Connect SQLAlchemy to this Flask application
    db.init_app(app)

    #Register routes
    register_routes(app)
    
    
    return app