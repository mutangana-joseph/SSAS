from app.extensions import db


class Sector(db.Model):
    __tablename__ = "sectors"

    sector_id = db.Column(db.String(10), primary_key=True)

    district_id = db.Column(
        db.String(10),
        db.ForeignKey("districts.district_id"),
        nullable=False
    )

    sector_name = db.Column(db.String(100), nullable=False)