from flask import Blueprint
from flask import render_template

main = Blueprint("main", __name__, url_prefix="/ssas/")

@main.route("/")
def home():
    return render_template("home.html")