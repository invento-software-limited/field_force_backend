# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt
import datetime

import frappe
from field_force.field_force.report.utils import set_user_link
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    sales_order_name = ''
    sales_order_items = []
    subtotal = get_subtotal()
    date_wise_total = {}
    item_count = 0

    for sales_order_item in data:
        # date_wise_total = set_date_wise_qty_and_amount(date_wise_total, sales_order_item)

        if sales_order_name == sales_order_item.name:
            sales_order_item.transaction_date = None
            sales_order_item.name = None
            sales_order_item.customer = None
            sales_order_item.distributor = None
            sales_order_item.delivery_date = None
            sales_order_item.sales_person = None
            sales_order_item.grand_total = None
            sales_order_item.status = None
            sales_order_item.company = None
        else:
            sales_order_name = sales_order_item.name
            # set_user_link(sales_order_item)

            if item_count > 1:
                # sales_order_items.append(subtotal)
                subtotal = get_subtotal()
                item_count = 0

            # if sales_order_items:
            #     sales_order_items.append({})

        subtotal['qty'] += sales_order_item.qty
        subtotal['amount'] += sales_order_item.amount

        sales_order_items.append(sales_order_item)
        item_count += 1

    # if item_count > 1:
    #     sales_order_items.append(subtotal)

    chart = get_chart(data, date_wise_total, filters)
    return columns, sales_order_items, '', chart

def set_date_wise_qty_and_amount(date_wise_total, sales_order_item):
    transaction_date = str(sales_order_item.transaction_date)

    if transaction_date not in date_wise_total.keys():
        date_wise_total[transaction_date] = {
            'qty': sales_order_item.qty,
            'amount': sales_order_item.amount
        }
    else:
        date_wise_total[transaction_date]['qty'] += sales_order_item.qty
        date_wise_total[transaction_date]['amount'] += sales_order_item.amount

    return date_wise_total

def get_date_list(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')

    from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d")
    to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d")

    date_list = [str(from_date)]
    date = from_date

    while date <= to_date:
        date = date + datetime.timedelta(days=1)
        date_list.append(str(date.date()))

    return date_list

def get_subtotal():
    return {
        'uom': "Total = ",
        'qty':0,
        'amount': 0
    }

def get_columns():
    """ Columns of Report Table"""
    return [
        {"label": _("Date"), "fieldname": "transaction_date", "width": 100},
        {"label": _("ID"), "fieldname": "name", "width": 130, "fieldtype": "Link", "options": "Sales Order"},
        {"label": _("Distributor"), "fieldname": "distributor", "width": 120, "fieldtype": "Link",
         "options": "Distributor"},
        {"label": _("Customer"), "fieldname": "customer", "width": 200, "fieldtype": "Link", "options": "Customer"},
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
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
        {"label": _("Total"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 100},
        {"label": _("Delivery Date"), "fieldname": "delivery_date", "width": 100},
        {"label": _("Sales Person"), "fieldname": "sales_person", "fieldtype": "Link", "options": "Sales Person",
         "width": 100},
        {"label": _("Status"), "fieldname": "status", "width": 80},
		{"label": _("Company"), "fieldname": "company", "width": 100, "fieldtype": "Link", "options": "Company"},
    ]


def get_data(filters):
    conditions = get_conditions(filters)
    status = filters.get('status')

    query_string = '''SELECT sales_order.name, sales_order.transaction_date,sales_order.delivery_date,
                    sales_order.sales_person, sales_order.customer, sales_order.contact_number, sales_order.distributor,
                    sales_order.grand_total, sales_order_item.item_code, sales_order_item.item_name, sales_order_item.item_group,
                    sales_order_item.uom, sales_order_item.brand, sales_order_item.price_list_rate, sales_order_item.qty,
                    sales_order_item.discount_percentage, sales_order_item.discount_amount, sales_order_item.rate,
                    sales_order_item.amount, sales_order.user, sales_order.company, "%s" as status
                    from `tabSales Order` sales_order left join `tabSales Order Item` sales_order_item 
                    on sales_order.name=sales_order_item.parent where %s order by 
                    sales_order.transaction_date desc''' % (status, conditions)

    # print(query_string)
    query_result = frappe.db.sql(query_string, as_dict=1, debug=0)
    return query_result


def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    sales_person = filters.get('sales_person')
    customer = filters.get('customer')
    distributor = filters.get('distributor')
    item = filters.get('item')
    company = filters.get('company')
    status = filters.get('status')
    delivery_date = filters.get('delivery_date')

    status_dict = {
        "Draft": 0,
        "Submitted": 1,
        "Cancelled": 2
    }

    conditions = []

    if status:
        conditions.append('sales_order.docstatus = %s' % status_dict.get(status))
    if from_date:
        conditions.append('sales_order.transaction_date >= "%s"' % from_date)
    if to_date:
        conditions.append('sales_order.transaction_date <= "%s"' % to_date)
    if sales_person:
        conditions.append('sales_order.sales_person = "%s"' % sales_person)
    if customer:
        conditions.append('sales_order.customer = "%s"' % customer)
    if distributor:
        conditions.append('sales_order.distributor = "%s"' % distributor)
    if company:
        conditions.append('sales_order.company = "%s"' % company)

    if delivery_date:
        conditions.append('sales_order.delivery_date = "%s"' % delivery_date)

    if item:
        conditions.append('sales_order_item.item_code = "%s"' % item)

    return " and ".join(conditions)

def get_chart(data, date_wise_total, filters):
    date_list = get_date_list(filters)
    qty_list = []
    amount_list = []

    for date in date_list:
        if date in date_wise_total.keys():
            qty_list.append(date_wise_total[date]['qty'])
            amount_list.append(date_wise_total[date]['amount'])
        else:
            qty_list.append(0)
            amount_list.append(0)

    data = {
        # "labels": customers,
        "labels": date_list,
        "datasets": [
            {"name": "Quantity", "values": qty_list},
            {"name": "Amount", "values": amount_list}
        ]
    }

    chart = {
        "data": data,
        "isNavigable": True,
        "title": "Sales Order Item Analysis Chart",
        "type": "line", # or 'bar', 'line', 'pie', 'percentage'
        "height": 300,
        "colors": ["purple", "#00c2bb", "light-blue"],
        "axisOptions": {
            "xAxisMode": "tick", # default: span
            "xIsSeries": True
        },
        "lineOptions": {
            "regionFill": 1, # default: 0
            "dotSize": 5, # default: 4
            # "hideLine": 1 # default: 0
        },
        # "barOptions": {
        #     "stacked": False,
        #     "spaceRatio": 1
        # }
    }

    return chart

