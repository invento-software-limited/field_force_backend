import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint

@frappe.whitelist()
def get_result(doc, filters, to_date=None):
	doc = frappe.parse_json(doc)
	fields = []
	sql_function_map = {
		"Count": "count",
		"Sum": "sum",
		"Average": "avg",
		"Minimum": "min",
		"Maximum": "max",
	}

	function = sql_function_map[doc.function]

	if function == "count":
		fields = [f"{function}(*) as result"]
	else:
		fields = [
			"{function}({based_on}) as result".format(
				function=function, based_on=doc.aggregate_function_based_on
			)
		]

	if not filters:
		filters = []
	elif isinstance(filters, str):
		filters = frappe.parse_json(filters)

	if to_date:
		filters.append([doc.document_type, "creation", "<", to_date])

	res = frappe.get_all(
		doc.document_type, fields=fields, filters=filters, parent_doctype=doc.parent_document_type
	)
	number = res[0]["result"] if res else 0

	return cint(number)
