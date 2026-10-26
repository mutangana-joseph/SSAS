
from flask import Blueprint, render_template, request, abort

from app.extensions import db
from app.models.district import District
from app.models.variety import Variety
from app.models.district_variety import DistrictVariety


varieties_bp = Blueprint("varieties", __name__)


# ==================== 1. VARIETIES PAGE ====================
@varieties_bp.route("/varieties")
def varieties():

    # Fetch all districts
    districts = District.query.order_by(
        District.district_name
    ).all()

    # Get the selected district ID from the URL
    selected_district_id = request.args.get("district_id")

    # No results until a district is selected
    variety_results = []
    selected_district = None

    if selected_district_id:

        # Check whether the district exists
        selected_district = db.session.get(
            District, selected_district_id
        )

        if selected_district is None:
            abort(404)

        # Fetch varieties associated with this district
        variety_results = (
            db.session.query(
                Variety,
                DistrictVariety.suitability_status,
                DistrictVariety.evidence_source
            )
            .join(
                DistrictVariety,
                Variety.variety_id == DistrictVariety.variety_id
            )
            .filter(
                DistrictVariety.district_id == selected_district_id
            )
            .order_by(Variety.variety_name)
            .all()
        )

    return render_template(
        "varieties.html",
        districts=districts,
        varieties=variety_results,
        selected_district=selected_district,
        selected_district_id=selected_district_id
    )


# ==================== 2. VARIETY DETAILS PAGE ====================
@varieties_bp.route("/varieties/<variety_id>")
def variety_detail(variety_id):

    # Find the selected variety or return a 404 page
    variety = db.session.get(Variety, variety_id)

    if variety is None:
        abort(404)

    return render_template(
        "variety_detail.html",
        variety=variety
    )
