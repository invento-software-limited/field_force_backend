# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from field_force.field_force.doctype.utils import set_location_to_map, set_cheat_status, set_employee, set_sales_person
from frappe.model.document import Document

class StoreVisit(Document):
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

		set_sales_person(self)
		set_employee(self)
		set_cheat_status(self)

	def after_insert(self):
		filters = {
			"customer": self.customer,
			"user": self.user,
			"date": self.server_date
		}

		if frappe.db.exists('Store Visit Destination', filters):
			store_visit_destination = frappe.get_last_doc("Store Visit Destination", filters=filters)
			store_visit_destination.store_visit = self.name
			store_visit_destination.status = 'Visited'
			store_visit_destination.visited_time = self.server_time
			store_visit_destination.save()

	def before_save(self):
		set_location_to_map(self)
