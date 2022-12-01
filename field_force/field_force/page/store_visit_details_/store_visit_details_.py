import frappe
import json

from field_force.field_force.report.utils import set_user_link, set_image_url,\
    get_site_directory_path, set_link_to_doc


@frappe.whitelist()
def get_store_visit_data(filters=None):
    query_result = get_query_data(filters)
    site_directory = get_site_directory_path()

    for index, store_visit in enumerate(query_result):
        set_link_to_doc(store_visit, 'name', 'store-visit')
        set_link_to_doc(store_visit, 'customer', 'customer')
        set_user_link(store_visit)
        set_image_url(store_visit, site_directory)

        server_time = str(store_visit.server_time).split('.')[0] if '.' in str(store_visit.server_time) else store_visit.server_time
        device_time = str(store_visit.device_time).split('.')[0] if '.' in str(store_visit.device_time) else store_visit.device_time
        store_visit.server_date = f"{store_visit.server_date}<br>{server_time}"
        store_visit.device_date = f"{store_visit.device_date}<br>{device_time}"

        if store_visit.cheated:
            store_visit.cheated = 'Yes'

        store_visit['sl'] = index + 1

    return query_result

def get_query_data(filters):
    try:
        filters = json.loads(filters)
    except:
        pass
    conditions = get_conditions(filters)

    query_string = """select store_visit.name, store_visit.user, store_visit.user_fullname, store_visit.customer,
                    store_visit.image, store_visit.contact_number, store_visit.server_date, store_visit.server_time,
                    store_visit.device_date, store_visit.device_time, store_visit.latitude, store_visit.longitude,
                    store_visit.device_model, store_visit.customer_address, store_visit.cheated from `tabStore Visit` 
                    store_visit where %s order by store_visit.server_date desc""" % conditions

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