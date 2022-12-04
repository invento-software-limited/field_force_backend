import io
import os

from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

import frappe
import json
import openpyxl

from field_force.field_force.report.utils import set_image_url, set_user_link, get_site_directory_path

data = []

@frappe.whitelist()
def get_user_attendance_data(filters=None):
    global data
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

    data = query_result
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

@frappe.whitelist()
def export_data():
    labels =  {
        'sl': 'SL',
        'server_date': 'DateTime',
        'name': 'ID',
        'user': 'User',
        'type': 'Type',
        'device_date': 'Device DateTime',
        'cheated': 'Cheated',
        'latitude': 'Latitude',
        'longitude': 'Longitude',
        'device_model': 'Model',
        'image': 'Image'
    }

    print(labels.values())

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    generate_row(worksheet, 1, labels.values())
    row_count = 2

    for row in data:
        row_data = [row[field] for field in labels.keys()]
        generate_row(worksheet, row_count, row_data)
        row_count += 1

    byte_data = io.BytesIO()
    workbook.save(byte_data)

    frappe.local.response.filename = 'App_User_Attendance_Report.xlsx'
    frappe.local.response.filecontent = byte_data.getvalue()
    frappe.local.response.type = "download"


def generate_row(ws, row_count, column_values, font=None, font_size=None, color=None, height=None):
    cells = []
    amount_columns = [5, 7, 8]
    column_widths = [15, 15, 15,15, 15, 15,15, 15, 15,]

    for i, value in enumerate(column_values):
        column_number = i + 1
        cell = ws.cell(row=row_count, column=column_number)
        cell.value = value

        if font:
            cell.font = font
        elif font_size:
            cell.font = Font(size=font_size)
        if color:
            cell.fill = PatternFill(fgColor=color, fill_type='solid')

        # if isinstance(value, int):
        #     cell.number_format = "#,##0"
        # elif isinstance(value, float):
        if i+1 in amount_columns:
            cell.number_format = "#,##0.00"

        # ws.column_dimensions[get_column_letter(i + 1)].width = column_widths[i]
        cell.alignment = Alignment(vertical='center')
        cells.append(cell)

    if height:
        ws.row_dimensions[row_count].height = height

    # set_column_width(ws)
    return cells