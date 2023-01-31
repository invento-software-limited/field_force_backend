# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    """ Columns of Report Table"""
    columns = [
        {"label": _("Date"), "fieldname": "transaction_date", "width": 120},
        {},
        {"label": _("Total Requisition"), "fieldname": "total_requisitions", "width": 150},
        {"label": _("Total Item"), "fieldname": "total_items", "width": 160},
        {"label": _("Total Qty"), "fieldname": "total_qty", "fieldtype": "Int", "width": 160},
        {"label": _("Total Amount"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 160},
        {"label": _("Status"), "fieldname": "status", "fieldtype":"Data", "width": 120},
        {"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company","width": 140},
    ]

    if filters.get('group_by') == 'Distributor':
        columns[1] = {"label": _("Distributor"), "fieldname": "distributor", "fieldtype":"Link",
                      "options":"Distributor", "width": 200}
    elif filters.get('group_by') == 'Customer':
        columns[1] = {"label": _("Customer"), "fieldname": "customer", "fieldtype":"Link",
                      "options":"Customer", "width": 200}
    else:
        columns[1] = {"label": _("Sales Person"), "fieldname": "sales_person", "fieldtype": "Link",
                      "options":"Sales Person", "width": 200}

    return columns

def get_data(filters):
    conditions = get_conditions(filters)
    if filters.get('group_by') == 'Distributor':
        group_by = 'requisition.distributor'
    elif filters.get('group_by') == 'Customer':
        group_by = 'requisition.customer'
    else:
        group_by = 'requisition.sales_person'

    query_string = '''select requisition.transaction_date, requisition.sales_person, requisition.customer,
                    requisition.distributor, count(*) as total_requisitions, sum(requisition.total_items) 
                    as total_items, requisition.company, sum(requisition.total_qty) as total_qty, requisition.status,
                    sum(requisition.grand_total) as total_amount from `tabRequisition` requisition 
                    where %s group by %s
                    order by total_amount desc''' % (conditions, group_by)

    query_result = frappe.db.sql(query_string, as_dict=1, debug=0)
    return query_result


def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    group_by = filters.get('group_by')
    sales_person = filters.get('sales_person')
    distributor = filters.get('distributor')
    customer = filters.get('customer')
    status = filters.get('status')

    conditions = [
        'requisition.status = "%s"' % status
    ]

    if from_date:
        conditions.append('requisition.transaction_date >= "%s"' % from_date)
    if to_date:
        conditions.append('requisition.transaction_date <= "%s"' % to_date)

    if group_by == 'Distributor' and distributor:
        conditions.append('requisition.distributor = "%s"' % distributor)
    elif group_by == 'Customer' and customer:
        conditions.append('requisition.customer = "%s"' % customer)
    elif group_by == 'Sales Person' and sales_person:
        conditions.append('requisition.sales_person = "%s"' % sales_person)

    return " and ".join(conditions)