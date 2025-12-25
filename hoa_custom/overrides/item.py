import frappe

def autoname_item(doc, method=None):
    if doc.name:
        return

    if not doc.item_group or not doc.custom_item_department or not doc.custom_company:
        frappe.throw("Item Group and Item Department are required")

    # Item Group Abbreviation
    item_group_abbr = frappe.db.get_value(
        "Item Group",
        doc.item_group,
        "custom_item_group_abbr"
    )

    # Department Abbreviation (SAFE FILTER)
    department_abbr = frappe.db.get_value(
        "Item Department",
        {"name": doc.custom_item_department},
        "department_abbr"
    )

    # Company (Items are global)
    # company = (
    #     frappe.defaults.get_user_default("Company")
    #     or frappe.defaults.get_global_default("company")
    # )

    company_abbr = frappe.db.get_value("Company", {"company_name": doc.custom_company}, "abbr")
    #company_abbr = "HOA"

    if not item_group_abbr:
        frappe.throw("Item Group abbreviation missing")

    if not department_abbr:
        frappe.throw("Department abbreviation missing")

    if not company_abbr:
        frappe.throw("Company abbreviation missing")

    prefix = f"{item_group_abbr}-{department_abbr}-{company_abbr}"

    last_item = frappe.db.sql("""
        SELECT name
        FROM tabItem
        WHERE name LIKE %s
        ORDER BY creation DESC
        LIMIT 1
        FOR UPDATE
    """, (prefix + "-%",), as_dict=True)

    next_number = 1
    if last_item:
        next_number = int(last_item[0].name.split("-")[-1]) + 1

    item_code = f"{prefix}-{str(next_number).zfill(3)}"

    doc.name = item_code
    doc.item_code = item_code
    
