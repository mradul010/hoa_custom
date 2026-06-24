from erpnext.stock.doctype.material_request.material_request import (
    make_purchase_order as erpnext_make_purchase_order
)
import frappe


@frappe.whitelist()
def make_purchase_order(source_name, target_doc=None, args=None):
    
    # Generate Purchase Order using standard ERPNext logic
    po = erpnext_make_purchase_order(source_name, target_doc, args)

    # Fetch source Material Request
    mr = frappe.get_doc("Material Request", source_name)

    # Copy attachment from Material Request to Purchase Order
    po.custom_attach_document = mr.custom_attach_document

    # Map Material Request Type of Purchase to Purchase Order Type
    if mr.custom_type_of_purchase == "Material Purchase":
        po.po_type = "Normal Material"
    elif mr.custom_type_of_purchase == "Subcontract / Works Request":
        po.po_type = "Subcontracting/Works"
    elif mr.custom_type_of_purchase == "Machinery Rental":
        po.po_type = "Machinery Rentals"

    # Store Material Request reference in Purchase Order
    po.material_request_ref = mr.name

    # Set Material Request creator as Requested By
    po.requested_by = mr.owner

    # Set current logged-in user as Approved By
    po.approved_by = frappe.session.user

    return po