from app.extensions import db


class Supplier(db.Model):
    __tablename__ = "suppliers"

    supplier_id = db.Column(db.String(10), primary_key=True)
    supplier_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    sector_id = db.Column(
        db.String(10),
        db.ForeignKey("sectors.sector_id"),
        nullable=False
    )