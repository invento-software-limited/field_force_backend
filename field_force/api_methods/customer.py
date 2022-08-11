import json

import frappe
from field_force.response import build_custom_response

@frappe.whitelist()
def get_distributors(**kwargs):
    filters = {
        'customer_group': 'Distributor',
    }

    if kwargs.get('search'):
        filters['customer_name'] = ["like", f"%{kwargs.pop('search')}%"]

    if 'cmd' in kwargs.keys():
        del kwargs['cmd']

    if frappe.has_permission('Customer', 'read'):
        distributors = frappe.db.get_list('Customer', filters, **kwargs)
        frappe.local.response.total_items = len(distributors)
        frappe.local.response.data = distributors
    else:
        frappe.local.response.http_status_code =  403
        frappe.local.response.message = 'Permission Denied'

    return build_custom_response(response_type='custom')