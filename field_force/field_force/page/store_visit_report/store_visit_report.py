# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt
import json

import frappe
from field_force.field_force.page.utils import *
from field_force.field_force.report.utils import *


@frappe.whitelist()
def execute(filters=None):
    columns = get_columns()
    filters = json.loads(filters)
    data = get_absolute_data(filters)
    # print(data)
    return data, columns

def get_absolute_data(filters, export=False):
    data = get_query_data(filters)
    site_directory = get_site_directory_path()
    data_dict = {}
    index = 1

    for store_visit in data:
        set_image_url(store_visit, site_directory)
        data_key = f"{store_visit.server_date}_{store_visit.customer}_{store_visit.sales_person}"
        store_visit.cheated = 'Yes' if store_visit.cheated else 'No'

        if data_key not in data_dict.keys():
            store_visit.date = frappe.format_value(store_visit.server_date, 'Date')
            data_dict[data_key] = store_visit

            # data_dict[data_key]['checkin_time_'] = store_visit.server_time
            checkin_time = get_time_in_12_hour_format(store_visit.server_time)

            data_dict[data_key]['checkin_name'] = store_visit.name
            data_dict[data_key]['checkin_image'] = store_visit.image
            data_dict[data_key]['checkout_image'] = '/files/default-image.png'

            if export:
                store_visit.user = store_visit.user_fullname or store_visit.user
                data_dict[data_key]['checkin_time'] = checkin_time
            else:
                set_link_to_doc(store_visit, 'sales_person', 'sales-person')
                set_link_to_doc(store_visit, 'customer', 'customer')
                data_dict[data_key]['checkin_time'] = get_doc_url('store-visit', store_visit.name, checkin_time)

            index += 1
        else:
            checkout_time = get_time_in_12_hour_format(store_visit.server_time)
            data_dict[data_key]['spent_time'] = get_spent_time(data_dict[data_key].server_time, store_visit.server_time)

            data_dict[data_key]['checkout_name'] = store_visit.name
            data_dict[data_key]['checkout_image'] = store_visit.image

            if export:
                data_dict[data_key]['checkout_time'] = checkout_time
            else:
                data_dict[data_key]['checkout_time'] = get_doc_url('store-visit', store_visit.name, checkout_time)

    if data_dict.values():
        return list(data_dict.values())[::-1]

    return []

def get_query_data(filters):
    conditions = get_conditions(filters)

    base_query = '''select store_visit.name, store_visit.user, store_visit.user_fullname,
                    store_visit.server_date, store_visit.server_time, store_visit.device_time,
                    store_visit.type, store_visit.image, store_visit.cheated, store_visit.customer,
                    store_visit.sales_person, store_visit.latitude, store_visit.longitude
                    from `tabStore Visit` store_visit where %s order by store_visit.server_date,
                    store_visit.server_time''' % conditions

    query_result = frappe.db.sql(base_query, as_dict=1, debug=0)
    return query_result


def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    sales_person = filters.get('sales_person')
    customer = filters.get('customer')

    conditions = []

    if from_date:
        conditions.append('store_visit.server_date >= "%s"' % from_date)
    if to_date:
        conditions.append('store_visit.server_date <= "%s"' % to_date)
    if sales_person:
        conditions.append('store_visit.sales_person = "%s"' % sales_person)
    if customer:
        conditions.append('store_visit.customer = "%s"' % customer)

    return " and ".join(conditions)

def get_columns():
    columns =  [
        {'fieldname': 'sl', 'label': 'SL', 'width':30, 'expwidth': 5, 'export': False},
        {'fieldname': 'date', 'label': 'Date', 'width': 120, 'expwidth': 13},
        {'fieldname': 'sales_person', 'label': 'Sales Person', 'width': 220, 'expwidth': 25},
        {'fieldname': 'customer', 'label': 'Customer', 'width': 270, 'expwidth': 35},
        {'fieldname': 'checkin_time', 'label': 'IN Time', 'width': 120, 'expwidth': 15},
        {'fieldname': 'checkout_time', 'label': 'OUT Time', 'width': 120, 'expwidth': 15},
        {'fieldname': 'spent_time', 'label': 'Spent Time', 'width': 130, 'expwidth': 15},
        {'fieldname': 'cheated', 'label': 'Cheated', 'fieldtype': 'Data', 'width': 100, 'expwidth': 15},
        {'fieldname': 'checkin_image', 'label': 'IN Image', 'fieldtype': 'Image', 'width': 120, 'expwidth': 15, 'export': False},
        {'fieldname': 'checkout_image', 'label': 'OUT Image', 'fieldtype': 'Image', 'width': 120, 'expwidth': 15, 'export': False},
    ]
    return columns

@frappe.whitelist()
def export_file(**filters):
    columns = get_columns()
    data = get_export_data(filters)
    file_name = 'Store_Visit_Report.xlsx'
    generate_excel_and_download(columns, data, file_name, height=20)

def get_export_data(filters):
    query_result = get_absolute_data(filters, export=True)
    return query_result
