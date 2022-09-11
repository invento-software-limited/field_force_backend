# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)

    for store_visit in data:
        if store_visit.user:
            title = store_visit.user_fullname or store_visit.user
            store_visit['user'] = f'<a href="/app/user/{store_visit.user}" target="_blank">{title}</a>'

        if  store_visit.image:
            if '/files/' in store_visit.image:
                store_visit['image'] = f'<a href="{store_visit.image}" target="_blank">{store_visit.image}</a>'

    return columns, data

def get_columns(filters):
    """ Columns of Report Table"""

    columns = [
        {"label": _("Date"), "fieldname": "server_date", "width": 100},
        {"label": _("Time"), "fieldname": "server_time", "fieldtype": "Time", "width": 80},
        {"label": _("Name"), "fieldname": "name", "fieldtype": "Link", "options":"Store Visit", "width": 120},
        {"label": _("User"), "fieldname": "user", "width": 120},
        {"label": _("Customer"), "fieldname": "customer", "width": 120, "fieldtype": "Link", "options":"Customer"},
        {"label": _("Contact Number"), "fieldname": "contact_number", "width": 100},
        {"label": _("Device Date"), "fieldname": "device_date", "fieldtype": "Date", "width": 100},
        {"label": _("Device Time"), "fieldname": "device_time", "fieldtype": "Time", "width": 100},
        {"label": _("Latitude"), "fieldname": "latitude", "width": 125},
        {"label": _("Longitude"), "fieldname": "longitude", "width": 125},
        {"label": _("Device Model"), "fieldname": "device_model", "width": 120},
		{"label": _("Image"), "fieldname": "image", "width": 120},
	]

    return columns

def get_data(filters):
    conditions = get_conditions(filters)

    query_string = """select store_visit.name, store_visit.user, store_visit.user_fullname, store_visit.customer,
                    store_visit.image, store_visit.contact_number, store_visit.server_date, store_visit.server_time,
                    store_visit.device_date, store_visit.device_time, store_visit.latitude, store_visit.longitude,
                    store_visit.device_model from `tabStore Visit` store_visit where %s
                    order by store_visit.server_date desc""" % conditions

    query_result = frappe.db.sql(query_string, as_dict=1, debug=0)
    return query_result


def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    user = filters.get('user')
    customer = filters.get('customer')

    conditions = []

    if from_date:
        conditions.append("store_visit.server_date >= '%s'" % from_date)
    if to_date:
        conditions.append("store_visit.server_date <= '%s'" % to_date)
    if user:
        conditions.append("store_visit.user = '%s'" % user)
    if customer:
        conditions.append("store_visit.customer = '%s'" % customer)

    return " and ".join(conditions)