import frappe
import datetime
import json
import traceback
import frappe
import PyPDF2
import os
import re
from erpnext.controllers.queries import item_query
from erpnext.stock.utils import scan_barcode


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


@frappe.whitelist()
def get_data_from_pdf(url, end_page=None):
    data = []
    try:
        pdfFileObj = open(get_site_directory_path() + "/public" + url, 'rb')

        if pdfFileObj:
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
            text = ""
            for page_number in range(pdfReader.numPages):
                pageObj = pdfReader.getPage(page_number)
                text += pageObj.extractText()
            data_list = text.split("\n")
            for x in range(1, 50):
                try:
                    data_list.index(str(x))
                    start_index = data_list.index(str(x))
                    try:
                        data_list.index(str(x + 1))
                        end_index = data_list.index(str(x + 1))
                    except:
                        end_index = data_list.index("Net")
                    if start_index and end_index:
                        item_list = data_list[int(start_index):int(end_index)]
                        f_data = get_item_details_data(item_list)
                        data.append(f_data)
                except:
                    pass
    except:
        frappe.msgprint(str("Wrong URL, No such file <b>{}</b>".format(url)))

    return data


def get_item_details_data(item_list):
    data_dict = {}
    middle = 0
    data_dict["item_code"] = item_list[1]
    values = ()
    fields = ['item_code', 'item_name', 'brand', 'image']

    try:
        item_data = scan_barcode(data_dict['item_code'])
        values = frappe.db.get_value("Item", item_data.item_code, fields)
    except:
        pass

    if not values:
        try:
            values = frappe.get_value("Item", data_dict['item_code'], fields)
        except:
            values_ = frappe.db.sql('''select item_code, item_name, brand, image
                                    from `tabItem` where product_id="%s"''' % data_dict["item_code"])
            if values_:
                values = values_[0]

    if values:
        data_dict['item_code'], data_dict['item_name'], data_dict['brand'], data_dict['image'] = values


    for item in item_list:
        try:
            num = int(item)
        except ValueError:
            try:
                num = float(item)
                middle += item_list.index(item)
                data_dict["qty"] = float(item)
                break
            except ValueError:
                pass

    last_part = item_list[middle + 1: len(item_list)]

    for item in last_part:
        try:
            num = int(item)
        except ValueError:
            try:
                num = float(item)
                data_dict["rate"] = float(item)
                break
            except ValueError:
                pass

    return data_dict


def get_site_directory_path():
    site_name = frappe.local.site
    cur_dir = os.getcwd()
    return os.path.join(cur_dir, site_name)
