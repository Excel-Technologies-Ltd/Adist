
import frappe


def save_number_card_date():
	"""Save A/C Receivables and A/C Payables Number Cards daily at 12:05 AM."""
	cards = ["A/C Receivables", "A/C Payables"]

	for card_name in cards:
		try:
			doc = frappe.get_doc("Number Card", card_name)
			doc.save(ignore_permissions=True)
			frappe.db.commit()
			frappe.logger().info(f"Number Card '{card_name}' saved successfully.")
			print(f"Number Card '{card_name}' saved successfully.")
		except Exception:
			frappe.log_error(frappe.get_traceback(), f"Failed to save Number Card: {card_name}")
			print(f"Failed to save Number Card: {card_name}")