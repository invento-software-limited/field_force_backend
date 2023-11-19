# Copyright (c) 2023, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns, data = get_columns(), get_data(filters)
    return columns, data

def get_data(filters):
    condition = get_conditions(filters)
    
    query = frappe.db.sql("""select dt.name as id, dt.driver_name, dt.driver, dt.territory, date(dt.departure_time) as departure_date,dt.vehicle,
                                      time(dt.departure_time) as departure_time, ds.status, ds.customer, ds.grand_total, ds.address, ds.total_qty
                                         from `tabDelivery Stop` as ds left join `tabDelivery Trip` as dt on dt.name = ds.parent 
                                            where dt.name is not null {}""".format(condition),as_dict=1)
    # return query
    for trip in query:
        set_link_to_doc(trip, 'driver_name','driver',val=trip.get("driver"),color='#006433')
        change_color(trip,"departure_time","darkolivegreen")
        if trip.get("vehicle"):
            vehicle = frappe.get_doc("Vehicle", trip.get("vehicle"))
            labels = vehicle.name +","+ vehicle.model
            set_link_to_doc(trip, 'vehicle','vehicle',val=vehicle.name,label=labels,color='#00918a')
            
    return query
    
    
def get_conditions(filters):
    if not filters: filters = {}
    conditions = ""
    if filters.get("from_date"):
        conditions += " and date(dt.departure_time) >= '{}'".format(filters.get("from_date"))
    if filters.get("to_date"):
        conditions += " and date(dt.departure_time) <= '{}'".format(filters.get("to_date"))
    if filters.get("customer"):
        conditions += " and ds.customer = '{}'".format(filters.get("customer"))
    if filters.get("territory"):
        conditions += " and dt.territory = '{}'".format(filters.get("territory"))
    if filters.get("driver"):
        conditions += " and dt.driver = '{}'".format(filters.get("driver"))
    if filters.get("status"):
        conditions += " and ds.status = '{}'".format(filters.get("status"))
    if filters.get("vehicle"):
        conditions += " and dt.vehicle = '{}'".format(filters.get("vehicle"))
    return conditions


def get_columns():
    return [
            {"label": _("ID"), "fieldtype": "Link", "fieldname": "id","options":"Delivery Trip" ,"width": 160},
            {"label": _("Driver Name"), "fieldtype": "Data","fieldname": "driver_name", "width": 150},
            {"label": _("Departure Date"),"fieldtype": "Date","fieldname": "departure_date","width": 120},
            {"label": _("Departure Time"),"fieldtype": "Data","fieldname":"departure_time","width": 130},
            {"label": _("Territory"),"fieldtype": "Link","fieldname": "territory","options":"Territory","width": 180},
               {"label": _("Customer"), "fieldtype": "Link", "fieldname": "customer","options":"Customer","width": 180},
            {"label": _("Status"), "fieldtype": "Data","fieldname": "status", "width": 120},
            {"label": _("Vehicle"),"fieldtype": "Data","fieldname": "vehicle","width": 180},
            {"label": _("QTY"),"fieldtype": "Float","fieldname": "total_qty","width": 80},
            {"label": _("Address"),"fieldtype": "Data","fieldname":"address","width": 250},
            {"label": _("Grand Total"),"fieldtype": "Currency","fieldname": "grand_total","width": 140}
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
