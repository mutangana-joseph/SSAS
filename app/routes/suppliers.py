
from flask import Blueprint, render_template, request, abort

from app.extensions import db
from app.models.crop import Crop
from app.models.variety import Variety
from app.models.district import District
from app.models.sector import Sector
from app.models.district_variety import DistrictVariety
from app.models.supplier import Supplier
from app.models.supplier_variety import SupplierVariety

suppliers_bp = Blueprint("suppliers", __name__,url_prefix="/ssas")


@suppliers_bp.route("/varieties/<variety_id>/suppliers")
def supplier_varieties(variety_id):

    # 1. Find the selected variety
    variety = db.session.get(Variety, variety_id)

    if variety is None:
        abort(404)

    # 2. Find the crop belonging to this variety
    crop = db.session.get(Crop, variety.crop_id)

    # 3. Read the selected district and sector
    selected_district_id = request.args.get(
        "district_id", ""
    ).strip()

    selected_sector_id = request.args.get(
        "sector_id", ""
    ).strip()

    # 4. Fetch districts for the dropdown
    districts = District.query.order_by(
        District.district_name
    ).all()

    selected_district = None
    sectors = []
    suppliers = []

    # 5. Validate the selected district
    if selected_district_id:

        selected_district = db.session.get(
            District, selected_district_id
        )

        if selected_district is None:
            abort(404)

        # Only show sectors belonging to this district
        sectors = Sector.query.filter_by(
            district_id=selected_district_id
        ).order_by(Sector.sector_name).all()

        # 6. Validate the selected sector
        if selected_sector_id:

            selected_sector = db.session.get(
                Sector, selected_sector_id
            )

            if (
                selected_sector is None
                or selected_sector.district_id
                != selected_district_id
            ):
                abort(404)

            # 7. Find suppliers connected to this variety
            #    AND associated with the selected district
            #    AND physically located in the selected sector

            suppliers = (
                db.session.query(
                    Supplier,
                    SupplierVariety.availability,
                    Sector.sector_name
                )
                .join(
                    Sector,
                    Supplier.sector_id == Sector.sector_id
                )
                .join(
                    SupplierVariety,
                    Supplier.supplier_id
                    == SupplierVariety.supplier_id
                )
                .join(
                    DistrictVariety,
                    DistrictVariety.variety_id
                    == SupplierVariety.variety_id
                )
                .filter(
                    SupplierVariety.variety_id == variety_id,
                    DistrictVariety.district_id
                    == selected_district_id,
                    Supplier.sector_id == selected_sector_id,
                    SupplierVariety.availability.is_(True)
                )
                .order_by(Supplier.supplier_name)
                .all()
            )

    return render_template(
        "supplier_varieties.html",
        variety=variety,
        crop=crop,
        variety_id=variety_id,
        districts=districts,
        sectors=sectors,
        suppliers=suppliers,
        selected_district_id=selected_district_id,
        selected_sector_id=selected_sector_id,
        selected_district=selected_district
    )
