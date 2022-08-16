import frappe


def get_custom_data(doctype):
    method = {
        'Customer': get_customer_list,
        'Item': get_items_list
    }

    return method[doctype]()

def get_customer_list():
    frappe.local.form_dict['filters'] = [['customer_group', '=', 'Retail Shop']]
    frappe.local.response.total_items = len(frappe.get_list('Customer', frappe.local.form_dict.get('filters')))
    return frappe.call(frappe.client.get_list, 'Customer', **frappe.local.form_dict)


def get_items_list():
    pass