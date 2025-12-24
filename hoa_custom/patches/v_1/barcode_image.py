import frappe

def create_custom_field(dt, field):
    name = f"{dt}-{field['fieldname']}"
    if frappe.db.exists("Custom Field", name):
        print(f"Skip Custom Field {name}")
        return
    cf_doc = {
        "doctype": "Custom Field",
        "dt": dt,
        **field
    }
    try:
        cf = frappe.get_doc(cf_doc)
        cf.insert(ignore_permissions = True)
        frappe.db.commit()
        print(f"[ok] created custom field: {name}")
    except Exception as e:
        print(f"[error] Failed Create {name}: {e}")
        frappe.db.rollback()

def execute():
    dt = 'Item Barcode'
    fields = [
        {
            "label": 'Barcode Image',
            "fieldname": 'barcode_image',
            "fieldtype": 'Attach Image',
            "reqd": 1,
            "insert_after": 'uom',
            "in_list_view": 1
        }
    ]

    for f in fields:
        create_custom_field(dt, f)
