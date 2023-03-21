import frappe
import json

from field_force.field_force.page.utils import generate_excel_and_download, get_time_in_12_hour_format
from field_force.field_force.report.utils import set_image_url, set_link_to_doc, get_site_directory_path, \
    set_google_map_location_button

@frappe.whitelist()
def get_user_attendance_data(filters=None):
    columns = get_columns()
    query_result = get_query_data(filters)
    site_directory = get_site_directory_path()

    for index, app_user_attendance in enumerate(query_result):
        set_link_to_doc(app_user_attendance, 'sales_person', 'sales-person')
        app_user_attendance.server_time = get_time_in_12_hour_format(app_user_attendance.server_time)
        app_user_attendance.device_time = get_time_in_12_hour_format(app_user_attendance.device_time)

        app_user_attendance['name'] = f'<a href="/app/app-user-attendance/{app_user_attendance.name}" ' \
                                      f'target="_blank">{app_user_attendance.name}</a>'
        # app_user_attendance.server_date = f"{app_user_attendance.server_date}<br>{app_user_attendance.server_time}"
        # app_user_attendance.device_date = f"{app_user_attendance.device_date}<br>{app_user_attendance.device_time}"

        app_user_attendance.cheated = 'Yes' if app_user_attendance.cheated else 'No'
        app_user_attendance.location = set_google_map_location_button(app_user_attendance)
        set_image_url(app_user_attendance, site_directory)
        app_user_attendance['sl'] = index + 1

    # data = query_result
    return query_result, columns

def get_query_data(filters):
    try:
        filters = json.loads(filters)
    except:
        pass
    conditions = get_conditions(filters)

    query_string = '''select app_user_attendance.name, app_user_attendance.server_date, app_user_attendance.server_time,
                    app_user_attendance.type, app_user_attendance.device_date, app_user_attendance.device_time, 
                    app_user_attendance.latitude, app_user_attendance.longitude, app_user_attendance.device_model, 
                    app_user_attendance.image, app_user_attendance.sales_person, app_user_attendance.cheated
                    from `tabApp User Attendance` app_user_attendance where %s 
                    order by app_user_attendance.server_date desc, app_user_attendance.server_time desc''' % (conditions)

    query_result = frappe.db.sql(query_string, as_dict=1, debug=0)
    return query_result


def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    sales_person = filters.get('sales_person')
    type = filters.get('type')

    conditions = []

    if type:
        conditions.append('app_user_attendance.type = "%s"' % type)
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
        {'fieldname': 'server_date', 'label': 'Date', 'expwidth': 12},
        {'fieldname': 'server_time', 'label': 'Time', 'expwidth': 12},
        {'fieldname': 'name', 'label': 'ID', 'expwidth': 15},
        {'fieldname': 'sales_person', 'label': 'Sales Person', 'expwidth': 15},
        {'fieldname': 'type', 'label': 'Type', 'expwidth': 10},
        {'fieldname': 'device_date', 'label': 'Device Date', 'expwidth': 15},
        {'fieldname': 'device_time', 'label': 'Device Time', 'expwidth': 15},
        {'fieldname': 'cheated', 'label': 'Cheated', 'expwidth': 10},
        {'fieldname': 'location', 'label': 'Location', 'expwidth': 15},
        {'fieldname': 'image', 'label': 'Image', 'fieldtype': 'Image', 'expwidth': 15, 'export': False}
    ]
    return columns

@frappe.whitelist()
def export_file(**filters):
    columns = get_columns()
    data = get_export_data(filters)
    file_name = 'App_User_Attendance_Report.xlsx'
    generate_excel_and_download(columns, data, file_name)

def get_export_data(filters):
    query_result = get_query_data(filters)

    for index, app_user_attendance in enumerate(query_result):
        # app_user_attendance.user = app_user_attendance.user_fullname or app_user_attendance.user
        # app_user_attendance.server_date = f"{app_user_attendance.server_date}\n{app_user_attendance.server_time}"
        # app_user_attendance.device_date = f"{app_user_attendance.device_date}\n{app_user_attendance.device_time}"
        app_user_attendance.cheated = 'Yes' if app_user_attendance.cheated else 'No'
        app_user_attendance['sl'] = index + 1

    return query_result
