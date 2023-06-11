# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from field_force.field_force.doctype.utils import set_cheat_status, set_location_to_map, set_sales_person, set_employee

class MerchandisingPicture(Document):
    def validate(self):
        # if frappe.session.user != 'administrator':
        # 	self.user = frappe.session.user

        if not self.email or not self.user_fullname:
            email, user_fullname = frappe.db.get_value('User', self.user, ['email', 'full_name'])

            if not self.email and email:
                self.email = email
            if not self.user_fullname and user_fullname:
                self.user_fullname = user_fullname

        if not self.contact_number or not self.customer_address:
            contact_number, customer_address = frappe.db.get_value('Customer', self.customer, ['contact_number', 'address'])

            if not self.contact_number and contact_number:
                self.contact_number = contact_number
            if not self.customer_address and customer_address:
                self.customer_address = customer_address

        set_sales_person(self)
        set_employee(self)
        set_cheat_status(self)

    def before_save(self):
        self.add_feedback_from()
        set_location_to_map(self)

    def add_feedback_from(self):
        if self.feedback:
            previous_doc = self.get_doc_before_save()

            if previous_doc:
                previous_feedback = previous_doc.get('feedback')

                if previous_feedback != self.feedback \
                    and frappe.db.exists("Sales Person", {"user": frappe.session.user}):
                    self.feedback_from = frappe.db.get_value("Sales Person", {"user": frappe.session.user}, 'name')
                else:
                    self.feedback_from = None
        else:
            self.feedback_from = None
