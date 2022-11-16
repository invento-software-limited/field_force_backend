import frappe
import json

@frappe.whitelist()
def get_store_visit_data(filters=None):
    query_result = get_query_data(filters)

    for index, store_visit in enumerate(query_result):
        if store_visit.user:
            title = store_visit.user_fullname or store_visit.user
            store_visit['user'] = f'<a href="/app/user/{store_visit.user}" target="_blank">{title}</a>'

        # if  store_visit.image:
        #     if '/files/' in store_visit.image:
        #         store_visit['image'] = f'<a href="{store_visit.image}" target="_blank">{store_visit.image}</a>'
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
                    store_visit.device_model from `tabStore Visit` store_visit where %s
                    order by store_visit.server_date desc""" % conditions

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