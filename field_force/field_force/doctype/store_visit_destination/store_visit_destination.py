# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from field_force.field_force.page.utils import get_spent_time

class StoreVisitDestination(Document):
    def validate(self):
        if self.checkin_time and self.checkout_time:
            self.spent_time = get_spent_time(self.checkin_time, self.checkout_time, in_word=False)
