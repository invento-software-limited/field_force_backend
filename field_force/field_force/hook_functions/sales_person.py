import frappe
import datetime

@frappe.whitelist()
def create_employee_and_set_role_profile(self, method):
    if self.create_employee and not self.employee:
        if self.user:
            if frappe.db.exists("Employee", {"user_id": self.user}):
                frappe.throw(f"Employee already exists with user id '<b>{self.user}</b>'")

        if not frappe.db.exists("Role Profile", {"role_profile": self.type}):
            role = frappe.get_doc({
                "doctype": "Role Profile",
                "role_profile": self.type
            })
            role.insert()

        if not frappe.db.exists("Gender", {"name": "N/A"}):
            gender = frappe.get_doc({
                "doctype": "Gender",
                "gender": "N/A"
            })
            gender.insert()

        employee_dict = frappe._dict({
            "first_name": self.sales_person_name,
            "gender": "N/A",
            "date_of_birth": (datetime.datetime.today() - datetime.timedelta(days=1)).date(),
            "date_of_joining": datetime.datetime.today().date(),
            "user_id": self.user,
            # "role_profile": self.type
        })

        print(employee_dict)
        employee = frappe.new_doc("Employee", employee_dict)
        employee.insert()
