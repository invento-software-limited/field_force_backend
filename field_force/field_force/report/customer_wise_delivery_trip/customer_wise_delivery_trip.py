# Copyright (c) 2023, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from field_force.field_force.page.utils import *


def execute(filters=None):
    columns, data = get_columns(), get_data(filters)
    card=get_card(data,filters)
    return columns, data, None, None, card

def get_data(filters):
    condition = get_conditions(filters)
    customers = frappe.get_list("Customer", filters={"disabled": 0}, pluck='name')
    customers_in_tuple_str = '("' + '", "'.join(customers) + '")'

    query = frappe.db.sql('''select dt.name as id, dt.driver_name, dt.driver, dt.territory, ds.requisition,
                        date(dt.departure_time) as departure_date, dt.vehicle, time(dt.departure_time) as departure_time,
                         ds.status, ds.customer, ds.grand_total, ds.address, ds.total_qty
                        from `tabDelivery Stop` as ds left join `tabDelivery Trip` as dt on dt.name = ds.parent
                        where dt.name is not null and ds.customer in {} {}
                        order by departure_time desc'''.format(customers_in_tuple_str, condition),as_dict=1)

    # return query
    for trip in query:
        trip['departure_time'] = get_time_in_12_hour_format(str(trip.departure_time))
        change_color(trip,"departure_date","#0099cc")
        change_color(trip,"departure_time","#0099cc")

        if trip.requisition:
            set_link_to_doc(trip, 'requisition','requisition',val=trip.requisition, color='blue')

        set_link_to_doc(trip, 'id','delivery-trip',val=trip.id, color='blue')
        set_link_to_doc(trip, 'customer','customer',val=trip.customer, color='#0080ff')
        set_link_to_doc(trip, 'territory','territory',val=trip.territory, color='#0080ff	')
        set_link_to_doc(trip, 'driver_name','driver',val=trip.driver, color='#0080ff	')

        if trip.get("vehicle"):
            vehicle = frappe.get_doc("Vehicle", trip.get("vehicle"))
            labels = vehicle.name +","+ vehicle.model
            set_link_to_doc(trip, 'vehicle','vehicle',val=vehicle.name,label=labels,color='#00918a')

    return query


def get_conditions(filters):
    if not filters: filters = {}
    conditions = ''

    if filters.get("from_date"):
        conditions += ' and date(dt.departure_time) >= "{}"'.format(filters.get("from_date"))
    if filters.get("to_date"):
        conditions += ' and date(dt.departure_time) <= "{}"'.format(filters.get("to_date"))
    if filters.get("customer"):
        conditions += ' and ds.customer = "{}"'.format(filters.get("customer"))
    if filters.get("territory"):
        conditions += ' and dt.territory = "{}"'.format(filters.get("territory"))
    if filters.get("driver"):
        conditions += ' and dt.driver = "{}"'.format(filters.get("driver"))
    if filters.get("status"):
        conditions += ' and ds.status = "{}"'.format(filters.get("status"))
    if filters.get("vehicle"):
        conditions += ' and dt.vehicle = "{}"'.format(filters.get("vehicle"))

    return conditions


def get_columns():
    columns =  [
        {"label": _("Customer"), "fieldtype": "Data", "fieldname": "customer", "options": "Customer", "width": 180},
        {"label": _("Dep. Date"),"fieldtype": "Data","fieldname": "departure_date","width": 100},
        {"label": _("Dep. Time"),"fieldtype": "Data","fieldname":"departure_time","width": 90},
        {"label": _("Territory"),"fieldtype": "Data","fieldname": "territory","options":"Territory","width": 120},
        {"label": _("Status"), "fieldtype": "Data","fieldname": "status", "width": 80},
        {"label": _("Vehicle"),"fieldtype": "Data","fieldname": "vehicle","width": 120},
        {"label": _("Driver Name"), "fieldtype": "Data", "fieldname": "driver_name", "width": 120},
        {"label": _("Address"),"fieldtype": "Data","fieldname":"address","width": 200},
        {"label": _("QTY"), "fieldtype": "Int", "fieldname": "total_qty", "width": 80},
        {"label": _("Grand Total"),"fieldtype": "Currency","fieldname": "grand_total","width": 100}
    ]

    if 'Customer' in frappe.get_roles(frappe.session.user):
        columns.insert(
        0,{"label": _("Requisition ID"), "fieldtype": "Data", "fieldname": "requisition", "options":"Requisition" ,"width": 120})
    else:
        columns.insert(
        0,{"label": _("Trip ID"), "fieldtype": "Data", "fieldname": "id","options":"Delivery Trip" ,"width": 120})

    return  columns


def get_card(data, filters):
    cm, cn, it, sc, dt = 0, 0, 0, 0, 0

    for x in data:
        if x.get("status") == "In Transit":
            it += 1
        elif x.get("status") == "Scheduled":
            sc += 1
        elif x.get("status") == "Completed":
            cm += 1
        elif x.get("status") == "Cancelled":
            cn += 1
        elif x.get("status") == "Draft":
            dt += 1

    if filters.get("status") == "In Transit":
        return {"value": it, "label": _("In Transit"), "datatype": "Data", "indicator": "Blue"},
    elif filters.get("status") == "Scheduled":
        return {"value": sc, "label": _("Scheduled"), "datatype": "Data", "indicator": "Purpel"},
    elif filters.get("status") == "Completed":
        return {"value": cm, "label": _("Completed"), "datatype": "Data", "indicator": "Orange"},
    elif filters.get("status") == "Cancelled":
        return {"value": cn, "label": _("Cancelled"), "datatype": "Data", "indicator": "Orange"},
    elif filters.get("status") == "Draft":
        return {"value": dt, "label": _("Draft"), "datatype": "Data", "indicator": "Orange"},
    else:
        return [
            {"value": dt, "label": _("Draft"), "datatype": "Data", "indicator": "Orange"},
            {"value": sc, "label": _("Scheduled"), "datatype": "Data", "indicator": "Purpel"},
            {"value": it, "label": _("In Transit"), "datatype": "Data", "indicator": "Blue"},
            {"value": cm, "label": _("Completed"), "datatype": "Data", "indicator": "Green"},
            {"value": cn, "label": _("Cancelled"), "datatype": "Data", "indicator": "Red"},
        ]


def set_link_to_doc(doc, field, doc_url='',val=None, label=None, color=None):
    style = f'style="color:{color};"' if color else ''

    doc[field] = f'''<a href="/app/{doc_url}/{val}" target="_blank" %s>
                        {label or doc[field]}
                    </a>
                ''' % style
    return doc[field]

def change_color(doc, field, color):
    style = f'style="color:{color};"' if color else ''

    doc[field] = f'''<span %s>{doc[field] or "" }</span>''' % style

    return doc[field]
