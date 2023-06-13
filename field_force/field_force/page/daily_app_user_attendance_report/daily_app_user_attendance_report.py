# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt
import json

import frappe
from field_force.field_force.page.utils import generate_excel_and_download, get_time_in_12_hour_format
from field_force.field_force.report.utils import set_link_to_doc, set_image_url, get_site_directory_path,\
    set_google_map_location_button


@frappe.whitelist()
def get_user_attendance_data(filters=None):
    columns = get_columns()
    filters = json.loads(filters)
    data = get_absolute_data(filters)
    return data, columns

def get_absolute_data(filters, export=False):
    data = get_query_data(filters)
    site_directory = get_site_directory_path()
    data_dict = {}
    # index = 1

    for app_user_attendance in data:
        set_image_url(app_user_attendance, site_directory)
        data_key = f"{app_user_attendance.server_date}_{app_user_attendance.user}"
        app_user_attendance.cheated = 'Yes' if app_user_attendance.cheated else 'No'

        if data_key not in data_dict.keys():
            app_user_attendance.date = frappe.format_value(app_user_attendance.server_date, 'Date')
            data_dict[data_key] = app_user_attendance
            # data_dict[data_key]['sl'] = index
            data_dict[data_key]['checkin_time'] = get_time_in_12_hour_format(app_user_attendance.server_time)
            data_dict[data_key]['checkin_device_time'] = get_time_in_12_hour_format(app_user_attendance.device_time)
            data_dict[data_key]['checkin_name'] = app_user_attendance.name
            data_dict[data_key]['checkin_image'] = app_user_attendance.image
            data_dict[data_key]['checkout_image'] = '/files/default-image.png'
            data_dict[data_key]['checkin_location'] = set_google_map_location_button(app_user_attendance)

            if export:
                app_user_attendance.user = app_user_attendance.user_fullname or app_user_attendance.user
            else:
                set_link_to_doc(app_user_attendance, 'sales_person', 'sales-person')

            # index += 1
        else:
            data_dict[data_key]['checkout_time'] = get_time_in_12_hour_format(app_user_attendance.server_time)

            data_dict[data_key]['checkout_device_time'] = get_time_in_12_hour_format(app_user_attendance.device_time)
            data_dict[data_key]['checkout_name'] = app_user_attendance.name
            data_dict[data_key]['checkout_image'] = app_user_attendance.image
            data_dict[data_key]['checkout_location'] = set_google_map_location_button(app_user_attendance)

    if data_dict.values():
        return list(data_dict.values())[::-1]

    return []

def get_query_data(filters):
    conditions = get_conditions(filters)

    base_query = '''select app_user_attendance.name, app_user_attendance.user, app_user_attendance.user_fullname,
                    app_user_attendance.server_date, app_user_attendance.server_time, app_user_attendance.device_time,
                    app_user_attendance.type, app_user_attendance.image, app_user_attendance.cheated,
                    app_user_attendance.sales_person, app_user_attendance.latitude, app_user_attendance.longitude
                    from `tabApp User Attendance` app_user_attendance where %s order by app_user_attendance.server_date,
                    app_user_attendance.server_time''' % conditions

    query_result = frappe.db.sql(base_query, as_dict=1, debug=0)
    return query_result


def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    sales_person = filters.get('sales_person')

    conditions = []

    if from_date:
        conditions.append('app_user_attendance.server_date >= "%s"' % from_date)
    if to_date:
        conditions.append('app_user_attendance.server_date <= "%s"' % to_date)
    if sales_person:
        conditions.append('app_user_attendance.sales_person = "%s"' % sales_person)

    return " and ".join(conditions)

def get_columns():
    columns =  [
        {'fieldname': 'sl', 'label': 'SL', 'expwidth': 5, 'export': False},
        {'fieldname': 'date', 'label': 'Date', 'expwidth': 13},
        # {'fieldname': 'name', 'label': 'ID', 'expwidth': 20},
        {'fieldname': 'sales_person', 'label': 'Sales Person', 'expwidth': 20},
        {'fieldname': 'checkin_time', 'label': 'IN Time', 'expwidth': 15},
        {'fieldname': 'checkout_time', 'label': 'OUT Time', 'expwidth': 15},
        {'fieldname': 'checkin_device_time', 'label': 'IN Device Time', 'expwidth': 15},
        {'fieldname': 'checkout_device_time', 'label': 'OUT Device Time', 'expwidth': 15},
        {'fieldname': 'cheated', 'label': 'Cheated', 'fieldtype': 'Data', 'expwidth': 15},
        {'fieldname': 'checkin_location', 'label': 'IN<br>Location', 'export': False},
        {'fieldname': 'checkout_location', 'label': 'OUT<br>Location', 'export': False},
        {'fieldname': 'checkin_image', 'label': 'IN Image', 'fieldtype': 'Image', 'expwidth': 15, 'export': False},
        {'fieldname': 'checkout_image', 'label': 'OUT Image', 'fieldtype': 'Image', 'expwidth': 15, 'export': False},
    ]
    return columns

@frappe.whitelist()
def export_file(**filters):
    columns = get_columns()
    data = get_export_data(filters)
    file_name = 'Daily_App_User_Attendance_Report.xlsx'
    generate_excel_and_download(columns, data, file_name, height=20)

def get_export_data(filters):
    query_result = get_absolute_data(filters, export=True)
    return query_result
