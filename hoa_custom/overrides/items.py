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
    prefix = f"{item_group_abbr}-{department_abbr}-{company_abbr}"

    last = frappe.db.sql(
        """SELECT name FROM tabItem
           WHERE name LIKE %s
           ORDER BY creation DESC LIMIT 1 FOR UPDATE""",
        (prefix + "-%",),
        as_dict=True
    )

    next_no = int(last[0].name.split("-")[-1]) + 1 if last else 1
    code = f"{prefix}-{str(next_no).zfill(3)}"

    doc.name = code
    doc.item_code = code