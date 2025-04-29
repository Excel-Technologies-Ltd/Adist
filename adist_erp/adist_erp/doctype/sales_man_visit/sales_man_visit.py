# Copyright (c) 2025, Shaid Azmin and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SalesManVisit(Document):
	def before_save(self):
		if not self.date:
			self.date = frappe.datetime.get_today()
		if not self.time:
			self.time = frappe.datetime.now_datetime()
		if not bool(self.is_set_location):
			frappe.throw("Please enable location permission in your device to set the location")
        
