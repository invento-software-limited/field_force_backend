# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt
import json

import frappe

@frappe.whitelist()
def get_user_attendance_data(filters=None):
    filters = json.loads(filters)
    data = get_data(filters)
    data_dict = {}
    index = 1

    for app_user_attendance in data:
        # set_image_url(app_user_attendance)
        data_key = f"{app_user_attendance.server_date}_{app_user_attendance.user}"

        if data_key not in data_dict.keys():
            data_dict[data_key] = app_user_attendance
            data_dict[data_key]['checkin_time'] = app_user_attendance.server_time
            data_dict[data_key]['checkin_device_time'] = app_user_attendance.device_time
            data_dict[data_key]['checkin_name'] = app_user_attendance.name
            data_dict[data_key]['checkin_image'] = app_user_attendance.image
            data_dict[data_key]['sl'] = index

            set_user_link(app_user_attendance)
            index += 1
        else:
            data_dict[data_key]['checkout_time'] = app_user_attendance.server_time
            data_dict[data_key]['checkout_device_time'] = app_user_attendance.device_time
            data_dict[data_key]['checkout_name'] = app_user_attendance.name
            data_dict[data_key]['checkout_image'] = app_user_attendance.image

    if data_dict.values():
        return list(data_dict.values())[::-1]

    return []

def set_user_link(app_user_attendance):
    if app_user_attendance.user:
        title = app_user_attendance.user_fullname or app_user_attendance.user
        app_user_attendance['name'] = f'<a href="/app/app-user-attendance/{app_user_attendance.name}"' \
                                      f' target="_blank">{app_user_attendance.name}</a>'
        app_user_attendance['user'] = f'<a href="/app/user/{app_user_attendance.user}" target="_blank">{title}</a>'

def set_image_url(app_user_attendance):
    image_url = app_user_attendance.image

    if image_url:
        if image_url.startswith('/files/'):
            app_user_attendance['image'] = f'<a href="{image_url}" target="_blank">{image_url}</a>'
        else:
            app_user_attendance['image'] = ''


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