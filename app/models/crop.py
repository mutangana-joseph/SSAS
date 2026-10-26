
from app.extensions import db


class Crop(db.Model):
    __tablename__ = "crops"

    crop_id = db.Column(db.String(10), primary_key=True)
    crop_name = db.Column(db.String(100), nullable=False)
