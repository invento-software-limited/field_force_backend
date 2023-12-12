import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint
from frappe.boot import get_allowed_report_names

ALLOWED_CHILD_DOCTYPES = ["Requisition Item", "Delivery Stop"]

def has_permission(doc, ptype, user):
	roles = frappe.get_roles(user)
	if "System Manager" in roles:
		return True

	if doc.type == "Report":
		if doc.report_name in get_allowed_report_names():
			return True
	else:
		allowed_doctypes = frappe.permissions.get_doctypes_with_read()
		allowed_doctypes.extend(ALLOWED_CHILD_DOCTYPES)

		if doc.document_type in allowed_doctypes:
			return True

	return False

