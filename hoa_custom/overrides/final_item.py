import frappe

def autoname_item(doc, method=None):

    if doc.name and not doc.__islocal:
        return

    if not doc.item_group or not doc.department_name or not doc.custom_company:
        frappe.throw("Item Group, Department and Company are required")

    item_group_abbr = frappe.db.get_value(
        "Item Group",
        doc.item_group,
        "custom_item_group_abbr"
    )

    department_abbr = frappe.db.get_value(
        "Item Department",
        doc.department_name,
        "department_abbr"
    )

    company_abbr = frappe.db.get_value(
        "Company",
        {"company_name": doc.custom_company},
        "abbr"
    )

    prefix = f"{item_group_abbr}-{department_abbr}-{company_abbr}"

    # get highest used number safely
    last = frappe.db.sql("""
        SELECT MAX(CAST(SUBSTRING_INDEX(name, '-', -1) AS UNSIGNED))
        FROM tabItem
        WHERE name LIKE %s
    """, (prefix + "-%",))

    next_no = (last[0][0] or 0) + 1

    # collision-safe numbering
    while True:
        code = f"{prefix}-{str(next_no).zfill(3)}"
        if not frappe.db.exists("Item", code):
            break
        next_no += 1

    doc.name = code
    doc.item_code = code
