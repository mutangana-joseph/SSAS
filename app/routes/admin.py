

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash

#========= DATABASE =====================================
from app.extensions import db

# ==================== DATABASE MODELS ====================
from app.models.admin import Admin
from app.models.crop import Crop
from app.models.variety import Variety
from app.models.district import District
from app.models.sector import Sector
from app.models.district_variety import DistrictVariety
from app.models.growing_guide import GrowingGuide
from app.models.guide_step import GuideStep
from app.models.supplier import Supplier
from app.models.supplier_variety import SupplierVariety
from app.models.feedback import Feedback


#================ ADMIN ROUTE ============================
admin_bp = Blueprint("admin", __name__,url_prefix="/ssas")



#==================== HELPER FUNTIONS=====================
def delete_record(model, record_id):
    # Find the record using its model and ID
    record = db.session.get(model, record_id)

    # Stop if the record does not exist
    if record is None:
        return False

    # Delete the record and save the change
    db.session.delete(record)
    db.session.commit()

    return True
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
        flash("ID/imeri cg umubare w'ibanga bikuranga sibyo .", "error")
        return render_template("admin_login.html")

    # Start a fresh authenticated session.
    session.clear()
    session["admin_id"] = admin.admin_id
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



# ==================== MANAGEMENT ROUTES ====================

# Reusable helper for management pages.
def render_management(section):

    # Only logged-in admins can access management pages.
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login"))

    return render_template(
        "management.html",
        active_section=section
    )



# ==================== MANAGE CROPS ====================
@admin_bp.route("/admin/manage/crops")
def manage_crops():

    # Check whether the admin is logged in.
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login"))

    # Fetch all crops from the database.
    crops = Crop.query.order_by(Crop.crop_id).all()

    # Return the management template with the crops.
    return render_template(
        "management.html",
        active_section="crops",
        crops=crops
    )




# ==================== MANAGE VARIETIES ====================
@admin_bp.route("/admin/manage/varieties")
def manage_varieties():

    # Check whether the admin is logged in.
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login"))

    # Fetch all varieties from the database.
    varieties = Variety.query.order_by(Variety.variety_id).all()

    # Fetch crops so we can display their names alongside varieties.
    crops = Crop.query.order_by(Crop.crop_name).all()

    # Return the management template with the varieties.
    return render_template(
        "management.html",
        active_section="varieties",
        varieties=varieties,
        crops=crops
    )



# ==================== MANAGE DISTRICTS ====================
@admin_bp.route("/admin/manage/districts")
def manage_districts():

    # Check whether the admin is logged in.
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login"))

    # Fetch all districts from the database.
    districts = District.query.order_by(District.district_id).all()

    # Return the management template with the districts.
    return render_template(
        "management.html",
        active_section="districts",
        districts=districts
    )



# ==================== MANAGE SECTORS ====================
@admin_bp.route("/admin/manage/sectors")
def manage_sectors():

    # Check whether the admin is logged in.
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login"))

    # Fetch all sectors from the database.
    sectors = Sector.query.order_by(Sector.sector_id).all()

    # Fetch districts so each sector can be associated with its district.
    districts = District.query.order_by(District.district_name).all()

    # Return the management template with the sectors and districts.
    return render_template(
        "management.html",
        active_section="sectors",
        sectors=sectors,
        districts=districts
    )




# ==================== MANAGE GROWING GUIDES ====================
@admin_bp.route("/admin/manage/guides")
def manage_guides():

    # Check whether the admin is logged in.
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login"))

    # Fetch all growing guides.
    guides = GrowingGuide.query.order_by(
        GrowingGuide.guide_id
    ).all()

    # Fetch guide steps.
    guide_steps = GuideStep.query.order_by(
        GuideStep.guide_id,
        GuideStep.step_number
    ).all()

    # Fetch varieties and districts for displaying their names.
    varieties = Variety.query.order_by(Variety.variety_name).all()
    districts = District.query.order_by(District.district_name).all()

    # Return the management template with the required records.
    return render_template(
        "management.html",
        active_section="guides",
        guides=guides,
        guide_steps=guide_steps,
        varieties=varieties,
        districts=districts
    )


# ==================== MANAGE SUPPLIERS ====================
@admin_bp.route("/admin/manage/suppliers")
def manage_suppliers():

    # Check whether the admin is logged in.
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login"))

    # Fetch all suppliers.
    suppliers = Supplier.query.order_by(
        Supplier.supplier_id
    ).all()

    # Fetch sectors to identify each supplier's location.
    sectors = Sector.query.order_by(
        Sector.sector_name
    ).all()

    # Fetch varieties that suppliers may provide.
    varieties = Variety.query.order_by(
        Variety.variety_name
    ).all()

    # Fetch supplier-variety availability records.
    supplier_varieties = SupplierVariety.query.order_by(
        SupplierVariety.supplier_id,
        SupplierVariety.variety_id
    ).all()

    # Return the management template with the required records.
    return render_template(
        "management.html",
        active_section="suppliers",
        suppliers=suppliers,
        sectors=sectors,
        varieties=varieties,
        supplier_varieties=supplier_varieties
    )

# ==================== MANAGE GUIDE STEPS ====================
@admin_bp.route("/admin/manage/guide-steps")
def manage_guide_steps():

    # Check whether the admin is logged in.
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login"))

    # Fetch all guide steps.
    guide_steps = GuideStep.query.order_by(
        GuideStep.guide_id,
        GuideStep.step_number
    ).all()

    # Fetch guides so each step can be associated with its guide.
    guides = GrowingGuide.query.order_by(
        GrowingGuide.guide_id
    ).all()

    # Return the management template with the required records.
    return render_template(
        "management.html",
        active_section="guide_steps",
        guide_steps=guide_steps,
        guides=guides
    )

# ==================== MANAGE FEEDBACK ====================
@admin_bp.route("/admin/manage/feedback")
def manage_feedback():

    # Check whether the admin is logged in.
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login"))

    # Fetch all feedback records.
    feedback = Feedback.query.all()

    # Return the management template with the feedback.
    return render_template(
        "management.html",
        active_section="feedback",
        feedback=feedback
    )



    #================ ADMIN ACTIONS ==============================
    
@admin_bp.route("/admin/guides/<int:guide_id>/steps/add", methods=["GET", "POST"])
def add_guide_step(guide_id):
    # 1. Make sure the administrator is logged in
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login"))

    # 2. Find the growing guide receiving this step
    guide = db.session.get(GrowingGuide, guide_id)

    if guide is None:
        flash("Growing guide not found.", "error")
        return redirect(url_for("admin.manage_guides"))

    # 3. Process the submitted form
    if request.method == "POST":
        step_number = request.form.get("step_number", "").strip()
        title = request.form.get("title", "").strip()
        instructions = request.form.get("instructions", "").strip()

        if not step_number or not title or not instructions:
            flash("Please fill in all fields.", "error")

        else:
            try:
                step_number = int(step_number)

                if step_number < 1:
                    flash("Step number must be at least 1.", "error")

                else:
                    new_step = GuideStep(
                        guide_id=guide.guide_id,
                        step_number=step_number,
                        title=title,
                        instructions=instructions
                    )

                    db.session.add(new_step)
                    db.session.commit()

                    flash("Guide step added successfully!", "success")
                    return redirect(url_for("admin.manage_guides"))

            except ValueError:
                flash("Step number must be a valid whole number.", "error")

    # 4. Display the form
    return render_template(
        "add_guide_step.html",
        guide=guide
    )



@admin_bp.route(
    "/admin/guide-steps/<int:step_id>/edit",
    methods=["GET", "POST"]
)
def edit_guide_step(step_id):
    # Make sure the administrator is logged in
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login"))

    # Find the step being edited
    step = db.session.get(GuideStep, step_id)

    if step is None:
        flash("Guide step not found.", "error")
        return redirect(url_for("admin.manage_guides"))

    if request.method == "POST":
        step_number = request.form.get("step_number", "").strip()
        title = request.form.get("title", "").strip()
        instructions = request.form.get("instructions", "").strip()

        if not step_number or not title or not instructions:
            flash("Please fill in all fields.", "error")

        else:
            try:
                step_number = int(step_number)

                if step_number < 1:
                    flash("Step number must be at least 1.", "error")

                else:
                    step.step_number = step_number
                    step.title = title
                    step.instructions = instructions

                    db.session.commit()

                    flash("Guide step updated successfully!", "success")
                    return redirect(url_for("admin.manage_guides"))

            except ValueError:
                flash("Step number must be a valid whole number.", "error")

    return render_template(
        "edit_guide_step.html",
        step=step
    )


@admin_bp.route(
    "/admin/guide-steps/<int:step_id>/delete",
    methods=["POST"]
)
def delete_guide_step(step_id):
    # Make sure the administrator is logged in
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login"))

    # Use our reusable helper to delete the guide step
    deleted = delete_record(GuideStep, step_id)

    if deleted:
        flash("Intambwe yasibwe neza!", "success")
    else:
        flash("Intambwe ntiboneka.", "error")

    return redirect(url_for("admin.manage_guides"))


# ============================================================
# ADD CROP
# ============================================================
@admin_bp.route("/admin/crops/add",methods=["GET", "POST"]
)
def add_crop():
    # Kugenzura niba umuyobozi yinjiye muri sisitemu
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login"))

    if request.method == "POST":
        crop_id = request.form.get("crop_id", "").strip()
        crop_name = request.form.get("crop_name", "").strip()

        # Kugenzura ko amakuru yose yatanzwe
        if not crop_id or not crop_name:
            flash(
                "Uzuza imyanya yose isabwa.",
                "error"
            )

        else:
            # Kugenzura niba iyi ID itarakoreshejwe
            existing_crop = db.session.get(Crop, crop_id)

            if existing_crop is not None:
                flash(
                    "Iyi nimero y'igihingwa isanzwe ikoreshwa.",
                    "error"
                )

            else:
                # Gukora igihingwa gishya
                new_crop = Crop(
                    crop_id=crop_id,
                    crop_name=crop_name
                )

                db.session.add(new_crop)
                db.session.commit()

                flash(
                    "Igihingwa gishya cyongeweho neza.",
                    "success"
                )

                return redirect(
                    url_for("admin.manage_crops")
                )

    return render_template("add_crop.html")


# ============================================================
# ADD VARIETY
# ============================================================
@admin_bp.route(
    "/admin/varieties/add",
    methods=["GET", "POST"]
)
def add_variety():
    # Kugenzura niba umuyobozi yinjiye muri sisitemu
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login"))

    # Kubona ibihingwa biri muri database
    crops = Crop.query.order_by(Crop.crop_name).all()

    if request.method == "POST":
        variety_id = request.form.get("variety_id", "").strip()
        crop_id = request.form.get("crop_id", "").strip()
        variety_name = request.form.get("variety_name", "").strip()
        description = request.form.get("description", "").strip()

        # Kugenzura ko amakuru asabwa yuzuye
        if not variety_id or not crop_id or not variety_name:
            flash(
                "Uzuza imyanya yose isabwa.",
                "error"
            )

        else:
            # Kugenzura niba igihingwa cyatoranyijwe kibaho
            crop = db.session.get(Crop, crop_id)

            if crop is None:
                flash(
                    "Igihingwa wahisemo nticyabonetse.",
                    "error"
                )

            else:
                # Kugenzura niba ID y'ubu bwoko itarakoreshejwe
                existing_variety = db.session.get(
                    Variety, variety_id
                )

                if existing_variety is not None:
                    flash(
                        "Iyi nimero y'ubwoko bw'igihingwa isanzwe ikoreshwa.",
                        "error"
                    )

                else:
                    # Gukora ubwoko bushya bw'igihingwa
                    new_variety = Variety(
                        variety_id=variety_id,
                        crop_id=crop_id,
                        variety_name=variety_name,
                        description=description or None
                    )

                    db.session.add(new_variety)
                    db.session.commit()

                    flash(
                        "Ubwoko bushya bw'igihingwa bwongeweho neza.",
                        "success"
                    )

                    return redirect(
                        url_for("admin.manage_varieties")
                    )

    return render_template(
        "add_variety.html",
        crops=crops
    )



# ============================================================
# ADD DISTRICT VARIETY
# ============================================================
@admin_bp.route("/admin/district-varieties/add",methods=["GET", "POST"]
)
def add_district_variety():
    # Kugenzura niba umuyobozi yinjiye muri sisitemu
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login"))

    # Kubona uturere n'ubwoko bw'ibihingwa biri muri database
    districts = District.query.order_by(
        District.district_name
    ).all()

    varieties = Variety.query.order_by(
        Variety.variety_name
    ).all()

    if request.method == "POST":
        district_id = request.form.get(
            "district_id", ""
        ).strip()

        variety_id = request.form.get(
            "variety_id", ""
        ).strip()

        suitability_status = request.form.get(
            "suitability_status", ""
        ).strip()

        evidence_source = request.form.get(
            "evidence_source", ""
        ).strip()

        # Kugenzura amakuru asabwa
        if not district_id or not variety_id or not suitability_status:
            flash("Uzuza imyanya yose isabwa.", "error")

        else:
            district = db.session.get(District, district_id)
            variety = db.session.get(Variety, variety_id)

            if district is None or variety is None:
                flash(
                    "Akarere cyangwa ubwoko bw'igihingwa wahisemo ntibubonetse.",
                    "error"
                )

            else:
                # Kugenzura niba ubwo bwoko butari busanzwe
                # bufitanye isano n'ako karere
                existing_assignment = DistrictVariety.query.filter_by(
                    district_id=district_id,
                    variety_id=variety_id
                ).first()

                if existing_assignment:
                    flash(
                        "Ubu bwoko bw'igihingwa busanzwe bufitanye isano n'aka karere.",
                        "error"
                    )

                else:
                    new_assignment = DistrictVariety(
                        district_id=district_id,
                        variety_id=variety_id,
                        suitability_status=suitability_status,
                        evidence_source=evidence_source or None
                    )

                    db.session.add(new_assignment)
                    db.session.commit()

                    flash(
                        "Ubwoko bw'igihingwa bwahujwe n'akarere neza.",
                        "success"
                    )

                    return redirect(
                        url_for("admin.manage_district_varieties")
                    )

    return render_template(
        "add_district_variety.html",
        districts=districts,
        varieties=varieties
    )



# ============================================================
# MANAGE DISTRICT VARIETIES
# ============================================================
@admin_bp.route("/admin/manage/district-varieties")
def manage_district_varieties():
    # Kugenzura niba umuyobozi yinjiye muri sisitemu
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login"))

    # Kubona ubwoko bw'ibihingwa bwose buhujwe n'uturere
    district_varieties = DistrictVariety.query.all()

    # Kubona uturere n'ubwoko bw'ibihingwa
    districts = District.query.order_by(
        District.district_name
    ).all()

    varieties = Variety.query.order_by(
        Variety.variety_name
    ).all()

    return render_template(
        "management.html",
        active_section="district_varieties",
        district_varieties=district_varieties,
        districts=districts,
        varieties=varieties
    )


#=========================== ADDING GUIDE ===================
@admin_bp.route(
    "/admin/guides/add",
    methods=["GET", "POST"]
)
def add_guide():
    # Kugenzura niba umuyobozi yinjiye muri sisitemu
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login"))

    # Kubona uturere n'ubwoko bw'ibihingwa byo muri database
    districts = District.query.order_by(
        District.district_name
    ).all()

    varieties = Variety.query.order_by(
        Variety.variety_name
    ).all()

    if request.method == "POST":
        district_id = request.form.get(
            "district_id", ""
        ).strip()

        variety_id = request.form.get(
            "variety_id", ""
        ).strip()

        introduction = request.form.get(
            "introduction", ""
        ).strip()

        # Kugenzura ko amakuru yose yatanzwe
        if not district_id or not variety_id or not introduction:
            flash(
                "Uzuza imyanya yose isabwa.",
                "error"
            )

        else:
            # Kugenzura ko akarere n'ubwoko bw'igihingwa bibaho
            district = db.session.get(
                District, district_id
            )

            variety = db.session.get(
                Variety, variety_id
            )

            if district is None or variety is None:
                flash(
                    "Akarere cyangwa ubwoko bw'igihingwa wahisemo ntibubonetse.",
                    "error"
                )

            else:
                # Gukora amabwiriza mashya
                new_guide = GrowingGuide(
                    district_id=district_id,
                    variety_id=variety_id,
                    introduction=introduction
                )

                db.session.add(new_guide)
                db.session.commit()

                flash(
                    "Amabwiriza mashya yo guhinga yongewemo neza.",
                    "success"
                )

                return redirect(
                    url_for("admin.manage_guides")
                )

    return render_template(
        "add_guide.html",
        districts=districts,
        varieties=varieties
    )

#====================== DELETING GUIDE FROM STORED DUIDES ===========================
@admin_bp.route("/admin/guides/<int:guide_id>/delete",methods=["POST"]
)
def delete_guide(guide_id):
    # Kugenzura niba umuyobozi yinjiye muri sisitemu
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login"))

    # Gushaka amabwiriza yo guhinga agiye gusibwa
    guide = db.session.get(GrowingGuide, guide_id)

    if guide is None:
        flash("Amabwiriza yo guhinga ntiyabonetse.", "error")
        return redirect(url_for("admin.manage_guides"))

    # Kugenzura niba ayo mabwiriza agifite intambwe zo guhinga
    has_steps = GuideStep.query.filter_by(
        guide_id=guide_id
    ).first()

    if has_steps:
        flash(
            "Aya mabwiriza ntashobora gusibwa kuko agifite intambwe zo guhinga. "
            "Banza usibe intambwe zose ziyagize.",
            "error"
        )
        return redirect(url_for("admin.manage_guides"))

    # Gusiba amabwiriza hakoreshejwe helper dusanzwe dufite
    deleted = delete_record(GrowingGuide, guide_id)

    if deleted:
        flash("Amabwiriza yo guhinga yasibwe neza.", "success")
    else:
        flash("Amabwiriza yo guhinga ntiyabonetse.", "error")

    return redirect(url_for("admin.manage_guides"))






# ============================================================
# EDIT DISTRICT VARIETY
# ============================================================
@admin_bp.route(
    "/admin/district-varieties/<district_id>/<variety_id>/edit",
    methods=["GET", "POST"]
)
def edit_district_variety(district_id, variety_id):
    # Kugenzura niba umuyobozi yinjiye muri sisitemu
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login"))

    # Gushaka assignment hakoreshejwe ID zombi
    assignment = DistrictVariety.query.filter_by(
        district_id=district_id,
        variety_id=variety_id
    ).first()

    if assignment is None:
        flash("Aya makuru ntiyabonetse.", "error")
        return redirect(url_for("admin.manage_district_varieties"))

    districts = District.query.order_by(
        District.district_name
    ).all()

    varieties = Variety.query.order_by(
        Variety.variety_name
    ).all()

    if request.method == "POST":
        new_district_id = request.form.get(
            "district_id", ""
        ).strip()

        new_variety_id = request.form.get(
            "variety_id", ""
        ).strip()

        suitability_status = request.form.get(
            "suitability_status", ""
        ).strip()

        evidence_source = request.form.get(
            "evidence_source", ""
        ).strip()

        allowed_statuses = {
            "Suitable",
            "Not Suitable",
            "Under Evaluation"
        }

        if (
            not new_district_id
            or not new_variety_id
            or suitability_status not in allowed_statuses
        ):
            flash("Uzuza imyanya isabwa neza.", "error")

        elif (
            db.session.get(District, new_district_id) is None
            or db.session.get(Variety, new_variety_id) is None
        ):
            flash("Akarere cyangwa ubwoko wahisemo ntikabonetse.", "error")

        else:
            # Kwirinda gusubiramo district-variety assignment
            duplicate = DistrictVariety.query.filter_by(
                district_id=new_district_id,
                variety_id=new_variety_id
            ).first()

            same_assignment = (
                new_district_id == assignment.district_id
                and new_variety_id == assignment.variety_id
            )

            if duplicate is not None and not same_assignment:
                flash(
                    "Ubu bwoko busanzwe bufitanye isano n'aka karere.",
                    "error"
                )

            else:
                # Guhindura amakuru y'iyi assignment
                assignment.district_id = new_district_id
                assignment.variety_id = new_variety_id
                assignment.suitability_status = suitability_status
                assignment.evidence_source = evidence_source or None

                db.session.commit()

                flash("Amakuru yahinduwe neza.", "success")
                return redirect(
                    url_for("admin.manage_district_varieties")
                )

    return render_template(
        "edit_district_variety.html",
        assignment=assignment,
        districts=districts,
        varieties=varieties
    )

    
# ============================================================
# DELETE DISTRICT VARIETY
# ============================================================
@admin_bp.route(
    "/admin/district-varieties/<district_id>/<variety_id>/delete",
    methods=["POST"]
)
def delete_district_variety(district_id, variety_id):
    # Kugenzura niba umuyobozi yinjiye muri sisitemu
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login"))

    # Gushaka assignment hakoreshejwe ID zombi
    assignment = DistrictVariety.query.filter_by(
        district_id=district_id,
        variety_id=variety_id
    ).first()

    if assignment is None:
        flash("Aya makuru ntiyabonetse.", "error")
    else:
        db.session.delete(assignment)
        db.session.commit()

        flash("Aya makuru yasibwe neza.", "success")

    return redirect(
        url_for("admin.manage_district_varieties")
    )


# ============================================================
# SHARED HELPERS FOR EDITING AND DELETING RECORDS
# ============================================================

def require_admin():
    """Return True when an administrator is logged in."""
    return bool(session.get("admin_id"))


def safe_delete(model, record_id, return_endpoint):
    """
    Delete a record only when it exists.
    Protect related records by rolling back failed deletions.
    """
    if not require_admin():
        return redirect(url_for("admin.admin_login"))

    record = db.session.get(model, record_id)

    if record is None:
        flash("Amakuru wasabye ntiyabonetse.", "error")
        return redirect(url_for(return_endpoint))

    try:
        db.session.delete(record)
        db.session.commit()
        flash("Amakuru yasibwe neza.", "success")

    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "Record deletion failed for %s", model.__name__
        )
        flash(
            "Aya makuru ntashobora gusibwa kuko ashobora kuba agifitanye "
            "isano n'andi makuru muri sisitemu.",
            "error"
        )

    return redirect(url_for(return_endpoint))


# ============================================================
# EDIT CROP
# ============================================================

@admin_bp.route(
    "/admin/crops/<string:crop_id>/edit",
    methods=["GET", "POST"]
)
def edit_crop(crop_id):
    if not require_admin():
        return redirect(url_for("admin.admin_login"))

    crop = db.session.get(Crop, crop_id)

    if crop is None:
        flash("Igihingwa nti cyabonetse.", "error")
        return redirect(url_for("admin.manage_crops"))

    if request.method == "POST":
        crop_name = request.form.get("crop_name", "").strip()

        if not crop_name:
            flash("Andika izina ry'igihingwa.", "error")
        else:
            crop.crop_name = crop_name

            try:
                db.session.commit()
                flash("Igihingwa cyahinduwe neza.", "success")
                return redirect(url_for("admin.manage_crops"))
            except Exception:
                db.session.rollback()
                current_app.logger.exception("Crop update failed.")
                flash("Ntibyashobotse guhindura igihingwa.", "error")

    return render_template("edit_crop.html", crop=crop)


# ============================================================
# DELETE CROP
# ============================================================

@admin_bp.route(
    "/admin/crops/<string:crop_id>/delete",
    methods=["POST"]
)
def delete_crop(crop_id):
    return safe_delete(Crop, crop_id, "admin.manage_crops")


# ============================================================
# EDIT VARIETY
# ============================================================

@admin_bp.route(
    "/admin/varieties/<string:variety_id>/edit",
    methods=["GET", "POST"]
)
def edit_variety(variety_id):
    if not require_admin():
        return redirect(url_for("admin.admin_login"))

    variety = db.session.get(Variety, variety_id)

    if variety is None:
        flash("Ubwoko bw'igihingwa ntibubonetse.", "error")
        return redirect(url_for("admin.manage_varieties"))

    crops = Crop.query.order_by(Crop.crop_name).all()

    if request.method == "POST":
        crop_id = request.form.get("crop_id", "").strip()
        variety_name = request.form.get("variety_name", "").strip()
        description = request.form.get("description", "").strip()

        crop = db.session.get(Crop, crop_id)

        if not crop_id or not variety_name:
            flash("Uzuza imyanya isabwa.", "error")
        elif crop is None:
            flash("Igihingwa wahisemo nticyabonetse.", "error")
        else:
            variety.crop_id = crop_id
            variety.variety_name = variety_name
            variety.description = description or None

            try:
                db.session.commit()
                flash("Ubwoko bw'igihingwa bwahinduwe neza.", "success")
                return redirect(url_for("admin.manage_varieties"))
            except Exception:
                db.session.rollback()
                current_app.logger.exception("Variety update failed.")
                flash("Ntibyashobotse guhindura ubu bwoko.", "error")

    return render_template(
        "edit_variety.html",
        variety=variety,
        crops=crops
    )


# ============================================================
# DELETE VARIETY
# ============================================================

@admin_bp.route(
    "/admin/varieties/<string:variety_id>/delete",
    methods=["POST"]
)
def delete_variety(variety_id):
    return safe_delete(Variety, variety_id, "admin.manage_varieties")


# ============================================================
# EDIT DISTRICT
# ============================================================

@admin_bp.route(
    "/admin/districts/<string:district_id>/edit",
    methods=["GET", "POST"]
)
def edit_district(district_id):
    if not require_admin():
        return redirect(url_for("admin.admin_login"))

    district = db.session.get(District, district_id)

    if district is None:
        flash("Akarere ntikabonetse.", "error")
        return redirect(url_for("admin.manage_districts"))

    if request.method == "POST":
        district_name = request.form.get("district_name", "").strip()

        if not district_name:
            flash("Andika izina ry'akarere.", "error")
        else:
            district.district_name = district_name

            try:
                db.session.commit()
                flash("Akarere kahinduwe neza.", "success")
                return redirect(url_for("admin.manage_districts"))
            except Exception:
                db.session.rollback()
                current_app.logger.exception("District update failed.")
                flash("Ntibyashobotse guhindura akarere.", "error")

    return render_template("edit_district.html", district=district)


# ============================================================
# DELETE DISTRICT
# ============================================================

@admin_bp.route(
    "/admin/districts/<string:district_id>/delete",
    methods=["POST"]
)
def delete_district(district_id):
    return safe_delete(District, district_id, "admin.manage_districts")


# ============================================================
# EDIT SECTOR
# ============================================================

@admin_bp.route(
    "/admin/sectors/<string:sector_id>/edit",
    methods=["GET", "POST"]
)
def edit_sector(sector_id):
    if not require_admin():
        return redirect(url_for("admin.admin_login"))

    sector = db.session.get(Sector, sector_id)

    if sector is None:
        flash("Umurenge ntiwabonetse.", "error")
        return redirect(url_for("admin.manage_sectors"))

    districts = District.query.order_by(District.district_name).all()

    if request.method == "POST":
        sector_name = request.form.get("sector_name", "").strip()
        district_id = request.form.get("district_id", "").strip()

        district = db.session.get(District, district_id)

        if not sector_name or not district_id:
            flash("Uzuza imyanya isabwa.", "error")
        elif district is None:
            flash("Akarere wahisemo ntikabonetse.", "error")
        else:
            sector.sector_name = sector_name
            sector.district_id = district_id

            try:
                db.session.commit()
                flash("Umurenge wahinduwe neza.", "success")
                return redirect(url_for("admin.manage_sectors"))
            except Exception:
                db.session.rollback()
                current_app.logger.exception("Sector update failed.")
                flash("Ntibyashobotse guhindura umurenge.", "error")

    return render_template(
        "edit_sector.html",
        sector=sector,
        districts=districts
    )


# ============================================================
# DELETE SECTOR
# ============================================================

@admin_bp.route(
    "/admin/sectors/<string:sector_id>/delete",
    methods=["POST"]
)
def delete_sector(sector_id):
    return safe_delete(Sector, sector_id, "admin.manage_sectors")


# ============================================================
# EDIT SUPPLIER
# ============================================================

@admin_bp.route(
    "/admin/suppliers/<string:supplier_id>/edit",
    methods=["GET", "POST"]
)
def edit_supplier(supplier_id):
    if not require_admin():
        return redirect(url_for("admin.admin_login"))

    supplier = db.session.get(Supplier, supplier_id)

    if supplier is None:
        flash("Umutanga imbuto ntiyabonetse.", "error")
        return redirect(url_for("admin.manage_suppliers"))

    sectors = Sector.query.order_by(Sector.sector_name).all()

    if request.method == "POST":
        supplier_name = request.form.get("supplier_name", "").strip()
        phone = request.form.get("phone", "").strip()
        sector_id = request.form.get("sector_id", "").strip()

        sector = db.session.get(Sector, sector_id)

        if not supplier_name or not phone or not sector_id:
            flash("Uzuza imyanya isabwa.", "error")
        elif sector is None:
            flash("Umurenge wahisemo ntubonetse.", "error")
        else:
            supplier.supplier_name = supplier_name
            supplier.phone = phone
            supplier.sector_id = sector_id

            try:
                db.session.commit()
                flash("Umutanga imbuto yahinduwe neza.", "success")
                return redirect(url_for("admin.manage_suppliers"))
            except Exception:
                db.session.rollback()
                current_app.logger.exception("Supplier update failed.")
                flash("Ntibyashobotse guhindura amakuru.", "error")

    return render_template(
        "edit_supplier.html",
        supplier=supplier,
        sectors=sectors
    )


# ============================================================
# DELETE SUPPLIER
# ============================================================

@admin_bp.route(
    "/admin/suppliers/<string:supplier_id>/delete",
    methods=["POST"]
)
def delete_supplier(supplier_id):
    return safe_delete(Supplier, supplier_id, "admin.manage_suppliers")


# ============================================================
# EDIT GROWING GUIDE
# ============================================================

@admin_bp.route(
    "/admin/guides/<int:guide_id>/edit",
    methods=["GET", "POST"]
)
def edit_guide(guide_id):
    if not require_admin():
        return redirect(url_for("admin.admin_login"))

    guide = db.session.get(GrowingGuide, guide_id)

    if guide is None:
        flash("Amabwiriza yo guhinga ntiyabonetse.", "error")
        return redirect(url_for("admin.manage_guides"))

    districts = District.query.order_by(District.district_name).all()
    varieties = Variety.query.order_by(Variety.variety_name).all()

    if request.method == "POST":
        district_id = request.form.get("district_id", "").strip()
        variety_id = request.form.get("variety_id", "").strip()
        introduction = request.form.get("introduction", "").strip()

        district = db.session.get(District, district_id)
        variety = db.session.get(Variety, variety_id)

        if not district_id or not variety_id or not introduction:
            flash("Uzuza imyanya isabwa.", "error")
        elif district is None or variety is None:
            flash("Akarere cyangwa ubwoko wahisemo ntibubonetse.", "error")
        else:
            guide.district_id = district_id
            guide.variety_id = variety_id
            guide.introduction = introduction

            try:
                db.session.commit()
                flash("Amabwiriza yahinduwe neza.", "success")
                return redirect(url_for("admin.manage_guides"))
            except Exception:
                db.session.rollback()
                current_app.logger.exception("Guide update failed.")
                flash("Ntibyashobotse guhindura amabwiriza.", "error")

    return render_template(
        "edit_guide.html",
        guide=guide,
        districts=districts,
        varieties=varieties
    )
