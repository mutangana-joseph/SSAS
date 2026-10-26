

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash

from app.models.admin import Admin
from app.extensions import db

admin_bp = Blueprint("admin", __name__)


# ==================== ADMIN ENTRY POINT ====================
@admin_bp.route("/admin/")
def admin_index():

    # If the admin is logged in, show the dashboard.
    if session.get("admin_id"):
        return redirect(url_for("admin.admin_dashboard"))

    # Otherwise, require login.
    return redirect(url_for("admin.admin_login"))



# ==================== LOGIN PAGE ====================
@admin_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    # Display the login page.
    if request.method == "GET":
        return render_template("admin_login.html")

    # Receive submitted login details.
    admin_id = request.form.get("admin_id", "").strip()
    password = request.form.get("password", "")

    # Ensure both fields were provided.
    if not admin_id or not password:
        flash("Please enter your admin ID and password.", "error")
        return render_template("admin_login.html")

    # Find the admin account by ID or email.
    admin = Admin.query.filter(
        db.or_(
            Admin.admin_id == admin_id,
            Admin.email == admin_id.lower()
        )
    ).first()

    # Check the account and password.
    if admin is None or not check_password_hash(
        admin.password_hash, password
    ):
        flash("Invalid admin ID/email or password.", "error")
        return render_template("admin_login.html")

    # Start a fresh authenticated session.
    session.clear()
    session["admin_id"] = admin.admin_id

    flash("Login successful. Welcome back!", "success")
    return redirect(url_for("admin.admin_dashboard"))




# ==================== SIGNUP PAGE ====================
@admin_bp.route("/admin/signup", methods=["GET", "POST"])
def admin_signup():

    # Display the signup page.
    if request.method == "GET":
        return render_template("admin_signup.html")

    # Receive submitted form data.
    admin_id = request.form.get("admin_id", "").strip()
    name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")
    access_code = request.form.get("access_code", "")

    # Check required fields.
    if not all([admin_id, name, email, password, confirm_password, access_code]):
        flash("Please fill in all required fields.", "error")
        return render_template("admin_signup.html")

    # Check minimum password length.
    if len(password) < 6:
        flash("Password must contain at least 6 characters.", "error")
        return render_template("admin_signup.html")

    # Confirm both passwords match.
    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return render_template("admin_signup.html")

    # Verify the server-side access code.
    expected_code = current_app.config.get("SSAS_ADMIN_ACCESS_CODE")

    if not expected_code or access_code != expected_code:
        flash("Invalid admin access code.", "error")
        return render_template("admin_signup.html")

    # Check whether the admin ID or email already exists.
    existing_admin = Admin.query.filter(
        db.or_(
            Admin.admin_id == admin_id,
            Admin.email == email
        )
    ).first()

    if existing_admin:
        flash("That admin ID or email is already registered.", "error")
        return render_template("admin_signup.html")

    # Hash the password before saving it.
    password_hash = generate_password_hash(password)

    # Create the admin record.
    new_admin = Admin(
        admin_id=admin_id,
        name=name,
        email=email,
        password_hash=password_hash
    )

    # Insert the record into PostgreSQL.
    try:
        db.session.add(new_admin)
        db.session.commit()

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Admin signup failed.")
        flash("Signup could not be completed. Please try again.", "error")
        return render_template("admin_signup.html")

    flash("Admin account created successfully. You can now log in.", "success")
    return redirect(url_for("admin.admin_login"))


# ==================== PROTECTED DASHBOARD ====================
@admin_bp.route("/admin/dashboard")
def admin_dashboard():

    # Block anyone who has not logged in.
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login"))

    return render_template("admin_dashboard.html")


# ==================== LOGOUT ====================
@admin_bp.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(url_for("admin.admin_login"))
