# Copyright (c) 2023, Invento Software Limited and contributors
# For license information, please see license.txt

# import frappe



import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    """ Columns of Report Table"""
    columns = [
        {"label": _("Date"), "fieldname": "transaction_date", "width": 140},
        {},
        {"label": _("Total Sales Order"), "fieldname": "total_sales_orders", "width": 150},
        {"label": _("Total Item"), "fieldname": "total_items", "width": 160},
        {"label": _("Total Qty"), "fieldname": "total_qty", "fieldtype": "Int", "width": 160},
        {"label": _("Total Amount"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 160},
        # {"label": _("Created By"), "fieldname": "user", "fieldtype":"Data", "width": 140},
        {"label": _("Status"), "fieldname": "status", "fieldtype":"Data", "width": 120},
        {"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company","width": 160},
    ]

    if filters.get('group_by') == 'Distributor':
        columns[1] = {"label": _("Distributor"), "fieldname": "distributor", "fieldtype":"Link",
                      "options":"Distributor", "width": 160}
    elif filters.get('group_by') == 'Customer':
        columns[1] = {"label": _("Customer"), "fieldname": "customer", "fieldtype":"Link",
                      "options":"Customer", "width": 160}
    else:
        columns[1] = {"label": _("Sales Person"), "fieldname": "sales_person", "fieldtype": "Link",
                      "options":"Sales Person", "width": 160}

    return columns

def get_data(filters):
    conditions = get_conditions(filters)
    status = filters.get('status')

    if filters.get('group_by') == 'Distributor':
        group_by = 'sales_order.distributor'
    elif filters.get('group_by') == 'Customer':
        group_by = 'sales_order.customer'
    else:
        group_by = 'sales_order.sales_person'

    query_string = '''select sales_order.transaction_date, sales_order.sales_person, sales_order.customer,
                    sales_order.distributor, count(*) as total_sales_orders, sum(sales_order.total_items) 
                    as total_items, sales_order.company, sum(sales_order.total_qty) as total_qty, "%s" as status,
                    sum(sales_order.grand_total) as total_amount from `tabSales Order` sales_order 
                    where %s group by %s order by total_amount desc''' % (status, conditions, group_by)

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

    status_dict = {
        "Draft": 0,
        "Submitted": 1,
        "Cancelled": 2
    }

    conditions = [
        'sales_order.docstatus = %s' % status_dict.get(status)
    ]

    if from_date:
        conditions.append('sales_order.transaction_date >= "%s"' % from_date)
    if to_date:
        conditions.append('sales_order.transaction_date <= "%s"' % to_date)

    if group_by == 'Distributor' and distributor:
        conditions.append('sales_order.distributor = "%s"' % distributor)
    elif group_by == 'Customer' and customer:
        conditions.append('sales_order.customer = "%s"' % customer)
    elif group_by == 'Sales Person' and sales_person:
        conditions.append('sales_order.sales_person = "%s"' % sales_person)

    return " and ".join(conditions)