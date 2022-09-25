# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ItemRequest(Document):
	def validate(self):
		if not self.user:
			self.user = frappe.session.user
			self.user_fullname = frappe.db.get_value('User', self.user, 'full_name')
