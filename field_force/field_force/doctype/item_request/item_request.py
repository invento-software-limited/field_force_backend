# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ItemRequest(Document):
	def validate(self):
		if not self.user:
			self.user = frappe.session.user
			self.user_fullname = frappe.db.get_value('User', self.user, 'full_name')

		self.set_sales_person()
		self.set_employee()

	def set_sales_person(self):
		if self.user and not self.sales_person and frappe.db.exists("Sales Person", {"user": self.user}):
			self.sales_person = frappe.db.get_value("Sales Person", {"user": self.user}, "name")

	def set_employee(self):
		if self.owner and not self.employee:
			if frappe.db.exists("Employee", {"user_id": self.owner}):
				employee, employee_name = frappe.db.get_value("Employee", {"user_id": self.owner},
															  ['name', 'employee_name'])
				self.employee = employee
				self.employee_name = employee_name