# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)

    for item_request in data:
        if item_request.user:
            title = item_request.user_fullname or item_request.user
            item_request['user'] = f'<a href="/app/user/{item_request.user}" target="_blank">{title}</a>'

    return columns, data

def get_columns(filters):
    """ Columns of Report Table"""

    columns = [
        {"label": _("Date"), "fieldname": "date", "width": 120},
        {"label": _("Name"), "fieldname": "name", "fieldtype": "Link", "options":"Item Request", "width": 150},
        {"label": _("User"), "fieldname": "user", "width": 140},
        {"label": _("Customer"), "fieldname": "customer", "width": 150, "fieldtype": "Link", "options":"Customer"},
        {"label": _("Address"), "fieldname": "address", "width": 150},
        {"label": _("Contact Number"), "fieldname": "contact_number", "width": 150},
        {"label": _("Distributor"), "fieldname": "distributor", "width": 150},
        {"label": _("Item Details"), "fieldname": "item_details", "width": 200},
	]

    return columns

def get_data(filters):
    conditions = get_conditions(filters)

    query_string = """select item_request.date, item_request.name, item_request.user, item_request.user_fullname, 
                    item_request.customer, item_request.contact_number, item_request.address, item_request.distributor,
                    item_request.item_details
                    from `tabItem Request` item_request where %s order by item_request.date desc""" % conditions

    query_result = frappe.db.sql(query_string, as_dict=1, debug=0)
    return query_result


def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    user = filters.get('user')
    customer = filters.get('customer')

    conditions = []

    if from_date:
        conditions.append("item_request.date >= '%s'" % from_date)
    if to_date:
        conditions.append("item_request.date <= '%s'" % to_date)
    if user:
        conditions.append("item_request.user = '%s'" % user)
    if customer:
        conditions.append("item_request.customer = '%s'" % customer)

    return " and ".join(conditions)