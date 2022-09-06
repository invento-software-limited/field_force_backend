# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)

    return columns, data

def get_columns():
    """ Columns of Report Table"""
    return [
        {"label": _("Date"), "fieldname": "transaction_date", "width": 150},
        {"label": _("User"), "fieldname": "user", "width": 150, "fieldtype": "Link", "options": "User"},
        {"label": _("User Full Name"), "fieldname": "user_fullname", "width": 200, "fieldtype": "Link", "options": "User"},
        {"label": _("Total Requisitions"), "fieldname": "total_requisitions", "width": 250},
        {"label": _("Total Items"), "fieldname": "total_items", "width": 175},
        {"label": _("Total Quantity"), "fieldname": "total_qty", "fieldtype": "Int", "width": 125},
        {"label": _("Total Amount"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 150},
    ]


def get_data(filters):
    submitted = filters.get('submitted', 0)
    conditions = get_conditions(filters)

    query_string = """SELECT requisition.transaction_date, requisition.user, requisition.user_fullname,
                    count(*) as total_requisitions, sum(requisition.total_items) as total_items, 
                    sum(requisition.total_qty) as total_qty, sum(requisition.grand_total) as total_amount 
                    from `tabRequisition` requisition where requisition.docstatus = %s %s group by requisition.user,
                    requisition.transaction_date order by requisition.transaction_date desc""" % (submitted, conditions)

    query_result = frappe.db.sql(query_string, as_dict=1, debug=0)
    return query_result


def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    user = filters.get('user')
    conditions = ""

    if from_date:
        conditions += " and requisition.transaction_date >= '%s'" % from_date

    if to_date:
        conditions += " and requisition.transaction_date <= '%s'" % to_date

    if user:
        conditions += " and requisition.user = '%s'" % user

    # order_by = filters.get('order_by').lower()
    # sort_by = "" if filters.get('sort_by') == "Ascending" else "DESC"

    return conditions