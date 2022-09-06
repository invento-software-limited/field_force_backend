# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    print(data)
    for requisition in data:
        if requisition.user:
            requisition['user'] = f'<a href="/app/user/{requisition.user}" target="_blank">{requisition.user_fullname}</a>'

    return columns, data

def get_columns(filters):
    """ Columns of Report Table"""
    columns = [
        {"label": _("Date"), "fieldname": "transaction_date", "width": 150},
        {},
        {"label": _("Total Requisition"), "fieldname": "total_requisitions", "width": 180},
        {"label": _("Total Item"), "fieldname": "total_items", "width": 170},
        {"label": _("Total Quantity"), "fieldname": "total_qty", "fieldtype": "Int", "width": 180},
        {"label": _("Total Amount"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 180},
        {"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company","width": 150},
    ]

    if filters.get('group_by') == 'User':
        columns[1] = {"label": _("User"), "fieldname": "user", "width": 200}
    else:
        columns[1] = {"label": _("Customer"), "fieldname": "customer", "fieldtype":"Link",
                      "options":"Customer", "width": 200}

    return columns

def get_data(filters):
    conditions = get_conditions(filters)
    group_by = 'requisition.user' if filters.get('group_by') == 'User' else 'requisition.customer'

    query_string = """SELECT requisition.transaction_date, requisition.user, requisition.user_fullname,
                    requisition.customer, count(*) as total_requisitions, sum(requisition.total_items) 
                    as total_items, requisition.company, sum(requisition.total_qty) as total_qty, 
                    sum(requisition.grand_total) as total_amount from `tabRequisition` requisition 
                    where %s group by requisition.transaction_date, %s
                    order by requisition.transaction_date desc""" % (conditions, group_by)

    query_result = frappe.db.sql(query_string, as_dict=1, debug=0)
    return query_result


def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    group_by = filters.get('group_by')
    user = filters.get('user')
    customer = filters.get('customer')
    status = filters.get('status')

    conditions = [
        "requisition.status = '%s'" % status
    ]

    if from_date:
        conditions.append("requisition.transaction_date >= '%s'" % from_date)
    if to_date:
        conditions.append("requisition.transaction_date <= '%s'" % to_date)
    if group_by == 'User' and user:
        conditions.append("requisition.user = '%s'" % user)
    if group_by == 'Customer' and customer:
        conditions.append("requisition.customer = '%s'" % customer)

    return " and ".join(conditions)