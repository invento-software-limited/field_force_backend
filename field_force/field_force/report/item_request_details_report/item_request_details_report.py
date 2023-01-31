# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import re

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)

    # for item_request in data:
    #     if item_request.user:
    #         title = item_request.user_fullname or item_request.user
    #         item_request['user'] = f'<a href="/app/user/{item_request.user}" target="_blank">{title}</a>'

    return columns, data

def get_columns(filters):
    """ Columns of Report Table"""

    columns = [
        {"label": _("Date"), "fieldname": "date", "width": 100},
        {"label": _("ID"), "fieldname": "name", "fieldtype": "Link", "options":"Item Request", "width": 130},
        {"label": _("Distributor"), "fieldname": "distributor", "fieldtype": "Link", "options":"Distributor", "width": 140},
        {"label": _("Customer"), "fieldname": "customer", "width": 200, "fieldtype": "Link", "options":"Customer"},
        {"label": _("Address"), "fieldname": "address", "width": 100},
        {"label": _("Contact"), "fieldname": "contact_number", "width": 100},
        {"label": _("Item Details"), "fieldname": "item_details", "width": 300},
        {"label": _("Sales Person"), "fieldname": "sales_person", "fieldtype": "Link", "options":"Sales Person", "width": 140},
    ]

    return columns

def get_data(filters):
    conditions = get_conditions(filters)

    query_string = '''select 
                            item_request.date,
                            item_request.name,
                            item_request.sales_person,
                            item_request.user_fullname, 
                            item_request.customer,
                            item_request.contact_number,
                            item_request.address, 
                            item_request.distributor,
                            item_request.item_details
                        from `tabItem Request` item_request
                        where %s 
                        order by item_request.date desc''' % conditions

    query_result = frappe.db.sql(query_string, as_dict=1, debug=0)
    return query_result


def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    distributor = filters.get('distributor')
    customer = filters.get('customer')
    sales_person = filters.get('sales_person')
    conditions = []

    if from_date:
        conditions.append('item_request.date >= "%s"' % from_date)
    if to_date:
        conditions.append('item_request.date <= "%s"' % to_date)
    if distributor:
        conditions.append('item_request.distributor = "%s"' % distributor)
    if customer:
        conditions.append('item_request.customer = "%s"' % customer)
    if sales_person:
        conditions.append('item_request.sales_person = "%s"' % sales_person)

    return " and ".join(conditions)