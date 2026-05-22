import json

import frappe

# Maps the table name sent from the JS to the actual MariaDB table name.
# All values are hardcoded -- never derived from user input.
_TABLE_MAP = {
	"Purchase Order Item": "`tabPurchase Order Item`",
	"Purchase Invoice Item": "`tabPurchase Invoice Item`",
	"Purchase Receipt Item": "`tabPurchase Receipt Item`",
	"Material Request Item": "`tabMaterial Request Item`",
	"Sales Order Item": "`tabSales Order Item`",
	"Sales Invoice Item": "`tabSales Invoice Item`",
	"Delivery Note Item": "`tabDelivery Note Item`",
	"Stock Entry Detail": "`tabStock Entry Detail`",
	"Stock Ledger Entry": "`tabStock Ledger Entry`",
	"Bin": "`tabBin`",
}

_ALLOWED_ROLES = {"System Manager", "Stock Manager"}


@frappe.whitelist()
def sync_item_names(doctypes):
	if not _ALLOWED_ROLES.intersection(set(frappe.get_roles())):
		frappe.throw(
			"You need the System Manager or Stock Manager role to run Item Name Sync.",
			frappe.PermissionError,
		)

	if isinstance(doctypes, str):
		doctypes = json.loads(doctypes)

	summary = {}
	# Keyed by item_code to deduplicate the same item appearing across multiple tables.
	items_changed = {}

	try:
		for table_key in doctypes:
			sql_table = _TABLE_MAP.get(table_key)
			if not sql_table:
				frappe.log_error(f"Unknown table key received: {table_key}", "Item Name Sync")
				summary[table_key] = 0
				continue

			try:
				# Collect mismatches BEFORE updating so we can report what changed.
				mismatches = frappe.db.sql(
					f"""
					SELECT DISTINCT t.item_code, t.item_name AS old_name, i.item_name AS new_name
					FROM {sql_table} t
					INNER JOIN `tabItem` i ON t.item_code = i.item_code
					WHERE t.item_name != i.item_name
					   OR t.item_name IS NULL
					""",
					as_dict=True,
				)
				for row in mismatches:
					if row.item_code not in items_changed:
						items_changed[row.item_code] = {
							"item_code": row.item_code,
							"old_name": row.old_name or "",
							"new_name": row.new_name,
						}

				# Single bulk UPDATE via JOIN.
				frappe.db.sql(
					f"""
					UPDATE {sql_table} t
					INNER JOIN `tabItem` i ON t.item_code = i.item_code
					SET t.item_name = i.item_name
					WHERE t.item_name != i.item_name
					   OR t.item_name IS NULL
					"""
				)
				row_count = frappe.db.sql("SELECT ROW_COUNT()")[0][0]
				summary[table_key] = int(row_count)
			except Exception:
				frappe.log_error(frappe.get_traceback(), f"Item Name Sync -- {table_key}")
				summary[table_key] = 0

		frappe.db.commit()

	except Exception:
		frappe.log_error(frappe.get_traceback(), "Item Name Sync -- Fatal")
		frappe.throw("An error occurred during sync. Check the Error Log for details.")

	return {
		"summary": summary,
		"items_changed": sorted(items_changed.values(), key=lambda x: x["item_code"]),
	}