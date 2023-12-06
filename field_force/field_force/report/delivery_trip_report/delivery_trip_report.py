# Copyright (c) 2023, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from field_force.field_force.page.utils import *


def execute(filters=None):
    columns, data = get_columns(), get_data(filters)
    card=get_card(data,filters)
    return columns, data,None,None,card

def get_data(filters):
    condition = {"name": ["!=", 'null']}
    condition.update(get_conditions(filters))
    print(condition)
    fields = ["name as id", "driver_name", "driver", "territory", "departure_time", "status", "vehicle"]
    query = frappe.get_list("Delivery Trip", condition , fields)

    # query = frappe.db.sql("""select dt.name as id, dt.driver_name, dt.driver, dt.territory, date(dt.departure_time) as departure_date,
    #                                   time(dt.departure_time) as departure_time, dt.status,dt.vehicle
    #                                      from `tabDelivery Trip` as dt where dt.name is not null {}""".format(condition),as_dict=1)

    for trip in query:
        set_link_to_doc(trip, 'driver_name','driver',val=trip.get("driver"),color='#006433')
        trip['departure_date'] = frappe.format(trip.departure_time, {'fieldtype': 'Date'})
        trip['departure_time'] = get_time_in_12_hour_format(frappe.format(trip.departure_time, {'fieldtype': 'Time'}))

        change_color(trip,"departure_date","#0099cc")
        change_color(trip,"departure_time","#0099cc")
        set_link_to_doc(trip,"id","delivery-trip", trip.id, color="blue")
        set_link_to_doc(trip,"territory","territory", trip.territory, color="#0080ff")

        if trip.get("vehicle"):
            vehicle = frappe.get_doc("Vehicle", trip.get("vehicle"))
            labels = vehicle.name +","+ vehicle.model
            set_link_to_doc(trip, 'vehicle','vehicle',val=vehicle.name,label=labels,color='#00918a')

    return query


def get_conditions(filters):
    if not filters: filters = {}
    conditions = {}

    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    if from_date and to_date:
        conditions["departure_time"] = ["between", [from_date, to_date]]
    elif from_date:
        conditions["departure_time"] = [">=", from_date]
    elif to_date:
        conditions["departure_time"] = ["<=", to_date]

    if filters.get("territory"):
        conditions["territory"] = filters.get("territory")
    if filters.get("driver"):
        conditions["driver"] = filters.get("driver")
    if filters.get("status"):
        conditions["status"] = filters.get("status")

    return conditions


def get_columns():
    return [
        {"label": _("ID"), "fieldtype": "Data", "fieldname": "id","options":"Delivery Trip" ,"width": 150},
        {"label": _("Territory"), "fieldtype": "Data", "fieldname": "territory", "options": "Territory", "width": 210},
        {"label": _("Driver Name"), "fieldtype": "Data","fieldname": "driver_name", "width": 210},
        {"label": _("Departure Date"), "fieldtype": "Data","fieldname": "departure_date","width": 140},
        {"label": _("Departure Time"),"fieldtype": "Data","fieldname":"departure_time","width": 140},
        {"label": _("Status"), "fieldtype": "Data","fieldname": "status", "width": 140},
        {"label": _("Vehicle"),"fieldtype": "Data","fieldname": "vehicle","width": 200},
    ]

def get_card(data,filters):
    cm,cn,it,sc,dt = 0,0,0,0,0

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
        return {"value": it,"label": _("In Transit"),"datatype": "Data","indicator": "Blue"},
    elif filters.get("status") == "Scheduled":
        return {"value": sc,"label": _("Scheduled"),"datatype": "Data","indicator": "Purpel"},
    elif filters.get("status") == "Completed":
        return {"value": cm,"label": _("Completed"),"datatype": "Data","indicator": "Orange"},
    elif filters.get("status") == "Cancelled":
        return {"value": cn,"label": _("Cancelled"),"datatype": "Data","indicator": "Orange"},
    elif filters.get("status") == "Draft":
        return {"value": dt,"label": _("Draft"),"datatype": "Data","indicator": "Orange"},
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

def change_color(doc,field,color):
    style = f'style="color:{color};"' if color else ''

    doc[field] = f'''<span %s>{doc[field] or "" }</span>''' % style

    return doc[field]
