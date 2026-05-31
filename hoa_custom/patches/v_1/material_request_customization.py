import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


MATERIAL_REQUEST_FIELDS = {
	"Material Request": [
		{
			"fieldname": "custom_type_of_purchase",
			"label": "Type of Purchase",
			"fieldtype": "Select",
			"options": "Material Purchase\nMachinery Rental\nSubcontract / Works Request",
			"insert_after": "material_request_type",
		},
		{
			"fieldname": "custom_attach_document",
			"label": "Attach Document",
			"fieldtype": "Attach",
			"insert_after": "custom_type_of_purchase",
		},
		{
			"fieldname": "custom_comment",
			"label": "Comment",
			"fieldtype": "Small Text",
			"insert_after": "custom_attach_document",
		},
		{
			"fieldname": "custom_priority_urgency",
			"label": "Priority / Urgency",
			"fieldtype": "Select",
			"options": "Low\nModerate\nHigh",
			"default": "Moderate",
			"insert_after": "custom_comment",
		},
		{
			"fieldname": "custom_delivery_location",
			"label": "Delivery Location",
			"fieldtype": "Small Text",
			"insert_after": "schedule_date",
		},
	]
}


def execute():
	create_custom_fields(MATERIAL_REQUEST_FIELDS, update=True)
	hide_material_request_price_list()
	frappe.clear_cache(doctype="Material Request")


def hide_material_request_price_list():
	if not frappe.get_meta("Material Request").has_field("buying_price_list"):
		return

	property_setter_name = frappe.db.exists(
		"Property Setter",
		{
			"doc_type": "Material Request",
			"field_name": "buying_price_list",
			"property": "hidden",
		},
	)

	if property_setter_name:
		frappe.db.set_value("Property Setter", property_setter_name, "value", "1")
		frappe.db.set_value("Property Setter", property_setter_name, "property_type", "Check")
		return

	make_property_setter(
		"Material Request",
		"buying_price_list",
		"hidden",
		1,
		"Check",
	)
