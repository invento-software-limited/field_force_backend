# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime
from frappe.model.document import Document
from field_force.field_force.doctype.utils import set_employee, set_sales_person


class StoreVisitAssign(Document):
    def validate(self):
        filters = [
            ['name', '!=', self.name],
            ['sales_person', '=', self.sales_person],
            ['date', '=', self.date],
            ['docstatus', '=', 1]
        ]

        if frappe.db.get_list('Store Visit Assign', filters):
            frappe.throw(f"Store Visit already assigned for '{self.sales_person}' at '{self.date}'")

        if self.destinations:
            for destination in self.destinations:
                destination.sales_person = self.sales_person
                destination.employee = self.employee
                destination.user = self.user
                destination.date = self.date

                if not destination.checkin_store_visit:
                    destination.checkin_time = None
                if not destination.checkout_store_visit:
                    destination.checkout_time = None

        self.validate_time()
        self.set_status()
        set_sales_person(self)
        set_employee(self)

    def after_insert(self):
        if self.created_from_app:
            self.submit()

    def validate_time(self):
        for destination in self.destinations:
            if destination.expected_time and isinstance(destination.expected_time, str):
                expected_time = destination.expected_time
                expected_time = expected_time.split('.')[0] if '.' in expected_time else expected_time

                expected_time = datetime.strptime(expected_time, "%H:%M:%S").strftime("%I:%M %p")
                destination.exp_hour = expected_time[:2]
                destination.exp_minute = expected_time[3:5] if expected_time[3:5] in ['00', '15', '30', '45'] else '00'
                destination.exp_format = expected_time[-2:]
                destination.expected_time = get_time_obj(destination.exp_hour, destination.exp_minute,
                                                         destination.exp_format)

            if destination.expected_time_till and isinstance(destination.expected_time_till, str):
                expected_time_till = destination.expected_time_till
                expected_time_till = expected_time_till.split('.')[0] if '.' in expected_time_till else expected_time_till

                expected_time_till = datetime.strptime(expected_time_till, "%H:%M:%S").strftime("%I:%M %p")
                destination.time_till_hour = expected_time_till[:2]
                destination.time_till_minute = expected_time_till[3:5] if expected_time_till[3:5] in ['00', '15', '30', '45'] else '00'
                destination.time_till_format = expected_time_till[-2:]

                destination.expected_time_till = get_time_obj(destination.time_till_hour, destination.time_till_minute,
														  destination.time_till_format)

    def set_status(self):
        visited_stores = frappe.db.exists("Store Visit Destination", {"parent": self.name, "status": "Visited"})
        not_visited_stores = frappe.db.exists("Store Visit Destination", {"parent": self.name, "status": "Not Visited"})

        if visited_stores and not not_visited_stores:
            self.status = "Completed"

        elif visited_stores and not_visited_stores:
            self.status = "Partially"

def get_time_obj(hour, minute, format):
    time = f"{hour}:{minute} {format}"
    time_obj = datetime.strptime(time, "%I:%M %p")
    return time_obj.strftime("%H:%M:%S")
