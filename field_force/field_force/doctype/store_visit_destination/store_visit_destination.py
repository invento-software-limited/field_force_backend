# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from field_force.field_force.page.utils import get_spent_time

class StoreVisitDestination(Document):
    def validate(self):
        if not self.checkin_store_visit:
            self.checkin_time = None
        if not self.checkout_store_visit:
            self.checkout_time = None

        if self.checkin_time and self.checkout_time:
            self.spent_time = get_spent_time(self.checkin_time, self.checkout_time, in_word=False)

        self.set_status()

    def set_status(self):
        visited_stores = frappe.db.exists("Store Visit Destination", {"parent": self.parent, "status": "Visited", "docstatus": 1})
        not_visited_stores = frappe.db.exists("Store Visit Destination", {"parent": self.parent, "status": "Not Visited", "docstatus": 1})
        status = ""

        if visited_stores and not not_visited_stores:
            status = "Completed"

        elif visited_stores and not_visited_stores:
            status = "Partially"

        if status:
            frappe.db.set_value(self.parenttype, self.parent, 'status', status)
            frappe.db.commit()
