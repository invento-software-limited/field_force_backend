import frappe

def validate(self, method):
    # self._original = self.get_doc_before_save()
    set_customer_group(self, method)
    set_sales_person_and_employee(self, method)

def after_insert(self, method):
    create_distributor(self, method)
    add_customer_to_sales_person(self)

def before_save(self, method):
    self.previous_doc = self.get_doc_before_save()
    create_or_update_distributor(self, method)

def on_update(self, method):
    if self.previous_doc:
        if self.previous_doc.sales_person != self.sales_person:
            # delete_customer_from_previous_sales_person(self)
            add_customer_to_sales_person(self)
            frappe.db.commit()

def create_or_update_distributor(self, method):
    doctype = "Distributor"

    if self.customer_group == "Distributor" and frappe.db.exists(doctype, {'customer':self.name}):
        customer_info = {
            'contact_person': self.contact_person,
            'contact_number': self.contact_number,
            'address': self.address,
            'email_address': self.email_address,
            'thana': self.thana,
            'zip_code': self.zip_code,
            'latitude': self.latitude,
            'longitude': self.longitude
        }

        distributor = frappe.get_doc(doctype, {'customer': self.name})
        distributor.update(customer_info)

        if self.sales_person != distributor.sales_person:
            distributor.sales_person = self.sales_person
            distributor.save()
    else:
        create_distributor(self, method)

def add_customer_to_sales_person(self):
    if self.sales_person and self.sales_person != 'Sales Team':
        filters = {
            "customer": self.name,
            "parent": self.sales_person
        }

        if not frappe.db.exists("Sales Person Customer", filters):
            sales_person = frappe.get_doc("Sales Person", self.sales_person)

            if self.customer_group == 'Distributor' and sales_person.type == 'Sales Representative':
                sales_person.distributor = self.name
            else:
                sales_person.append('customers', {
                    "doctype": "Sales Person Customer",
                    "parenttype": "Sales Person",
                    "parent": self.sales_person,
                    "customer": self.name
                })

            sales_person.save()

def delete_customer_from_previous_sales_person(self):
    if self.previous_doc:
        filters = {
            "customer": self.name,
            "parent": self.previous_doc.sales_person
        }

        if frappe.db.exists("Sales Person Customer", filters):
            sales_person_customer = frappe.get_doc("Sales Person Customer", filters)
            sales_person_customer.delete()


def set_customer_group(self, method):
    if not self.customer_group:
        self.customer_group = 'Retail Shop'

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

# def set_employee(self, method):
#     if self.owner and not self.employee:
#         if frappe.db.exists("Employee", {"user_id": self.owner}):
#             employee, employee_name = frappe.db.get_value("Employee", {"user_id": self.owner}, ['name', 'employee_name'])
#             self.employee = employee
#             self.employee_name = employee_name

@frappe.whitelist()
def enqueue_refresh_sales_person_customers():
    frappe.enqueue(method='field_force.field_force.hook_functions.customer.refresh_sales_person_customers')
    frappe.msgprint("Refreshing All Sales Person's Customer List..")

@frappe.whitelist()
def refresh_sales_person_customers():
    doctype = "Sales Person Customer"
    customers = frappe.db.get_list("Customer", fields=['name', 'sales_person', 'customer_group'])

    for customer in customers:
        try:
            # print("=====>>", customer)
            filters = {
                "customer": customer.name,
                "parent": ["!=", customer.sales_person]
            }

            # deleting from previous sales persons
            deletable_customers = frappe.get_list(doctype, filters, 'name')

            for sales_person_customer in deletable_customers:
                sales_person_customer = frappe.get_doc(doctype, sales_person_customer.name)
                sales_person_customer.delete()

            # adding customers to sales person
            if customer.sales_person and customer.sales_person != 'Sales Team':
                filters['parent'] = customer.sales_person

                if not frappe.db.exists("Sales Person Customer", filters):
                    sales_person = frappe.get_doc("Sales Person", customer.sales_person)

                    if customer.customer_group == 'Distributor' and sales_person.type == 'Sales Representative':
                        sales_person.distributor = customer.name
                    else:
                        sales_person.append('customers', {
                            "doctype": "Sales Person Customer",
                            "parenttype": "Sales Person",
                            "parent": customer.sales_person,
                            "customer": customer.name
                        })

                    sales_person.save()
                    # print(customer.name, "=====added to====>>", customer.sales_person)

            frappe.db.commit()
        except:
            frappe.log_error(frappe.get_traceback(), f"{customer.name}-{customer.sales_person}")
