import frappe
import datetime
import json
import traceback

def set_sales_person(self):
    if self.user and not self.sales_person and frappe.db.exists("Sales Person", {"user": self.user}):
        self.sales_person = frappe.db.get_value("Sales Person", {"user": self.user}, "name")

def set_employee(self):
    if self.owner and not self.employee:
        if frappe.db.exists("Employee", {"user_id": self.owner}):
            employee, employee_name = frappe.db.get_value("Employee", {"user_id": self.owner},
                                                          ['name', 'employee_name'])
            self.employee = employee
            self.employee_name = employee_name

def set_cheat_status(doc):
    try:
        if '.' in str(doc.server_time):
            doc.server_time = str(doc.server_time).split('.')[0]

        device_datetime = datetime.datetime.strptime(f"{doc.device_date} {doc.device_time}", "%Y-%m-%d %H:%M:%S")
        server_datetime = datetime.datetime.strptime(f"{doc.server_date} {doc.server_time}", "%Y-%m-%d %H:%M:%S")
        time_difference = server_datetime - device_datetime if server_datetime > device_datetime \
            else device_datetime - server_datetime
        tolerance_time = 2 * 60

        if time_difference.seconds > tolerance_time:
            doc.cheated = 1
        else:
            doc.cheated = 0

    except Exception:
        error = f"device_date = {doc.device_date}, device_time = {doc.device_time} \n" \
                f"server_date = {doc.server_date}, server_time = {doc.server_time} \n\n {traceback.format_exc()}"
        frappe.log_error(error, doc.doctype)
        

def set_location_to_map(doc):
    location = {
        "type": "FeatureCollection",
        "features": [
            get_location(doc.latitude, doc.longitude)
        ]
    }

    doc.location = json.dumps(location)


def get_location(latitude, longitude):
    return {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Point",
            "coordinates": [
                latitude,
                longitude
            ]
        }
    }

def set_line_string(doc):
    filters = {
        'user': doc.user,
        'server_date': doc.server_date
    }

    if frappe.db.exists("App User Route", filters):
        routes = frappe.get_list('App User Route', filters, ['name', 'latitude', 'longitude'])
        doc.location['features'].append({
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [
                        doc.latitude,
                        doc.longitude
                    ]
                ]
            }
        })

        for route in routes:
            doc.location['features'].append(get_location(route.latitude, route.longitude))
            doc.location['features'][1]['geometry']['coordinates'].append([route.latitude, route.longitude])