#rejected_item_purchase_receipt
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
    dt = "Purchase Receipt Item"
    fields = [
        {
            "label": "Balance Quantity",
            "fieldname": "balance_quantity",
            "fieldtype": "Float",
            "reqd": 0,
            "insert_after": "rejected_qty",
            "in_list_view": 1,
            "read_only": 1
        },
        {
            "label": "Reason for Rejection",
            "fieldname": "reason_for_rejection",
            "fieldtype": "Small Text",
            "reqd": 0,
            "insert_after": "balance_qty",
            "in_list_view": 1
        },
        {
            "label": "Rejection Photo",
            "fieldname": "rejection_photo",
            "fieldtype": "Attach Image",
            "reqd": 0,
            "insert_after": "reason_for_rejection",
            "in_list_view": 1
        }
    ]

    for f in fields:
        create_custom_field(dt, f)
