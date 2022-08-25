# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class StoreVisit(Document):
	def after_insert(self):
		filters = {
			"customer": self.customer,
			"employee": self.employee,
			"date": self.device_date
		}

		if frappe.db.exists('Store Visit Destination', filters):
			store_visit_destination = frappe.get_last_doc("Store Visit Destination", filters=filters)
			store_visit_destination.store_visit = self.name
			store_visit_destination.status = 'Visited'
			store_visit_destination.save()
