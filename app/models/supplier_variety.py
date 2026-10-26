from app.extensions import db


class SupplierVariety(db.Model):
    __tablename__ = "supplier_varieties"

    supplier_id = db.Column(
        db.String(10),
        db.ForeignKey("suppliers.supplier_id"),
        primary_key=True
    )

    variety_id = db.Column(
        db.String(10),
        db.ForeignKey("varieties.variety_id"),
        primary_key=True
    )

    availability = db.Column(db.Boolean, nullable=False, default=True)