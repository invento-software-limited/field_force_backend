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
            ['date', '=', self.date]
        ]

        if frappe.db.get_list('Store Visit Assign', filters):
            frappe.throw(f"Store Visit is already assigned for user '{self.sales_person}' at '{self.date}'")

        if self.destinations:
            for destination in self.destinations:
                destination.sales_person = self.sales_person
                destination.employee = self.employee
                destination.user = self.user
                destination.date = self.date

        set_sales_person(self)
        set_employee(self)
        self.validate_time()

    def validate_time(self):
        for destination in self.destinations:
            destination.expected_time = get_time_obj(destination.exp_hour, destination.exp_minute, destination.exp_format)
            destination.expected_time_till = get_time_obj(destination.time_till_hour, destination.time_till_minute,
														  destination.time_till_format)

def get_time_obj(hour, minute, format):
    time = f"{hour}:{minute} {format}"
    time_obj = datetime.strptime(time, "%I:%M %p")
    return time_obj.strftime("%H:%M:%S")
