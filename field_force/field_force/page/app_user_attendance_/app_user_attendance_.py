import os

import frappe
import json

from field_force.field_force.report.utils import set_image_url, set_user_link, get_site_directory_path


@frappe.whitelist()
def get_user_attendance_data(filters=None):
    query_result = get_query_data(filters)
    site_directory = get_site_directory_path()

    for index, app_user_attendance in enumerate(query_result):
        set_user_link(app_user_attendance)
        app_user_attendance['name'] = f'<a href="/app/app-user-attendance/{app_user_attendance.name}" ' \
                                      f'target="_blank">{app_user_attendance.name}</a>'
        app_user_attendance.server_date = f"{app_user_attendance.server_date}<br>{app_user_attendance.server_time}"
        app_user_attendance.device_date = f"{app_user_attendance.device_date}<br>{app_user_attendance.device_time}"

        if app_user_attendance.cheated:
            app_user_attendance.cheated = 'Yes'

        # if not app_user_attendance.image or '/files/' not in app_user_attendance.image:
        #     app_user_attendance.image = '/files/default-image.png'

        set_image_url(app_user_attendance, site_directory)
        # set_cheat_status(doc=app_user_attendance)

        app_user_attendance['sl'] = index + 1
    return query_result


def get_query_data(filters):
    try:
        filters = json.loads(filters)
    except:
        pass
    conditions = get_conditions(filters)

    query_string = """select app_user_attendance.name, app_user_attendance.user, app_user_attendance.user_fullname, 
                    app_user_attendance.server_date, app_user_attendance.server_time, app_user_attendance.type,
                    app_user_attendance.device_date, app_user_attendance.device_time, app_user_attendance.latitude,
                    app_user_attendance.longitude, app_user_attendance.device_model, app_user_attendance.image,
                    app_user_attendance.cheated from `tabApp User Attendance` app_user_attendance where %s
                    order by app_user_attendance.server_date desc""" % (conditions)

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
        conditions.append("app_user_attendance.server_date >= '%s'" % from_date)
    if to_date:
        conditions.append("app_user_attendance.server_date <= '%s'" % to_date)
    if user:
        conditions.append("app_user_attendance.user = '%s'" % user)

    return " and ".join(conditions)
