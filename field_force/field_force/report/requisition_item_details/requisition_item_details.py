# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt


import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    requisition_name = ''
    fields = ['transaction_date', 'name', 'customer', 'distributor', 'delivery_date', 'user', 'status', 'company']
    requisition_items = []

    for requisition in data:
        if requisition_name == requisition.name:
            for field in fields:
                requisition[field] = None
        else:
            requisition_name = requisition.name

            if requisition_items:
                requisition_items.append({})

        requisition_items.append(requisition)

    # chart = get_chart(data, filters)
    return columns, requisition_items

def get_columns():
    """ Columns of Report Table"""
    return [
        {"label": _("Date"), "fieldname": "transaction_date", "width": 100},
        {"label": _("Requisition"), "fieldname": "name", "width": 100, "fieldtype": "Link", "options": "Requisition"},
		{"label": _("Customer"), "fieldname": "customer", "width": 100, "fieldtype": "Link", "options": "Customer"},
		# {"label": _("Contact Number"), "fieldname": "contact_number", "width": 120},
		{"label": _("Distributor"), "fieldname": "distributor", "width": 100, "fieldtype": "Link", "options": "Distributor"},
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 100},
        {"label": _("Item Name"), "fieldname": "item_name", "width": 100},
        {"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 80},
        {"label": _("Brand"), "fieldname": "brand", "fieldtype": "Link", "options": "Brand", "width": 80},
        {"label": _("UOM"), "fieldname": "uom", "fieldtype": "Data", "width": 70},
        {"label": _("Unit Price"), "fieldname": "price_list_rate", "fieldtype": "Currency", "width": 100},
        {"label": _("Discount(%)"), "fieldname": "discount_percentage", "fieldtype": "Float", "precision":2, "width": 100},
        {"label": _("Discount Amount"), "fieldname": "discount_amount", "fieldtype": "Currency", "width": 100},
        {"label": _("Quantity"), "fieldname": "qty", "fieldtype": "Int", "width": 80},
        {"label": _("Rate"), "fieldname": "rate", "fieldtype": "Currency", "width": 100},
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 100},
        {"label": _("Delivery Date"), "fieldname": "delivery_date", "width": 100},
		{"label": _("Issued By"), "fieldname": "user", "width": 100, "fieldtype": "Link", "options": "User"},
		{"label": _("Status"), "fieldname": "status", "width": 80},
		{"label": _("Company"), "fieldname": "company", "width": 100, "fieldtype": "Link", "options": "Company"},
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    query_string = """SELECT requisition.name, requisition.transaction_date,requisition.delivery_date, requisition.user,
                    requisition.user_fullname, requisition.customer, requisition.contact_number, requisition.distributor,
                    requisition_item.item_code, requisition_item.item_name, requisition_item.item_group,
                    requisition_item.uom, requisition_item.brand, requisition_item.price_list_rate, requisition_item.qty,
                    requisition_item.discount_percentage, requisition_item.discount_amount, requisition_item.rate,
                    requisition_item.amount, requisition.user, requisition.company, requisition.status
                    from `tabRequisition` requisition left join `tabRequisition Item` requisition_item 
                    on requisition.name=requisition_item.parent where %s order by 
                    requisition.transaction_date desc""" % conditions

    # print(query_string)
    query_result = frappe.db.sql(query_string, as_dict=1, debug=0)
    return query_result


def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    user = filters.get('user')
    customer = filters.get('customer')
    distributor = filters.get('distributor')
    item = filters.get('item')
    company = filters.get('company')
    status = filters.get('status')
    delivery_date = filters.get('delivery_date')

    conditions = []

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
    if status:
        conditions.append("requisition.status = '%s'" % status)
    if delivery_date:
        conditions.append("requisition.delivery_date = '%s'" % delivery_date)

    if item:
        conditions.append("requisition_item.item_code = '%s'" % item)

    return " and ".join(conditions)

#
# def get_chart(data, filters):
#     items_quantity = 20
#     data_ = data if items_quantity == "All" else data[:int(items_quantity)]
#
#     data = {
#         "labels": [item.get("customer") for item in data_],
#         "datasets": [
#             {"name": "Quantity", "values": [item.get("qty") for item in data_]},
#             {"name": "Amount", "values": [item.get("amount")+2000 for item in data_]}
#         ]
#     }
#
#     chart = {
#         "data": data,
#         "isNavigable": 1,
#         "title": "Item Analysis Chart",
#         "type": "line", # or 'bar', 'line', 'pie', 'percentage'
#         "height": 400,
#         "colors": ["purple", "#00c2bb", "light-blue"],
#         "axisOptions": {
#             "xAxisMode": "tick",
#             "xIsSeries": True
#         },
#         "lineOptions": {
#             "regionFill": 1, # default: 0
#             "dotSize": 5 # default: 4
#         },
#         "barOptions": {
#             "stacked": True,
#             "spaceRatio": 1
#         }
#     }
#
#     return chart

