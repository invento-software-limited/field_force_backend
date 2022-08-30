# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class StoreVisitAssign(Document):
	def validate(self):
		filters = [
			['name', '!=', self.name],
			['employee', '=', self.employee],
			['date', '=', self.date]
		]

		if frappe.db.get_list('Store Visit Assign', filters):
			frappe.throw(f"Store Visit is already assigned for user '{self.user}' at '{self.date}'")

		if self.destinations:
			for destination in self.destinations:
				destination.user = self.user
				destination.date = self.date
