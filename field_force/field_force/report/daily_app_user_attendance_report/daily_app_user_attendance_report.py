# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)

    data_dict = {}

    for app_user_attendance in data:
        set_image_url(app_user_attendance)
        data_key = f"{app_user_attendance.server_date}_{app_user_attendance.user}"

        if data_key in data_dict.keys():
            data_dict[data_key]['checkout_time'] = app_user_attendance.server_time
            data_dict[data_key]['checkout_device_time'] = app_user_attendance.device_time
            data_dict[data_key]['checkout_name'] = app_user_attendance.name
            data_dict[data_key]['checkout_image'] = app_user_attendance.image
        else:
            data_dict[data_key] = app_user_attendance
            set_user_link(app_user_attendance)

    return columns, list(data_dict.values())

def set_user_link(app_user_attendance):
    if app_user_attendance.user:
        title = app_user_attendance.user_fullname or app_user_attendance.user
        app_user_attendance['user'] = f'<a href="/app/user/{app_user_attendance.user}" target="_blank">{title}</a>'

def set_image_url(app_user_attendance):
    image_url = app_user_attendance.image

    if image_url:
        if image_url.startswith('/files/'):
            app_user_attendance['image'] = f'<a href="{image_url}" target="_blank">{image_url}</a>'
        else:
            app_user_attendance['image'] = ''

def get_columns(filters):
    """ Columns of Report Table"""
    columns = [
		{"label": _("Date"), "fieldname": "server_date", "width": 150},
        {"label": _("User"), "fieldname": "user", "width": 200, "fieldtype": "Data"},
        {"label": _("Checkin Time"), "fieldname": "server_time", "fieldtype": "Time", "width": 140},
        {"label": _("Checkout Time"), "fieldname": "checkout_time", "fieldtype": "Time", "width": 140},
        {"label": _("Checkin Device Time"), "fieldname": "device_time", "fieldtype": "Time", "width": 145},
        {"label": _("Checkout Device Time"), "fieldname": "checkout_device_time", "fieldtype": "Time", "width": 145},
        {"label": _("Checkin Image"), "fieldname": "image", "width": 145},
        {"label": _("Checkout Image"), "fieldname": "checkout_image", "width": 145},
    ]

    return columns

def get_data(filters):
    conditions = get_conditions(filters)

    base_query = """select app_user_attendance.name, app_user_attendance.user, app_user_attendance.user_fullname, 
                    app_user_attendance.server_date, app_user_attendance.server_time, app_user_attendance.device_time,
                    app_user_attendance.type, app_user_attendance.image from `tabApp User Attendance` 
                    app_user_attendance where %s order by app_user_attendance.server_date, 
                    app_user_attendance.server_time""" % conditions

    query_result = frappe.db.sql(base_query, as_dict=1, debug=0)
    return query_result


def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    user = filters.get('user')

    conditions = []

    if from_date:
        conditions.append("app_user_attendance.server_date >= '%s'" % from_date)
    if to_date:
        conditions.append("app_user_attendance.server_date <= '%s'" % to_date)
    if user:
        conditions.append("app_user_attendance.user = '%s'" % user)

    return " and ".join(conditions)