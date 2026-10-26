from app.extensions import db


class GuideStep(db.Model):
    __tablename__ = "guide_steps"

    step_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    guide_id = db.Column(
        db.Integer,
        db.ForeignKey("growing_guides.guide_id"),
        nullable=False
    )

    step_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    instructions = db.Column(db.Text, nullable=False)