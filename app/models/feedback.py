from app.extensions import db
from datetime import datetime, timezone


class Feedback(db.Model):
    __tablename__ = "feedback"

    feedback_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    variety_id = db.Column(
        db.String(10),
        db.ForeignKey("varieties.variety_id"),
        nullable=False
    )

    district_id = db.Column(
        db.String(10),
        db.ForeignKey("districts.district_id"),
        nullable=False
    )

    outcome = db.Column(db.String(30), nullable=False)
    comments = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )