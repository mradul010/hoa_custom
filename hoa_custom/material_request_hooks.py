import frappe
from frappe.desk.form.assign_to import add as add_assignment


def assign_material_request_on_submit(doc, method=None):
	try:
		settings = frappe.get_single("HOA Custom Settings")
	except frappe.DoesNotExistError:
		return

	if hasattr(settings, "enable_material_request_auto_assignment"):
		if not settings.enable_material_request_auto_assignment:
			return

	assignee = getattr(settings, "default_material_request_assignee", None)
	if not assignee:
		return

	existing = frappe.db.exists(
		"ToDo",
		{
			"reference_type": doc.doctype,
			"reference_name": doc.name,
			"allocated_to": assignee,
			"status": "Open",
		},
	)
	if existing:
		return

	add_assignment(
		{
			"assign_to": [assignee],
			"doctype": doc.doctype,
			"name": doc.name,
			"description": f"Material Request {doc.name} has been submitted and assigned automatically.",
		}
	)
