# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class APIDocConfig(Document):
	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)

		if self.api_docs:
			for doc in self.api_docs:
				fields = doc.fields.replace(' ', '').split(',')
				valid_fields = []
				invalid_fields = []

				for field in fields:
					filters = {
						'parent': doc.doc,
						'fieldname': field
					}

					if frappe.db.exists('DocField', filters):
						if field and field not in valid_fields:
							valid_fields.append(field)
					else:
						if field and field not in invalid_fields:
							invalid_fields.append(field)

				if invalid_fields:
					frappe.throw(f"The fields {invalid_fields} are not valid!")
