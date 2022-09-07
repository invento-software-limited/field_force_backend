# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)

    for app_user_attendance in data:
        if app_user_attendance.user:
            title = app_user_attendance.user_fullname or app_user_attendance.user
            app_user_attendance['user'] = f'<a href="/app/user/{app_user_attendance.user}" target="_blank">{title}</a>'

    return columns, data

def get_columns(filters):
    """ Columns of Report Table"""
    columns = [
		{"label": _("Date"), "fieldname": "server_date", "width": 140},
		{"label": _("User"), "fieldname": "user", "width": 150, "fieldtype": "Data"},
        {"label": _("Type"), "fieldname": "type", "width": 140},
        {"label": _("Time"), "fieldname": "server_time", "fieldtype": "Time", "width": 130},
        {"label": _("Device Date"), "fieldname": "device_date", "fieldtype": "Date", "width": 140},
        {"label": _("Device Time"), "fieldname": "device_time", "fieldtype": "Time", "width": 130},
        {"label": _("Latitude"), "fieldname": "latitude", "width": 125},
        {"label": _("Longitude"), "fieldname": "longitude", "width": 125},
        {"label": _("Device Model"), "fieldname": "device_model", "width": 130},

    ]

    return columns

def get_data(filters):
    conditions = get_conditions(filters)

    query_string = """select app_user_attendance.user, app_user_attendance.user_fullname, 
                    app_user_attendance.server_date, app_user_attendance.server_time, app_user_attendance.type,
                    app_user_attendance.device_date, app_user_attendance.device_time 
                    from `tabApp User Attendance` app_user_attendance where %s
                    order by app_user_attendance.device_date desc""" % (conditions)
    print(query_string)
    query_result = frappe.db.sql(query_string, as_dict=1, debug=0)
    return query_result


def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    user = filters.get('user')
    type = filters.get('type')

    conditions = []

    if type:
        conditions.append("app_user_attendance.type = '%s'" % type)
    if from_date:
        conditions.append("app_user_attendance.device_date >= '%s'" % from_date)
    if to_date:
        conditions.append("app_user_attendance.device_date <= '%s'" % to_date)
    if user:
        conditions.append("app_user_attendance.user = '%s'" % user)

    return " and ".join(conditions)