import json

import frappe
from field_force.response import build_custom_response
from field_force.api_methods.utils import file_path


@frappe.whitelist()
def get_distributors(**kwargs):
    doctype = 'Distributor'
    api_response_fields = json.loads(open(file_path, "r").read())
    fields = api_response_fields.get(doctype, ['name'])

    frappe.local.form_dict.setdefault(
        "limit_page_length",
        frappe.local.form_dict.limit or frappe.local.form_dict.limit_page_length or 500,
    )

    if 'cmd' in frappe.local.form_dict.keys():
        del frappe.local.form_dict['cmd']

    if frappe.has_permission(doctype, 'read'):
        distributors = frappe.db.get_list(doctype, fields=fields, **frappe.local.form_dict)
        frappe.local.response.total_items = len(distributors)
        frappe.local.response.data = distributors
    else:
        frappe.local.response.http_status_code =  403
        frappe.local.response.message = 'Permission Denied'

    return build_custom_response(response_type='custom')
