
from flask import Blueprint, render_template, request, jsonify, abort

from app.models.district import District
from app.models.sector import Sector
from app.models.crop import Crop

feedback_bp = Blueprint("feedback", __name__)


@feedback_bp.route("/varieties/<variety_id>/feedback",methods=["GET", "POST"]
)
def feedback(variety_id):

    districts = District.query.order_by(
        District.district_name
    ).all()

    crops=Crop.query.order_by(Crop.crop_name).all()

    if request.method == "POST":
        # We will validate and save the submitted feedback here next.
        print(request.form)

    return render_template(
        "feedback.html",
        variety_id=variety_id,
        districts=districts, crops=crops
    )


@feedback_bp.route("/feedback/sectors/<district_id>")
def sectors_for_district(district_id):

    district = District.query.get(district_id)

    if district is None:
        abort(404)

    sectors = Sector.query.filter_by(
        district_id=district_id
    ).order_by(
        Sector.sector_name
    ).all()

    return jsonify([
        {
            "sector_id": sector.sector_id,
            "sector_name": sector.sector_name
        }
        for sector in sectors
    ])
