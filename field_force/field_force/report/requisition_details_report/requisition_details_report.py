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
        {"label": _("Date"), "fieldname": "transaction_date", "width": 100},
        {"label": _("ID"), "fieldname": "name", "width": 130, "fieldtype": "Link", "options": "Requisition"},
        {"label": _("Distributor"), "fieldname": "distributor", "width": 120, "fieldtype": "Link",
         "options": "Distributor"},
		{"label": _("Customer"), "fieldname": "customer", "width": 200, "fieldtype": "Link", "options": "Customer"},
		{"label": _("Territory"), "fieldname": "territory", "width": 120, "fieldtype": "Link", "options": "Territory"},
        {"label": _("PO Number"), "fieldname": "po_no", "width": 120},
        {"label": _("Delivery Date"), "fieldname": "delivery_date", "width": 110},
        # {"label": _("Total Items"), "fieldname": "total_items", "width": 100},
        {"label": _("Total Qty"), "fieldname": "total_qty", "fieldtype": "Int", "width": 100},
        {"label": _("Total Amount"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 150},
        {"label": _("Sales Person"), "fieldname": "sales_person", "fieldtype": "Link", "options":"Sales Person", "width": 120},
        {"label": _("Status"), "fieldname": "status", "width": 80, "fieldtype": "Data"},
        {"label": _("Company"), "fieldname": "company", "width": 140, "fieldtype": "Link", "options": "Company"},
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    query_string = '''select
                        requisition.name,
                        requisition.transaction_date,
                        requisition.delivery_date,
                        requisition.sales_person,
                        requisition.customer,
                        requisition.po_no,
                        requisition.distributor,
                        requisition.territory,
                        requisition.total_items,
                        requisition.total_qty,
                        requisition.grand_total as total_amount,
                        requisition.status, requisition.company
                from `tabRequisition` requisition where %s order by requisition.transaction_date desc''' % conditions

    query_result = frappe.db.sql(query_string, as_dict=1, debug=0)
    return query_result


def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    sales_person = filters.get('sales_person')
    customer = filters.get('customer')
    distributor = filters.get('distributor')
    territory = filters.get('territory')
    company = filters.get('company')
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
    if distributor:
        conditions.append('requisition.distributor = "%s"' % distributor)
    if territory:
        conditions.append('requisition.territory = "%s"' % territory)
    if company:
        conditions.append('requisition.company = "%s"' % company)

    return " and ".join(conditions)
