import frappe

# All tables that carry item_name alongside item_code.
_TABLES = [
	"`tabPurchase Order Item`",
	"`tabPurchase Invoice Item`",
	"`tabPurchase Receipt Item`",
	"`tabMaterial Request Item`",
	"`tabSales Order Item`",
	"`tabSales Invoice Item`",
	"`tabDelivery Note Item`",
	"`tabStock Entry Detail`",
	"`tabStock Ledger Entry`",
	"`tabBin`",
]


def on_item_update(doc, method=None):
	"""Keeps item_name in sync across all transaction tables whenever an Item is saved."""
	for table in _TABLES:
		try:
			frappe.db.sql(
				f"UPDATE {table} SET item_name = %(item_name)s WHERE item_code = %(item_code)s",
				{"item_name": doc.item_name, "item_code": doc.item_code},
			)
		except Exception:
			frappe.log_error(frappe.get_traceback(), f"Item Auto-Sync — {table}")
