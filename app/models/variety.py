from app.extensions import db


class Variety(db.Model):
    __tablename__ = "varieties"

    variety_id = db.Column(db.String(10), primary_key=True)

    crop_id = db.Column(
        db.String(10),
        db.ForeignKey("crops.crop_id"),
        nullable=False
    )

    variety_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)