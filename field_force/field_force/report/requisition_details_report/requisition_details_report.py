# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt


import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)

    for requisition in data:
        if requisition.user:
            requisition['user'] = f'<a href="/app/user/{requisition.user}" target="_blank">{requisition.user_fullname}</a>'

    return columns, data

def get_columns():
    """ Columns of Report Table"""
    return [
        {"label": _("Date"), "fieldname": "transaction_date", "width": 100},
        {"label": _("Delivery Date"), "fieldname": "delivery_date", "width": 100},
        {"label": _("Requisition"), "fieldname": "name", "width": 150, "fieldtype": "Link", "options": "Requisition"},
        {"label": _("User"), "fieldname": "user", "width": 120, "fieldtype": "Data", "options": "User"},
        # {"label": _("User Full Name"), "fieldname": "user_fullname", "width": 200, "fieldtype": "Link", "options": "User"},
		{"label": _("Customer"), "fieldname": "customer", "width": 120, "fieldtype": "Link", "options": "Customer"},
		{"label": _("Distributor"), "fieldname": "distributor", "width": 120, "fieldtype": "Link", "options": "Distributor"},
        {"label": _("Total Items"), "fieldname": "total_items", "width": 100},
        {"label": _("Total Quantity"), "fieldname": "total_qty", "fieldtype": "Int", "width": 100},
        {"label": _("Total Amount"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 150},
		{"label": _("Company"), "fieldname": "company", "width": 150, "fieldtype": "Link", "options": "Company"},
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    query_string = """SELECT requisition.name, requisition.transaction_date,requisition.delivery_date, requisition.user,
                    requisition.user_fullname, requisition.customer, requisition.distributor, requisition.total_items,
                    requisition.total_qty, requisition.grand_total as total_amount, requisition.company
                    from `tabRequisition` requisition %s order by requisition.transaction_date desc""" % conditions

    query_result = frappe.db.sql(query_string, as_dict=1, debug=0)
    return query_result


def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    user = filters.get('user')
    customer = filters.get('customer')
    distributor = filters.get('distributor')
    company = filters.get('company')
    conditions = [
        "where requisition.docstatus = %s" % filters.get('submitted', 0)
    ]

    if from_date:
        conditions.append("requisition.transaction_date >= '%s'" % from_date)
    if to_date:
        conditions.append("requisition.transaction_date <= '%s'" % to_date)
    if user:
        conditions.append("requisition.user = '%s'" % user)
    if customer:
        conditions.append("requisition.customer = '%s'" % customer)
    if distributor:
        conditions.append("requisition.distributor = '%s'" % distributor)
    if company:
        conditions.append("requisition.company = '%s'" % company)

    return " and ".join(conditions)