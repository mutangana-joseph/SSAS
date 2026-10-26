from app.extensions import db


class GrowingGuide(db.Model):
    __tablename__ = "growing_guides"

    guide_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    district_id = db.Column(
        db.String(10),
        db.ForeignKey("districts.district_id"),
        nullable=False
    )

    variety_id = db.Column(
        db.String(10),
        db.ForeignKey("varieties.variety_id"),
        nullable=False
    )

    introduction = db.Column(db.Text, nullable=False)