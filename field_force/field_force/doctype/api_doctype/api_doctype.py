# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from field_force.field_force.custom_functions.utils import set_doctype_fields_to_json

class APIDocType(Document):

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)  # call the base save method

		print(self.field_names)
		if self.field_names:
			fields = self.field_names.replace(' ','').split(',')
			valid_fields = []
			invalid_fields = []

			for field in fields:
				filters = {
					'parent': self.name,
					'fieldname': field
				}

				if frappe.db.exists('DocField', filters):
					if field and field not in valid_fields:
						valid_fields.append(field)
				else:
					if field and field not in invalid_fields:
						invalid_fields.append(field)

			if invalid_fields:
				frappe.throw(f"The fields {invalid_fields} are invalid!")

			set_doctype_fields_to_json(self.doc, fields)
