from flask import Blueprint, render_template

suppliers_bp = Blueprint("suppliers", __name__)


@suppliers_bp.route("/varieties/<variety_id>/suppliers")
def supplier_varieties(variety_id):
    return render_template(
        "supplier_varieties.html",
        variety_id=variety_id
    )