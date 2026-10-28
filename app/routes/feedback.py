
# app/routes/feedback.py
# Handles farmer feedback and checks that the selected
# variety is registered for the district before saving.

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
    current_app
)

from app.extensions import db
from app.models.district import District
from app.models.variety import Variety
from app.models.district_variety import DistrictVariety
from app.models.feedback import Feedback


feedback_bp = Blueprint(
    "feedback",
    __name__,
    url_prefix="/ssas"
)


@feedback_bp.route(
    "/varieties/<variety_id>/feedback",
    methods=["GET", "POST"]
)
def feedback(variety_id):

    # Fetch the variety selected by the farmer.
    variety = db.session.get(Variety, variety_id)

    if variety is None:
        abort(404)

    districts = District.query.order_by(
        District.district_name
    ).all()

    selected_district_id = ""
    selected_outcome = ""
    comments = ""

    if request.method == "POST":

        selected_district_id = request.form.get(
            "district_id", ""
        ).strip()

        selected_outcome = request.form.get(
            "experience", ""
        ).strip()

        comments = request.form.get(
            "message", ""
        ).strip()

        allowed_outcomes = {
            "good",
            "average",
            "poor",
            "not_harvested"
        }

        district = db.session.get(
            District, selected_district_id
        )

        if district is None:
            flash(
                "Banza uhitemo akarere nyako.",
                "error"
            )

        elif selected_outcome not in allowed_outcomes:
            flash(
                "Hitamo uko igihingwa cyitwaye.",
                "error"
            )

        else:
            # Confirm that this variety is registered
            # for the selected district.
            district_variety = DistrictVariety.query.filter_by(
                district_id=district.district_id,
                variety_id=variety.variety_id
            ).first()

            if district_variety is None:
                flash(
                    "Ubwoko wahisemo ntabwo bwanditswe muri "
                    "aka karere. Hitamo akarere ubwo bwoko "
                    "bwanditswemo.",
                    "error"
                )

            else:
                new_feedback = Feedback(
                    variety_id=variety.variety_id,
                    district_id=district.district_id,
                    outcome=selected_outcome,
                    comments=comments or None
                )

                try:
                    db.session.add(new_feedback)
                    db.session.commit()

                    flash(
                        "Igitekerezo cyawe cyakiriwe neza. Murakoze!",
                        "success"
                    )

                    return redirect(
                        url_for(
                            "feedback.feedback",
                            variety_id=variety.variety_id
                        )
                    )

                except Exception:
                    db.session.rollback()

                    current_app.logger.exception(
                        "Failed to save farmer feedback."
                    )

                    flash(
                        "Habaye ikibazo mu kubika igitekerezo. "
                        "Ongera ugerageze.",
                        "error"
                    )

    return render_template(
        "feedback.html",
        variety=variety,
        districts=districts,
        selected_district_id=selected_district_id,
        selected_outcome=selected_outcome,
        comments=comments
    )
