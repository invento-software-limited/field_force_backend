# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class StoreVisitAssign(Document):
	def validate(self):
		if frappe.db.exists('Store Visit Assign', {'employee': self.employee, 'date': self.date}):
			frappe.throw(f"Store Visit is already assigned for employee '{self.employee}' at '{self.date}'")

		if self.destinations:
			for destination in self.destinations:
				destination.employee = self.employee
				destination.date = self.date
