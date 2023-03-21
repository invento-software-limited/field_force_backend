import frappe
import json

from field_force.field_force.page.utils import generate_excel_and_download, get_time_in_12_hour_format, get_datetime_with_12_hour_format
from field_force.field_force.report.utils import set_image_url, get_site_directory_path, set_link_to_doc


@frappe.whitelist()
def get_store_visit_data(filters=None):
    columns = get_columns()
    data = get_absolute_data(filters)
    return data, columns

def get_absolute_data(filters, export=False):
    query_result = get_query_data(filters)
    site_directory = get_site_directory_path()

    for index, store_visit in enumerate(query_result):
        set_image_url(store_visit, site_directory)

        server_time = get_time_in_12_hour_format(store_visit.server_time)
        device_time = get_time_in_12_hour_format(store_visit.device_time)
        # server_time = str(store_visit.server_time).split('.')[0] \
        #     if '.' in str(store_visit.server_time) else store_visit.server_time
        # device_time = str(store_visit.device_time).split('.')[0] \
        #     if '.' in str(store_visit.device_time) else store_visit.device_time

        if not export:
            set_link_to_doc(store_visit, 'name', 'store-visit')
            set_link_to_doc(store_visit, 'customer', 'customer')
            set_link_to_doc(store_visit, 'sales_person', 'sales-person')

            # store_visit.server_date = f"{store_visit.server_date}<br>{server_time}"
            store_visit.server_time = server_time
            store_visit.device_date = f"{store_visit.device_date}<br>{device_time}"
        else:
            # store_visit.user = store_visit.user_fullname or store_visit.user
            # store_visit.server_date = f"{store_visit.server_date}\n{server_time}"
            store_visit.server_time = server_time
            store_visit.device_date = f"{store_visit.device_date}\n{device_time}"

        store_visit.cheated = 'Yes' if store_visit.cheated else 'No'
        store_visit['sl'] = index + 1

    return query_result

def get_query_data(filters):
    try:
        filters = json.loads(filters)
    except:
        pass
    conditions = get_conditions(filters)

    query_string = '''select store_visit.name, store_visit.sales_person, store_visit.customer, store_visit.details,
                    store_visit.image, store_visit.contact_number, store_visit.server_date, store_visit.server_time,
                    store_visit.device_date, store_visit.device_time, store_visit.latitude, store_visit.longitude,
                    store_visit.device_model, store_visit.customer_address, store_visit.cheated from `tabStore Visit` 
                    store_visit where %s order by store_visit.server_date desc, store_visit.server_time desc''' % conditions

    query_result = frappe.db.sql(query_string, as_dict=1, debug=0)
    return query_result


def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    sales_person = filters.get('sales_person')
    customer = filters.get('customer')

    conditions = []

    if from_date:
        conditions.append('store_visit.server_date >= "%s"' % from_date)
    if to_date:
        conditions.append('store_visit.server_date <= "%s"' % to_date)
    if sales_person:
        conditions.append('store_visit.sales_person = "%s"' % sales_person)
    if customer:
        conditions.append('store_visit.customer = "%s"' % customer)

    return " and ".join(conditions)

def get_columns():
    columns =  [
        {'fieldname': 'sl', 'label': 'SL', 'expwidth': 5, 'export': False, 'width': 30},
        {'fieldname': 'server_date', 'label': 'Date', 'expwidth': 13, 'width': 90},
        {'fieldname': 'server_time', 'label': 'Time', 'expwidth': 13, 'width': 70},
        {'fieldname': 'name', 'label': 'ID', 'expwidth': 20},
        {'fieldname': 'customer', 'label': 'Customer', 'expwidth': 15, 'width':150},
        # {'fieldname': 'customer_address', 'label': 'Address', 'expwidth': 15},
        # {'fieldname': 'contact_number', 'label': 'Contact', 'expwidth': 15},
        {'fieldname': 'details', 'label': 'Details', 'expwidth': 15, 'width':100},
        {'fieldname': 'sales_person', 'label': 'Sales Person', 'expwidth': 20},
        {'fieldname': 'device_date', 'label': 'Device Date Time', 'expwidth': 15, 'width': 80},
        {'fieldname': 'cheated', 'label': 'Cheated', 'fieldtype': 'Data', 'expwidth': 15, 'width': 20},
        # {'fieldname': 'latitude', 'label': 'Latitude', 'fieldtype': 'Data', 'expwidth': 15},
        # {'fieldname': 'longitude', 'label': 'Longitude', 'fieldtype': 'Data', 'expwidth': 15},
        # {'fieldname': 'device_model', 'label': 'Device Model', 'fieldtype': 'Data', 'expwidth': 15},
        {'fieldname': 'image', 'label': 'Image', 'fieldtype': 'Image', 'expwidth': 15, 'export': False},
    ]
    return columns

@frappe.whitelist()
def export_file(**filters):
    columns = get_columns()
    data = get_export_data(filters)
    file_name = 'Store_Visit_Details_Report.xlsx'
    generate_excel_and_download(columns, data, file_name, height=30)

def get_export_data(filters):
    query_result = get_absolute_data(filters, export=True)
    return query_result