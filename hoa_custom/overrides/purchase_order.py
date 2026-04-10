import frappe
from frappe.utils import now_datetime

def set_naming_series(doc, method):
    # Only allow changes in Draft
    if doc.docstatus != 0:
        return

    if not doc.company:
        frappe.throw("Please select Company")

    if not doc.po_type:
        frappe.throw("Please select PO Type")

    # Get company abbreviation
    abbr = frappe.db.get_value("Company", doc.company, "abbr")
    if not abbr:
        frappe.throw("Company abbreviation not found")

    year = now_datetime().year

    # Generate naming series
    if doc.po_type == "Normal Material":
        naming_series = f"{abbr}-MAT-{year}-.####"

    elif doc.po_type == "Subcontracting/Works":
        naming_series = f"{abbr}-SBC-{year}-.####"
        doc.is_subcontracted = 1

    elif doc.po_type == "Machinery Rentals":
        naming_series = f"{abbr}-MAC-{year}-.####"
        doc.is_subcontracted = 0

    else:
        return

    # Always update naming series if changed
    if doc.naming_series != naming_series:
        doc.naming_series = naming_series

        # Reset name only if still draft (so new series applies)
        doc.name = None