import frappe
import json

@frappe.whitelist()
def get_merchandising_picture_data(filters=None):
    query_result = get_query_data(filters)

    for index, merchandising_picture in enumerate(query_result):
        if merchandising_picture.user:
            title = merchandising_picture.user_fullname or merchandising_picture.user
            merchandising_picture['user'] = f'<a href="/app/user/{merchandising_picture.user}" target="_blank">{title}</a>'

        # if  merchandising_picture.image:
        #     if '/files/' in merchandising_picture.image:
        #         merchandising_picture['image'] = f'<a href="{merchandising_picture.image}" target="_blank">{merchandising_picture.image}</a>'
        merchandising_picture['sl'] = index + 1
        merchandising_picture.server_time = str(merchandising_picture.server_time).split('.')[0]

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
                    merchandising_picture.device_model from `tabMerchandising Picture` merchandising_picture where %s
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