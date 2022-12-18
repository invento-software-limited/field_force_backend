# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AppEndPermission(Document):
	def validate(self):
		if self.permissions:
			for permission in self.permissions:
				permission.doctypes = permission.doctypes.replace(" ", "")

				if self.check_validation:
					if frappe.db.exists('App End Permission Role Profile', {'name':['!=', permission.name],
																			'role_profile': permission.role_profile}):
						frappe.throw(f"App End Permissions already exist for <b>{permission.role_profile}.</b>")

					doctypes = permission.doctypes.split(',')

					for doctype in doctypes:
						doctype = doctype.replace("_", " ")

						if doctype and not frappe.db.exists({"doctype": doctype}):
							frappe.throw(f"<b>{permission.role_profile}:</b> '{doctype}' doctype not found!")
		# else:
		# 	frappe.throw("Must have one role permission")


	# def save(self, *args, **kwargs):
	# 	super().save(*args, **kwargs)
