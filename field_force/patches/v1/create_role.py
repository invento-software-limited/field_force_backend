import frappe

def execute():
    roles = [
        {
            "name": "Channel Manager",
            "search_bar": 1,
            "notifications": 1,
        },
        {
            "name": "Manager",
            "search_bar": 1,
            "notifications": 1,
        },
        {
            "name": "Supervisor",
            "notifications": 1,
        },
        {
            "name": "Merchandiser",
            "notifications": 1
        },
        {
            "name": "Sales Representative",
            "notifications": 1
        },
        {
            "name": "App User"
        }
    ]

    for role_name in roles:
        create_role(role_name)

def create_role(role):
    role_name = role.get('name')

    if not frappe.db.exists("Role", {"name": role_name}):
        role_dict = {
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
        }

        role_dict.update(role)
        role = frappe.get_doc(role_dict)
        role.insert()

        frappe.db.commit()
        print(f"===>> '{role_name}' role created")
    
