# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from field_force.field_force.doctype.utils import set_cheat_status, set_location_to_map

class MerchandisingPicture(Document):
	def validate(self):
		# if frappe.session.user != 'administrator':
		# 	self.user = frappe.session.user

		if not self.email or not self.user_fullname:
			email, user_fullname = frappe.db.get_value('User', self.user, ['email', 'full_name'])

			if not self.email and email:
				self.email = email
			if not self.user_fullname and user_fullname:
				self.user_fullname = user_fullname

		if not self.contact_number or not self.customer_address:
			contact_number, customer_address = frappe.db.get_value('Customer', self.customer, ['contact_number', 'address'])

			if not self.contact_number and contact_number:
				self.contact_number = contact_number
			if not self.customer_address and customer_address:
				self.customer_address = customer_address

		set_cheat_status(self)
		self.set_employee()

	def set_employee(self):
		if self.owner and not self.employee:
			if frappe.db.exists("Employee", {"user_id": self.owner}):
				employee, employee_name = frappe.db.get_value("Employee", {"user_id": self.owner},
															  ['name', 'employee_name'])
				self.employee = employee
				self.employee_name = employee_name

	def before_save(self):
		set_location_to_map(self)