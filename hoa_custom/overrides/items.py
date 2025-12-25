import frappe

def autoname_item(doc, method=None):
    if doc.name and not doc.__islocal:
        return

    # Mandatory checks
    if not doc.item_group or not doc.department_name or not doc.custom_company:
        frappe.throw("Item Group, Department and Company are required")

    # Item Group Abbreviation
    item_group_abbr = frappe.db.get_value(
        "Item Group",
        doc.item_group,
        "custom_item_group_abbr"
    )

    if not item_group_abbr:
        frappe.throw(f"Item Group Abbreviation not set for {doc.item_group}")

    # Department Abbreviation (CORRECT FIELD)
    department_abbr = frappe.db.get_value(
        "Item Department",
        {"name": doc.department_name},
        "department_abbr"
    )

    if not department_abbr:
        frappe.throw("Department Abbreviation not found")

    # Company Abbreviation
    company_abbr = frappe.db.get_value(
        "Company",
        {"company_name": doc.custom_company},
        "abbr"
    )

    if not company_abbr:
        frappe.throw("Company abbreviation not found")

    # Final Item Code
    doc.name = f"{company_abbr}-{item_group_abbr}-{department_abbr}-{frappe.generate_hash(length=4).upper()}"
