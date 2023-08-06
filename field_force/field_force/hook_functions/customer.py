import random

import frappe

def validate(self, method):
    set_customer_group(self, method)
    set_sales_person_and_employee(self, method)
    generate_customer_id(self, method)

def after_insert(self, method):
    create_distributor(self, method)
    add_customer_to_sales_person(self)
    update_brand_commissions(self)

def before_save(self, method):
    self.previous_doc = self.get_doc_before_save()

def on_update(self, method):
    if self.previous_doc:
        create_or_update_distributor(self, method)
        update_brand_commissions(self)

        if self.previous_doc.sales_person != self.sales_person:
            delete_customer_from_previous_sales_person(self)
            add_customer_to_sales_person(self)
            frappe.db.commit()

def generate_customer_id(self, method):
    if not self.customer_id and self.customer_group == "Retail Shop" and self.distributor:
        customer = frappe.db.get_value("Distributor", self.distributor, 'customer')
        customer_id = frappe.db.get_value("Customer", customer, 'customer_id')

        if customer_id:
            filters = {'name': ['!=', self.name], 'customer_id_unique_code': ['!=', 0]}
            customers = frappe.get_all("Customer", filters, pluck='customer_id_unique_code',
                                       order_by='customer_id_unique_code')
            unique_code = customers[-1] + 1 if customers else 1
            self.customer_id = f"{customer_id}/{str(unique_code)}"
            self.customer_id_unique_code = unique_code


def after_rename(new_doc, method, old_name, merge=False, ignore_permissions=False):
    doctype = "Distributor"

    if new_doc.customer_group == 'Distributor':
        if frappe.db.exists(doctype, {'customer': new_doc.name}):
            distributor_name = frappe.db.get_value(doctype, {'customer': new_doc.name}, 'name')

            if distributor_name != new_doc.name:
                frappe.rename_doc(doctype, distributor_name, new_doc.name)

def create_or_update_distributor(self, method):
    if self.customer_group == "Distributor":
        if frappe.db.exists("Distributor", {'customer':self.name}):
            update_distributor(self)
        else:
            create_distributor(self, method)

def update_distributor(self):
    updatable_fields = ['sales_person', 'contact_person', 'contact_number', 'address',
                        'email_address', 'thana', 'zip_code', 'latitude',  'longitude']
    data = {}

    for field in updatable_fields:
        if self.get(field) != self.previous_doc.get(field):
            data[field] = self.get(field)

    if data:
        distributor = frappe.get_doc('Distributor', {'customer': self.name})
        distributor.update(data)
        distributor.save(ignore_permissions=True)

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

            sales_person.save(ignore_permissions=True)

def delete_customer_from_previous_sales_person(self):
    if self.previous_doc:
        filters = {
            "customer": self.name,
            "parent": self.previous_doc.sales_person
        }

        if frappe.db.exists("Sales Person Customer", filters):
            sales_person_customer = frappe.get_doc("Sales Person Customer", filters)
            sales_person_customer.delete(ignore_permissions=True)

def set_customer_group(self, method):
    if not self.customer_group:
        self.customer_group = 'Retail Shop'

def set_sales_person_and_employee(self, method):
    if not self.sales_person:
        if frappe.db.exists("Sales Person", {"user": frappe.session.user}):
            self.sales_person, self.employee = frappe.db.get_value("Sales Person", {"user": frappe.session.user},
                                                                   ['name', 'employee'])
        else:
            self.sales_person, self.employee = frappe.db.get_value("Sales Person", "Sales Team", ['name', 'employee'])

        if self.employee:
            self.employee_name = frappe.db.get_value("Employee", self.employee, 'employee_name')

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
            update_brand_commissions(self)
            distributor.save(ignore_permissions=True)

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
            filters = {
                "customer": customer.name,
                "parent": ["!=", customer.sales_person]
            }

            # deleting from previous sales persons
            deletable_customers = frappe.get_list(doctype, filters, 'name', ignore_permissions=True)

            for sales_person_customer in deletable_customers:
                sales_person_customer = frappe.get_doc(doctype, sales_person_customer.name)
                sales_person_customer.delete(ignore_permissions=True)

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

                    sales_person.save(ignore_permissions=True)
                    # print(customer.name, "=====added to====>>", customer.sales_person)

            frappe.db.commit()
        except:
            frappe.log_error(frappe.get_traceback(), f"{customer.name}-{customer.sales_person}")

def update_brand_commissions(self):
    if self.customer_group == 'Distributor' and self.commissions:
        distributor = frappe.get_doc('Distributor', {'customer': self.name})
        doctype = "Distributor Brand Commission"
        filters = {'parent': distributor.name}
        new_brands = []

        for customer_brand_commission in self.commissions:
            filters['brand'] = customer_brand_commission.brand

            if frappe.db.exists(doctype, filters):
                distributor_brand_commission = frappe.get_last_doc(doctype, filters)

                if customer_brand_commission.commission_rate != distributor_brand_commission.commission_rate:
                    distributor_brand_commission.commission_rate = customer_brand_commission.commission_rate
                    distributor_brand_commission.save(ignore_permissions=True)
            else:
                new_brands.append(frappe._dict({
                    'brand': customer_brand_commission.brand,
                    'commission_rate': customer_brand_commission.commission_rate
                }))

        if new_brands:
            distributor = frappe.get_doc('Distributor', {'customer': self.name})

            for brand in new_brands:
                distributor.append("commissions", {
                    "doctype": doctype,
                    "parenttype": distributor.doctype,
                    "parent": distributor.name,
                    "brand": brand.brand,
                    "commission_rate": brand.commission_rate
                })

            distributor.save(ignore_permissions=True)

        delete_brand_commissions_from_distributor(self, distributor)

def delete_brand_commissions_from_distributor(self, distributor):
    doctype = "Distributor Brand Commission"
    filters = {'parent': distributor.name}

    distributor_brands = set(frappe.db.get_all(doctype, {"parent": distributor.name}, pluck='brand'))
    customer_brands = set(frappe.db.get_all("Customer Brand Commission", {"parent": self.name}, pluck='brand'))
    deleted_brands = list(distributor_brands - customer_brands)

    for brand in deleted_brands:
        filters['brand'] = brand
        deletable_brand = frappe.get_last_doc(doctype, filters)
        deletable_brand.delete(ignore_permissions=True)
