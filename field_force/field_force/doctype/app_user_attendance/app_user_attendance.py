# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe

from field_force.field_force.doctype.utils import set_cheat_status, set_location_to_map
from frappe.model.document import Document

class AppUserAttendance(Document):
	def validate(self):
	# 	if frappe.session.user != 'administrator':
	# 		self.user = frappe.session.user

		if not self.email or not self.user_fullname:
			email, user_fullname = frappe.db.get_value('User', self.user, ['email', 'full_name'])

			if not self.email and email:
				self.email = email
			if not self.user_fullname and user_fullname:
				self.user_fullname = user_fullname

		set_cheat_status(self)
		self.set_employee()

	def before_save(self):
		set_location_to_map(self)

	def set_employee(self):
		if self.owner and not self.employee:
			if frappe.db.exists("Employee", {"user_id": self.owner}):
				employee, employee_name = frappe.db.get_value("Employee", {"user_id": self.owner},
															  ['name', 'employee_name'])
				self.employee = employee
				self.employee_name = employee_name
