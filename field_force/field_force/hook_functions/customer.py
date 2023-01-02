import frappe

@frappe.whitelist()
def set_customer_group(self, method):
    if not self.customer_group:
        self.customer_group = 'Retail Shop'

@frappe.whitelist()
def set_sales_person_and_employee(self, method):
    if not self.sales_person:
        if frappe.db.exists("Sales Person", {"user": frappe.session.user}):
            self.sales_person, self.employee = frappe.db.get_value("Sales Person", {"user": frappe.session.user},
                                                                   ['name', 'employee'])
        else:
            self.sales_person, self.employee = 'Sales Team', None

# def set_partner_group(self, method):
    # if not self.partner_group:
    #     if frappe.db.exists("Partner Group", {'name': self.name}):
    #         self.partner_group = self.name
    #     else:
    #         partner_group = frappe.get_doc({
    #             "doctype": "Partner Group",
    #             "partner_group_name": self.name
    #         }).insert()
    #         self.partner_group = partner_group


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

# @frappe.whitelist()
# def set_employee(self, method):
#     if self.owner and not self.employee:
#         if frappe.db.exists("Employee", {"user_id": self.owner}):
#             employee, employee_name = frappe.db.get_value("Employee", {"user_id": self.owner}, ['name', 'employee_name'])
#             self.employee = employee
#             self.employee_name = employee_name