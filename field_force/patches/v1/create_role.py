import frappe

def execute():
    role_name = "App User"
    create_role(role_name)

def create_role(role_name):
    if not frappe.db.exists("Role", {"name": role_name}):
        role = frappe.get_doc({
            "doctype": "Role",
            "role_name": role_name,
            "home_page": "/desk",
            "is_custom": 0,
            "desk_access": 1,
            "two_factor_auth": 0,
            "search_bar": 0,
            "notifications": 0,
            "list_sidebar": 0,
            "bulk_actions": 0,
            "view_switcher": 0,
            "form_sidebar": 0,
            "timeline": 0,
            "dashboard": 0
        })
        role.insert()
