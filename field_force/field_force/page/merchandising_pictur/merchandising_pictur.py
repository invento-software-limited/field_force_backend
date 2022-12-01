import frappe
import json

from field_force.field_force.report.utils import set_link_to_doc, set_user_link, set_image_url, get_site_directory_path


@frappe.whitelist()
def get_merchandising_picture_data(filters=None):
    query_result = get_query_data(filters)
    site_directory = get_site_directory_path()

    for index, merchandising_picture in enumerate(query_result):
        set_link_to_doc(merchandising_picture, 'name', 'merchandising-picture')
        set_link_to_doc(merchandising_picture, 'customer', 'customer')
        set_link_to_doc(merchandising_picture, 'brand', 'brand')
        set_user_link(merchandising_picture)
        set_image_url(merchandising_picture, site_directory)

        server_time = str(merchandising_picture.server_time).split('.')[0] \
            if '.' in str(merchandising_picture.server_time) else merchandising_picture.server_time
        device_time = str(merchandising_picture.device_time).split('.')[0] \
            if '.' in str(merchandising_picture.device_time) else merchandising_picture.device_time
        merchandising_picture.server_date = f"{merchandising_picture.server_date}<br>{server_time}"
        merchandising_picture.device_date = f"{merchandising_picture.device_date}<br>{device_time}"

        if merchandising_picture.cheated:
            merchandising_picture.cheated = 'Yes'

        merchandising_picture['sl'] = index + 1

    return query_result

def get_query_data(filters):
    try:
        filters = json.loads(filters)
    except:
        pass
    conditions = get_conditions(filters)

    query_string = """select merchandising_picture.name, merchandising_picture.user, merchandising_picture.user_fullname,
                    merchandising_picture.customer, merchandising_picture.image, merchandising_picture.contact_number,
                    merchandising_picture.server_date, time(merchandising_picture.server_time) as server_time,
                    merchandising_picture.device_date, time(merchandising_picture.device_time) as device_time,
                    merchandising_picture.latitude, merchandising_picture.longitude, merchandising_picture.brand,
                    merchandising_picture.device_model, merchandising_picture.customer_address,
                    merchandising_picture.cheated from `tabMerchandising Picture` merchandising_picture where %s
                    order by merchandising_picture.server_date desc""" % conditions

    query_result = frappe.db.sql(query_string, as_dict=1, debug=0)
    return query_result


def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    user = filters.get('user')
    customer = filters.get('customer')
    brand = filters.get('brand')

    conditions = []

    if from_date:
        conditions.append("merchandising_picture.server_date >= '%s'" % from_date)
    if to_date:
        conditions.append("merchandising_picture.server_date <= '%s'" % to_date)
    if user:
        conditions.append("merchandising_picture.user = '%s'" % user)
    if customer:
        conditions.append("merchandising_picture.customer = '%s'" % customer)
    if brand:
        conditions.append("merchandising_picture.brand = '%s'" % brand)

    return " and ".join(conditions)