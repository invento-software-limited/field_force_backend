import frappe

@frappe.whitelist()
def set_customer_group(self, method):
    if not self.customer_group:
        self.customer_group = 'Retail Shop'

@frappe.whitelist()
def create_distributor(self, method):
    if self.customer_group == 'Distributor':
        if not self.created_from_distributor and (not self.distributor and not frappe.db.exists('Distributor', self.name)):
            distributor_info = {
                'doctype': 'Distributor',
                'distributor_name': self.name,
                'sales_person': self.sales_person,
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
            distributor.save()
@frappe.whitelist()
def set_employee(self, method):
    if self.owner and not self.employee:
        if frappe.db.exists("Employee", {"user_id": self.owner}):
            employee, employee_name = frappe.db.get_value("Employee", {"user_id": self.owner}, ['name', 'employee_name'])
            self.employee = employee
            self.employee_name = employee_name