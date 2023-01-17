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
        {"label": _(" Requisition Date"), "fieldname": "transaction_date", "width": 130},
        {"label": _("Partner"), "fieldname": "partner_group", "width": 150, "fieldtype": "Link", "options": "Requisition"},
		{"label": _("Outlet Name"), "fieldname": "customer", "width": 240, "fieldtype": "Link", "options": "Customer"},
		{"label": _("PO Number"), "fieldname": "po_no", "width": 120},
        {"label": _("Sales Person"), "fieldname": "sales_person", "fieldtype": "Link", "options": "Sales Person",
         "width": 150},
        {"label": _("Delivered Date"), "fieldname": "delivered_date", "fieldtype": "Date", "width": 120},
        {"label": _("Requisition Amount"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 150},
        {"label": _("Delivered Amount"), "fieldname": "delivered_amount", "fieldtype": "Currency", "width": 150},
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    query_string = '''select 
                        requisition.name,
                        requisition.transaction_date,
                        requisition.partner_group,
                        requisition.po_no,
                        requisition.delivered_date,
                        requisition.delivered_amount,
                        requisition.sales_person,
                        requisition.customer, 
                        requisition.grand_total as total_amount
                    from `tabRequisition` requisition
                    where %s order by requisition.transaction_date desc''' % conditions

    query_result = frappe.db.sql(query_string, as_dict=1, debug=0)
    return query_result


def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    sales_person = filters.get('sales_person')
    customer = filters.get('customer')
    partner_group = filters.get('partner_group')
    status = filters.get('status')

    conditions = [
        'requisition.status = "%s"' % status
    ]

    if from_date:
        conditions.append('requisition.transaction_date >= "%s"' % from_date)
    if to_date:
        conditions.append('requisition.transaction_date <= "%s"' % to_date)
    if sales_person:
        conditions.append('requisition.sales_person = "%s"' % sales_person)
    if customer:
        conditions.append('requisition.customer = "%s"' % customer)
    if partner_group:
        conditions.append('requisition.partner_group = "%s"' % partner_group)

    return " and ".join(conditions)