import frappe
import datetime

@frappe.whitelist()
def create_employee_and_set_role_profile(self, method):
    if self.create_employee and not self.employee:
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
            "first_name": self.sales_person_name,
            "gender": "N/A",
            "date_of_birth": (datetime.datetime.today() - datetime.timedelta(days=1)).date(),
            "date_of_joining": datetime.datetime.today().date(),
            "user_id": self.user,
        })

        employee.insert()
        self.employee = employee.name

    if self.user and self.type:
        user = frappe.get_doc("User", self.user)
        create_role_profile(self.type)

        if user.role_profile_name != self.type:
            user.role_profile_name = self.type
            user.save()

def create_role_profile(role_profile_name):
    if not frappe.db.exists("Role Profile", {"name": role_profile_name}):
        role_profile = frappe.get_doc({
            "doctype": "Role Profile",
            "role_profile": role_profile_name
        })

        role_profile.insert()
        print(f"'{role_profile_name}'")

        roles = {
            "Merchandiser": [
                "Sales User"
            ],
            "Sales Representative": [
                "Sales User"
            ],
            "Supervisor": [
                "Sales User"
            ],
            "Manager": [
                "Sales User",
                "Sales Manager",
            ],
            "Channel Manager": [
                "Sales User",
                "Sales Manager",
                "Sales Master Manager"
            ]
        }

        for role in roles[role_profile_name]:
            role_profile.append('roles', {
                "doctype": "Has Role",
                "role": role
            })

        role_profile.save()