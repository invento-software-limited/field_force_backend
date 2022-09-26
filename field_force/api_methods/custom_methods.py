import json

import frappe
from field_force.api_methods.utils import file_path, get_api_fields


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
    _, child_table_fields = get_api_fields('Item', with_child_fields=True)

    # retrieving items
    items = frappe.call(frappe.client.get_list, 'Item', **frappe.local.form_dict)
    frappe.local.response.total_items = len(frappe.get_list('Item', frappe.local.form_dict.get('filters')))

    items_dict = {}
    item_names = ''

    for item in items:
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


