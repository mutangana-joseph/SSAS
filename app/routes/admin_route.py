from flask import Blueprint
from flask import render_template

admin_bp = Blueprint("admin" , __name__, url_prefix="/ssas/admin")

@admin_bp.route("/")

def admin():

    return render_template("admin.html")