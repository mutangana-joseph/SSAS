from app.extensions import db


class District(db.Model):
    __tablename__ = "districts"

    district_id = db.Column(db.String(10), primary_key=True)
    district_name = db.Column(db.String(100), nullable=False)