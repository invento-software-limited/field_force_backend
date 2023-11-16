# Copyright (c) 2023, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_data(filters):
    condition = get_conditions(filters)
    
    query = frappe.db.sql("""select dt.name as id, dt.driver_name, dt.driver, dt.territory, date(dt.departure_time) as departure_date,
                          			time(dt.departure_time) as departure_time, dt.status
                             			from `tabDelivery Trip` as dt where dt.name is not null {}""".format(condition),as_dict=1)
    return query
    
    
def get_conditions(filters):
	if not filters: filters = {}
	conditions = ""
	if filters.get("departure_date"):
		conditions += " and date(dt.departure_time) = '{}'".format(filters.get("departure_date"))
	if filters.get("territory"):
		conditions += " and dt.territory = '{}'".format(filters.get("territory"))
	if filters.get("driver"):
		conditions += " and dt.driver = '{}'".format(filters.get("driver"))
	if filters.get("status"):
		conditions += " and dt.status = '{}'".format(filters.get("status"))
	return conditions


def get_columns():
	return [
			{"label": _("ID"), "fieldtype": "Link", "fieldname": "id","options":"Delivery Trip" ,"width": 200},
			{"label": _("Driver Name"), "fieldtype": "Data","fieldname": "driver_name", "width": 200},
			{"label": _("Departure Date"),"fieldtype": "Date","fieldname": "departure_date","width": 200},
			{"label": _("Departure Time"),"fieldtype": "Time","fieldname":"departure_time","width": 200},
			{"label": _("Territory"),"fieldtype": "Link","fieldname": "territory","options":"Territory","width": 200},
			{"label": _("Status"), "fieldtype": "Data","fieldname": "status", "width": 200}
		]