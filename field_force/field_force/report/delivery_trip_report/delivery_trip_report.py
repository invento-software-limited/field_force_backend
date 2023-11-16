# Copyright (c) 2023, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns, data = get_columns(), get_data(filters)
    card=get_card(data,filters)
    return columns, data,None,None,card

def get_data(filters):
    condition = get_conditions(filters)
    
    query = frappe.db.sql("""select dt.name as id, dt.driver_name, dt.driver, dt.territory, date(dt.departure_time) as departure_date,
                                      time(dt.departure_time) as departure_time, dt.status,dt.vehicle
                                         from `tabDelivery Trip` as dt where dt.name is not null {}""".format(condition),as_dict=1)
    for trip in query:
        set_link_to_doc(trip, 'driver_name','driver',val=trip.get("driver"),color='#006433')
        change_color(trip,"departure_time","#ff00f7")
        if trip.get("vehicle"):
            vehicle = frappe.get_doc("Vehicle", trip.get("vehicle"))
            labels = vehicle.name +","+ vehicle.model
            set_link_to_doc(trip, 'vehicle','vehicle',val=vehicle.name,label=labels,color='#00918a')
            
    return query
    
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
            {"value": cm , "label": _("Completed"), "datatype": "Data","indicator": "Green"},
            {"value": sc,"label": _("Scheduled"),"datatype": "Data","indicator": "Purpel"},
            {"value": it , "label": _("In Transit"), "datatype": "Data","indicator": "Blue"},
            {"value": cn,"label": _("Cancelled"),"datatype": "Data","indicator": "Red"},
            {"value": dt,"label": _("Draft"),"datatype": "Data","indicator": "Orange"},
        
        ]
    
def get_conditions(filters):
    if not filters: filters = {}
    conditions = ""
    if filters.get("from_date"):
        conditions += " and date(dt.departure_time) >= '{}'".format(filters.get("from_date"))
    if filters.get("to_date"):
        conditions += " and date(dt.departure_time) <= '{}'".format(filters.get("to_date"))
    if filters.get("territory"):
        conditions += " and dt.territory = '{}'".format(filters.get("territory"))
    if filters.get("driver"):
        conditions += " and dt.driver = '{}'".format(filters.get("driver"))
    if filters.get("status"):
        conditions += " and dt.status = '{}'".format(filters.get("status"))
    return conditions


def get_columns():
    return [
            {"label": _("ID"), "fieldtype": "Link", "fieldname": "id","options":"Delivery Trip" ,"width": 180},
            {"label": _("Driver Name"), "fieldtype": "Data","fieldname": "driver_name", "width": 200},
            {"label": _("Departure Date"),"fieldtype": "Date","fieldname": "departure_date","width": 140},
            {"label": _("Departure Time"),"fieldtype": "Data","fieldname":"departure_time","width": 140},
            {"label": _("Territory"),"fieldtype": "Link","fieldname": "territory","options":"Territory","width": 200},
            {"label": _("Status"), "fieldtype": "Data","fieldname": "status", "width": 140},
            {"label": _("Vehicle"),"fieldtype": "Data","fieldname": "vehicle","width": 180},
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