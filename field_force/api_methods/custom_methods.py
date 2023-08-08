import json

import frappe
from field_force.api_methods.utils import get_api_fields


CUSTOM_API_DOCTYPES = ['Customer', 'Item', 'Store Visit Assign', 'Territory']

def get_custom_data(doctype):
    method = {
        'Customer': get_customer_list,
        'Item': get_items_list,
        'Store Visit Assign': get_store_visit_assigns_list,
        'Territory': get_territories
    }

    return method[doctype](doctype)

def set_custom_data_before_creation(doctype, data):
    submit_on_creation_doctypes = ["Sales Order", "Store Visit Assign"]

    if doctype in submit_on_creation_doctypes:
        data['created_from_app'] = 1

def get_customer_list(doctype):
    if frappe.local.form_dict.get('filters'):
        filters = json.loads(frappe.local.form_dict.get('filters'))
        filters.append(['customer_group', 'in', ['Retail Shop', 'MT']])
    else:
        filters = [['customer_group', 'in', ['Retail Shop', 'MT']]]

    frappe.local.form_dict['filters'] = filters
    customers = frappe.call(frappe.client.get_list, doctype, **frappe.local.form_dict)
    frappe.local.response.total_items = len(customers)
    return customers

def get_items_list(doctype):
    _, child_table_fields = get_api_fields(doctype, with_child_fields=True)

    # retrieving items
    frappe.local.form_dict['filters'] = [['disabled', '=', 0]]
    items = frappe.call(frappe.client.get_list, doctype, **frappe.local.form_dict)
    frappe.local.response.total_items = len(items)

    items_dict = {}
    item_names = ''

    for item in items:
        if 'barcodes' in child_table_fields:
            item['barcodes'] = []

        item['batches'] = []
        items_dict[item.item_code] = item
        item_names += ", " + f"'{item.item_code}'" if item_names else f"'{item.item_code}'"

    if 'barcodes' in child_table_fields:
        # if 'barcodes' in API doc config field list
        barcodes = frappe.db.sql(f"""select barcode.parent, barcode.barcode from `tabItem Barcode` barcode
                                    where barcode.parent in ({item_names})""", as_dict=1)

        for barcode in barcodes:
            items_dict[barcode.parent]['barcodes'].append(barcode.barcode)

    # to send batch data with items
    batch_fields = get_api_fields('Batch')
    batch_fields_str = ",".join([f'batch.{field}' for field in batch_fields])

    batches = frappe.db.sql(f"""select {batch_fields_str} from `tabBatch` batch
                            where batch.item in ({item_names})""", as_dict=True)

    for batch in batches:
        items_dict[batch.item]['batches'].append(batch)

    return items

def get_store_visit_assigns_list(doctype):
    _, child_table_fields = get_api_fields(doctype, with_child_fields=True)

    # frappe.local.form_dict['filters'] = {'user': frappe.session.user}
    store_visit_assigns = frappe.call(frappe.client.get_list, doctype, **frappe.local.form_dict)
    frappe.local.response.total_items = len(store_visit_assigns)

    store_visit_assigns_dict = {}
    store_visit_assign_names = ''

    if store_visit_assigns and 'destinations' in child_table_fields:
        for store_visit_assign in store_visit_assigns:
            store_visit_assign['destinations'] = []

            store_visit_assigns_dict[store_visit_assign.name] = store_visit_assign
            store_visit_assign_names += ", " + f"'{store_visit_assign.name}'" if store_visit_assign_names else f"'{store_visit_assign.name}'"

        child_table_doctype = 'Store Visit Destination'
        store_visit_assign_fields = get_api_fields(child_table_doctype)
        store_visit_assign_fields_str = ",".join([f'store_visit_destination.{field}' for field in store_visit_assign_fields])

        destinations = frappe.db.sql(f"""select store_visit_destination.parent, {store_visit_assign_fields_str}
                                        from `tab{child_table_doctype}` store_visit_destination where
                                        store_visit_destination.parent in ({store_visit_assign_names})
                                        order by store_visit_destination.expected_time, store_visit_destination.idx""", as_dict=True)

        for destination in destinations:
            store_visit_assigns_dict[destination.parent]['destinations'].append(destination)

        return store_visit_assigns_dict.values()

    return store_visit_assigns

def get_territories(doctype):
    sales_person_filters = {
        "user": frappe.session.user,
        "territory": ["!=", None]
    }

    if frappe.db.exists("Sales Person", sales_person_filters):
        territory = frappe.db.get_value("Sales Person", sales_person_filters, 'territory')

        if territory:
            fields = get_api_fields(doctype)
            lft, rgt = frappe.db.get_value("Territory", territory, ['lft', 'rgt'])
            territories = frappe.get_list("Territory", filters={'lft': ['>=', lft], 'rgt': ['<=', rgt]},
                                          fields=fields, order_by='lft')

            frappe.local.response.total_items = len(territories)
            return territories

    return []
