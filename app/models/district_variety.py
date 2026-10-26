
from app.extensions import db


class DistrictVariety(db.Model):
    __tablename__ = "district_varieties"

    district_id = db.Column(
        db.String(10),
        db.ForeignKey("districts.district_id"),
        primary_key=True
    )

    variety_id = db.Column(
        db.String(10),
        db.ForeignKey("varieties.variety_id"),
        primary_key=True
    )

    suitability_status = db.Column(
        db.String(30),
        nullable=False
    )

    evidence_source = db.Column(
        db.Text,
        nullable=True
    )
