import frappe

@frappe.whitelist()
def set_customer_group(self, method):
    if self.distributor:
        self.customer_group = 'Retail Shop'

@frappe.whitelist()
def create_distributor(self, method):
    if self.customer_group == 'Distributor':
        if not frappe.db.exists('Distributor', self.name):
            distributor_info = {
                'doctype': 'Distributor',
                'distributor_name': self.name,
                'customer': self.name,
                'contact_person': self.contact_person,
                'contact_number': self.contact_number,
                'address': self.address,
                'email_address': self.email_address,
                'thana': self.thana,
                'zip_code': self.zip_code,
                'latitude': self.latitude,
                'longitude': self.longitude
            }
            distributor = frappe.get_doc(distributor_info)
            distributor.insert()
