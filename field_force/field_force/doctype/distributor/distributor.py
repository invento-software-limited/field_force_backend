# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Distributor(Document):

	def validate(self):
		if not self.customer and frappe.db.exists('Warehouse', self.distributor_name):
			frappe.throw(f"Warehouse with name '{self.distributor_name}' already exists!")
		elif not self.warehouse and frappe.db.exists('Customer', self.distributor_name):
			frappe.throw(f"Customer with name '{self.distributor_name}' already exists!")
		elif not self.customer and not self.warehouse:
			customer = {
				'doctype': 'Customer',
				'customer_name': self.distributor_name,
				'customer_group': 'Distributor',
				'contact_person': self.contact_person,
				'contact_number': self.contact_number,
				'address': self.address,
				'email_address': self.email_address,
				'thana': self.thana,
				'zip_code': self.zip_code,
				'latitude': self.latitude,
				'longitude': self.longitude
			}
			customer = frappe.get_doc(customer)
			customer.insert()
			self.customer = customer.name

			warehouse = {
				'doctype': 'Warehouse',
				'warehouse_name': self.distributor_name
			}
			warehouse = frappe.get_doc(warehouse)
			warehouse.insert()
			self.warehouse = warehouse.name

		else:
			customer_info = {
				'contact_person': self.contact_person,
				'contact_number': self.contact_number,
				'address': self.address,
				'email_address': self.email_address,
				'thana': self.thana,
				'zip_code': self.zip_code,
				'latitude': self.latitude,
				'longitude': self.longitude
			}

			customer = frappe.get_doc('Customer', self.name)
			customer.update(customer_info)
			customer.save()
