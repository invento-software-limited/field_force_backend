import frappe

def execute():
    role_permissions = get_role_permissions()

    for role, permissions in role_permissions.items():
        for permission in permissions:
            # permission = get_permission(role, permission)
            # permission_ = frappe.get_doc(permission)
            # permission_.insert()

            permission = get_permission(role, permission)

            doctype = frappe.get_doc('DocType', permission['parent'])
            exists = False

            for perm in doctype.permissions:
                if perm.role == role:
                    exists = True
                    break

            if not exists and not frappe.db.exists('DocPerm', {'role': role, 'parent': permission['parent']}):
                doctype.append("permissions", permission)
                doctype.save()
            
                print(f"=====>> Permissions of '{permission['parent']}' added to Role '{role}'")
    
    frappe.db.commit()

def get_permission(role, permission, perm_level=0):
    defualt_permission = {
        "doctype": "DocPerm",
        "perm_level": perm_level,
        "select": 0,
        "read": 0,
        "write": 0,
        "create": 0,
        "delete": 0,
        "submit": 0,
        "cancel": 0,
        "amend": 0,
        "report": 0,
        "export": 0,
        "import": 0,
        "share": 0,
        "print": 0,
        "email": 0,
        "set_user_permissions": 0
    }

    defualt_permission["role"] = role
    defualt_permission.update(permission)
    return defualt_permission

def get_role_permissions():
    role_permissions = {
        "Channel Manager": [
            {
                "parent": "User",
                "select": 1,
                "create": 1,
                "read": 1,
                "write": 1,
                "report": 1,
                "export": 1,
                "import": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "User Permission",
                "select": 1,
                "read": 1,
                "write": 1,
                "create": 1,
            },
            {
                "parent": "Employee",
                "select": 1,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "report": 1,
                "export": 1,
                "import": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Sales Person",
                "perm_level": 0,
                "select": 1,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "report": 1,
                "export": 1,
                "import": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Customer Group",
                "select": 1,
                "read": 1,
            },
            {
                "parent": "Sales Order",
                "select": 1,
                "read": 1,
                "write": 1,
                "create": 1,
                "submit": 1,
                "cancel": 1,
                "amend": 1,
                "delete": 1,
                "report": 1,
                "export": 1,
                "import": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Customer",
                "select": 1,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "report": 1,
                "export": 1,
                "import": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Item",
                "select": 1,
                "read": 1,
                "create": 1,
                "write": 1,
                "delete": 1,
                "report": 1,
                "import": 1,
                "export": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Item Price",
                "select": 1,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "report": 1,
                "export": 1,
                "import": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Data Import",
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
            },
            {
                "parent": "Data Export",
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
            }
        ],
        "Manager": [
            {
                "parent": "User",
                "select": 1,
                "create": 1,
                "read": 1,
                "write": 1,
                "report": 1,
                "export": 1,
                "import": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "User Permission",
                "select": 1,
                "read": 1,
                "write": 1,
                "create": 1,
            },
            {
                "parent": "Employee",
                "select": 1,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "report": 1,
                "export": 1,
                "import": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Sales Person",
                "select": 1,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "report": 1,
                "export": 1,
                "import": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Customer Group",
                "select": 1,
                "read": 1,
            },
            {
                "parent": "Customer",
                "select": 1,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "report": 1,
                "export": 1,
                "import": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Sales Order",
                "select": 1,
                "read": 1,
                "write": 1,
                "create": 1,
                "submit": 1,
                "cancel": 1,
                "amend": 1,
                "delete": 1,
                "report": 1,
                "export": 1,
                "import": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Item",
                "select": 1,
                "read": 1,
                "report": 1,
                "export": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Item Price",
                "select": 1,
                "read": 1,
                "report": 1,
                "export": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Employee",
                "select": 1,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "report": 1,
                "export": 1,
                "import": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Data Import",
                "read": 1,
                "write": 1,
                "create": 1,
            },
            {
                "parent": "Data Export",
                "read": 1,
                "write": 1,
                "create": 1,
            }
        ],
        "Supervisor": [
            {
                "parent": "User",
                "select": 1,
                "create": 1,
                "read": 1,
                "write": 1,
                "report": 1,
                "export": 1,
                "import": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "User Permission",
                "select": 1,
                "read": 1,
                "write": 1,
                "create": 1,
            },
            {
                "parent": "Employee",
                "select": 1,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "report": 1,
                "export": 1,
                "import": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Sales Order",
                "select": 1,
                "read": 1,
                "write": 1,
                "create": 1,
                "submit": 1,
                "cancel": 1,
                "amend": 1,
                "delete": 1,
                "report": 1,
                "export": 1,
                "import": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Sales Person",
                "select": 1,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "report": 1,
                "export": 1,
                "import": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Customer Group",
                "select": 1,
                "read": 1,
            },
            {
                "parent": "Customer",
                "select": 1,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "report": 1,
                "export": 1,
                "import": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Item",
                "select": 1,
                "read": 1,
                "report": 1,
                "export": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Employee",
                "select": 1,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "report": 1,
                "export": 1,
                "import": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Data Import",
                "read": 1,
                "write": 1,
                "create": 1,
            },
            {
                "parent": "Data Export",
                "read": 1,
                "write": 1,
                "create": 1,
            }
        ],
        "Sales Representative": [
            {
                "parent": "Customer Group",
                "select": 1,
                "read": 1,
            },
            {
                "parent": "Customer",
                "select": 1,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "report": 1,
                "export": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Item",
                "select": 1,
                "read": 1,
                "report": 1,
                "export": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Item Price",
                "select": 1,
                "read": 1,
                "report": 1,
                "export": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Sales Order",
                "select": 1,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "report": 1,
                "export": 1,
                "import": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
        ],
        "Merchandiser": [
            {
                "parent": "Sales Order",
                "select": 1,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "report": 1,
                "export": 1,
                "import": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Customer Group",
                "select": 1,
                "read": 1,
            },
            {
                "parent": "Customer",
                "select": 1,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "report": 1,
                "export": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Item",
                "select": 1,
                "read": 1,
                "report": 1,
                "export": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
            {
                "parent": "Item Price",
                "select": 1,
                "read": 1,
                "report": 1,
                "export": 1,
                "share": 1,
                "print": 1,
                "email": 1
            },
        ]
    }
    return role_permissions