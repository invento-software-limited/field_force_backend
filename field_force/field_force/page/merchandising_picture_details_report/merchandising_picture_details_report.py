import frappe
import json

from field_force.field_force.page.utils import generate_excel_and_download, get_time_in_12_hour_format
from field_force.field_force.report.utils import set_link_to_doc, set_image_url, get_site_directory_path,\
    set_image_download_button


@frappe.whitelist()
def get_merchandising_picture_data(filters=None):
    columns = get_columns()
    data = get_absolute_data(filters)
    return data, columns

def get_absolute_data(filters, export=False):
    query_result = get_query_data(filters)
    site_directory = get_site_directory_path()

    for index, merchandising_picture in enumerate(query_result):
        merchandising_picture['docname'] = merchandising_picture.name
        merchandising_picture.brand = merchandising_picture.brand or ''

        set_image_download_button(merchandising_picture, site_directory)
        set_image_url(merchandising_picture, site_directory)

        server_time = get_time_in_12_hour_format(merchandising_picture.server_time)
        device_time = get_time_in_12_hour_format(merchandising_picture.device_time)
        merchandising_picture.server_date = frappe.format(merchandising_picture.server_date, 'Date')
        merchandising_picture.device_date = frappe.format(merchandising_picture.device_date, 'Date')
        # server_time = str(merchandising_picture.server_time).split('.')[0] \
        #     if '.' in str(merchandising_picture.server_time) else merchandising_picture.server_time
        # device_time = str(merchandising_picture.device_time).split('.')[0] \
        #     if '.' in str(merchandising_picture.device_time) else merchandising_picture.device_time

        if not export:
            set_link_to_doc(merchandising_picture, 'name', 'merchandising-picture')
            set_link_to_doc(merchandising_picture, 'customer', 'customer')
            set_link_to_doc(merchandising_picture, 'brand', 'brand')
            set_link_to_doc(merchandising_picture, 'sales_person', 'sales-person')

            # merchandising_picture.server_date = f"{merchandising_picture.server_date}<br>{server_time}"
            merchandising_picture.server_time = server_time
            merchandising_picture.device_date = f"{merchandising_picture.device_date}<br>{device_time}"
        else:
            # merchandising_picture.server_date = f"{merchandising_picture.server_date}\n{server_time}"
            merchandising_picture.server_time = server_time
            merchandising_picture.device_date = f"{merchandising_picture.device_date}\n{device_time}"

        merchandising_picture.cheated = 'Yes' if merchandising_picture.cheated else 'No'

    return query_result

def get_query_data(filters):
    try:
        filters = json.loads(filters)
    except:
        pass
    conditions = get_conditions(filters)

    query_string = '''select merchandising_picture.name, merchandising_picture.sales_person, merchandising_picture.details,
                    merchandising_picture.customer, merchandising_picture.image, merchandising_picture.contact_number,
                    merchandising_picture.server_date, time(merchandising_picture.server_time) as server_time,
                    merchandising_picture.device_date, time(merchandising_picture.device_time) as device_time,
                    merchandising_picture.latitude, merchandising_picture.longitude, merchandising_picture.brand,
                    merchandising_picture.device_model, merchandising_picture.customer_address, merchandising_picture.feedback,
                    merchandising_picture.cheated from `tabMerchandising Picture` merchandising_picture where %s
                    order by merchandising_picture.server_date desc, merchandising_picture.server_time desc''' % conditions

    query_result = frappe.db.sql(query_string, as_dict=1, debug=0)
    return query_result


def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    sales_person = filters.get('sales_person')
    customer = filters.get('customer')
    brand = filters.get('brand')

    conditions = []

    if from_date:
        conditions.append('merchandising_picture.server_date >= "%s"' % from_date)
    if to_date:
        conditions.append('merchandising_picture.server_date <= "%s"' % to_date)
    if sales_person:
        conditions.append('merchandising_picture.sales_person = "%s"' % sales_person)
    if customer:
        conditions.append('merchandising_picture.customer = "%s"' % customer)
    if brand:
        conditions.append('merchandising_picture.brand = "%s"' % brand)

    return " and ".join(conditions)

def get_columns():
    columns =  [
        {'fieldname': 'sl', 'label': 'SL', 'expwidth': 5, 'export': False, 'width': 30},
        {'fieldname': 'server_date', 'label': 'Date', 'expwidth': 13, 'width': 100},
        {'fieldname': 'server_time', 'label': 'Time', 'expwidth': 13, 'width': 100},
        {'fieldname': 'name', 'label': 'ID', 'expwidth': 20, 'width': 120},
        {'fieldname': 'brand', 'label': 'Brand', 'expwidth': 15, 'width': 120},
        {'fieldname': 'customer', 'label': 'Customer', 'expwidth': 15, 'width': 120},
        # {'fieldname': 'contact_number', 'label': 'Contact', 'expwidth': 15},
        {'fieldname': 'details', 'label': 'Details', 'expwidth': 13, 'width': 250, 'editable': False},
        {'fieldname': 'feedback', 'label': 'Feedback', 'expwidth': 13, 'width': 250, 'editable': True},
        {'fieldname': 'sales_person', 'label': 'Sales Person', 'expwidth': 20, 'width': 100},
        {'fieldname': 'device_date', 'label': 'Device Date Time', 'expwidth': 15, 'width': 100},
        {'fieldname': 'cheated', 'label': 'Cheated', 'fieldtype': 'Data', 'expwidth': 15, 'width': 30},
        {'fieldname': 'image', 'label': 'Image', 'fieldtype': 'Image', 'expwidth': 15, 'export': False},
        {'fieldname': 'image_download', 'label': '', 'fieldtype': 'Data', 'expwidth': 15, 'export': False},
    ]
    return columns

@frappe.whitelist()
def export_file(**filters):
    columns = get_columns()
    data = get_export_data(filters)
    file_name = 'Merchandising_Picture_Details_Report.xlsx'
    generate_excel_and_download(columns, data, file_name, height=30)

def get_export_data(filters):
    query_result = get_absolute_data(filters, export=True)
    return query_result

@frappe.whitelist()
def update_field(**kwargs):
    docname = kwargs.get('docname')
    fieldname = kwargs.get('fieldname')
    value = kwargs.get('value')
    merchandising_picture = frappe.get_doc("Merchandising Picture", docname)

    if merchandising_picture.get(fieldname) != value:
        merchandising_picture.update({fieldname:value})
        merchandising_picture.save()

    return True
