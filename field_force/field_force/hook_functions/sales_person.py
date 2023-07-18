import frappe
import datetime

def before_save(self, method):
    pass

def after_insert(self, method):
    create_employee_and_set_role_profile(self)
    update_sales_person(self)
    update_customers(self)

def on_update(self, method):
    # create_employee_and_set_role_profile(self)
    update_customers(self)
    update_sales_person(self)

def update_sales_person(self):
    if self.type == "Sales Representative" and self.distributor:
        customer = frappe.get_doc('Customer', self.distributor)

        if self.name != customer.sales_person:
            customer.sales_person = self.name
            customer.save()
    else:
        self.distributor = None

def create_employee_and_set_role_profile(self):
    sales_person = frappe.get_doc("Sales Person", self.parent_sales_person)

    if not self.create_employee and self.employee:
        if frappe.db.exists("Sales Person", {"employee": self.employee, "name": ["!=", self.name]}):
            frappe.throw(f"The employee <b>{self.employee}</b> already assigned to another sales person")
        elif frappe.db.exists("Employee", {"employee": self.employee, "user_id": None}):
            frappe.throw(f"The employee <b>{self.employee}</b> has no User ID", )
        else:
            self.user = frappe.db.get_value("Employee", self.employee, 'user_id')

    if self.create_employee and self.employee_number and not self.employee and not self.employee_created:
        if self.user:
            if frappe.db.exists("Employee", {"user_id": self.user}):
                frappe.throw(f"Employee already exists with user id '<b>{self.user}</b>'")

        if not frappe.db.exists("Gender", {"name": "N/A"}):
            gender = frappe.get_doc({
                "doctype": "Gender",
                "gender": "N/A"
            })
            gender.insert()

        employee = frappe.get_doc({
            "doctype": "Employee",
            "employee_number": self.employee_number,
            "first_name": self.sales_person_name,
            "gender": "N/A",
            "date_of_birth": (datetime.datetime.today() - datetime.timedelta(days=1)).date(),
            "date_of_joining": datetime.datetime.today().date(),
            "user_id": self.user,
        })

        employee.insert()
        self.employee = employee.name
        self.employee_created = 1
        employee.reports_to = sales_person.employee
        employee.save()

    elif sales_person.employee and frappe.db.exists("Employee", self.employee):
        employee = frappe.get_doc("Employee", self.employee)
        employee.reports_to = sales_person.employee

        # if employee.user_id and employee.user_id != self.user:
        #     frappe.throw("Employee's user id doesn't match with sales person's user")
        # elif not employee.user_id and self.user:
        #     employee.user_id = self.user

        employee.save()

    if self.user and self.type:
        user = frappe.get_doc("User", self.user)
        create_role_profile(self.type)

        if user.role_profile_name != self.type:
            user.role_profile_name = self.type

        user.module_profile = get_or_create_field_force_module_profile()
        user.save()

def create_role_profile(role_profile_name):
    if not frappe.db.exists("Role Profile", {"name": role_profile_name}):
        role_profile = frappe.get_doc({
            "doctype": "Role Profile",
            "role_profile": role_profile_name
        })

        role_profile.insert()
        # print(f"'{role_profile_name}'")

        roles = {
            "Merchandiser": [
                "Merchandiser",
                "App User"
            ],
            "Sales Representative": [
                "Sales Representative",
                "App User"
            ],
            "Supervisor": [
                "Supervisor",
                "App User"
            ],
            "Manager": [
                "Manager",
            ],
            "Channel Manager": [
                "Channel Manager"
            ]
        }

        for role in roles[role_profile_name]:
            role_profile.append('roles', {
                "doctype": "Has Role",
                "role": role
            })

        role_profile.save()
        return role_profile.name

    return role_profile_name

def get_or_create_field_force_module_profile():
    if not frappe.db.exists("Module Profile", {"name": "Field Force"}):
        module_profile = frappe.get_doc({
                "doctype": "Module Profile",
                "module_profile_name": "Field Force"
            }).insert()

        # modules = ["Field Force"]

        # for module in modules:
        #     module_profile.append('block_modules', {
        #         "doctype": "Block Module",
        #         "module": module
        #     })

        module_profile.save()
        return module_profile.name

    return 'Field Force'

def update_customers(self):
    if self.customers:
        for customer in self.customers:
            customer_obj = frappe.get_doc("Customer", customer.customer)

            if customer_obj.sales_person != self.name:
                filters = {
                    "name":["!=", customer.name],
                    "customer": customer.customer
                }

                if frappe.db.exists("Sales Person Customer", filters):
                    child_table_object = frappe.get_doc("Sales Person Customer", filters)
                    child_table_object.delete()

                customer_obj.sales_person = self.name
                customer_obj.save()

    if frappe.db.exists("Sales Person", self.name):
        delete_sales_person(self.name, self.customers)

def delete_sales_person(sales_person_name, current_customers):
    sales_person = frappe.get_doc("Sales Person", sales_person_name)
    customers = [customer.customer for customer in current_customers]

    for customer in sales_person.customers:
        if customer.customer not in customers:
            customer_obj = frappe.get_doc("Customer", customer.customer)
            customer_obj.sales_person = None
            customer_obj.save()
