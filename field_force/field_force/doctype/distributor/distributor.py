# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Distributor(Document):

    def validate(self):
        partner_group_name = self.distributor_name

        if not frappe.db.exists('Partner Group', self.distributor_name):
            partner_group = frappe.get_doc({
                "doctype": "Partner Group",
                "partner_group_name": self.distributor_name
            }).insert()
            partner_group_name = partner_group.name
        #
        # if self.name != self.customer:
        #     frappe.rename_doc("Distributor", self.name, self.customer)

        if not self.customer and frappe.db.exists('Customer', self.distributor_name):
            self.customer = self.distributor_name

        elif not self.customer:
            customer = {
                'doctype': 'Customer',
                'customer_name': self.distributor_name,
                'customer_group': 'Distributor',
                'partner_group': partner_group_name,
                'distributor_name': self.distributor_name,
                'sales_person': self.sales_person,
                'contact_person': self.contact_person,
                'contact_number': self.contact_number,
                'address': self.address,
                'email_address': self.email_address,
                'thana': self.thana,
                'zip_code': self.zip_code,
                'latitude': self.latitude,
                'longitude': self.longitude,
                'created_from_distributor': 1
            }
            customer = frappe.get_doc(customer)
            customer.insert()

            self.customer = customer.name
            self.customer_name = customer.customer_name

    # def after_save(self):
    #     customer_info = {
    #         'contact_person': self.contact_person,
    #         'contact_number': self.contact_number,
    #         'address': self.address,
    #         'email_address': self.email_address,
    #         'thana': self.thana,
    #         'zip_code': self.zip_code,
    #         'latitude': self.latitude,
    #         'longitude': self.longitude
    #     }
    #
    #     customer = frappe.get_doc('Customer', self.name)
    #     customer.update(customer_info)
    #     customer.save()

def after_rename(new_doc, method, old_name, merge=False, ignore_permissions=False):
    related_doctype = "Customer"

    if frappe.db.exists(related_doctype, {'name': old_name}):
        if old_name != new_doc.name:
            frappe.rename_doc(related_doctype, old_name, new_doc.name)
