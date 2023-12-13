import frappe

def on_update(doc,method=None):
    if doc.department:
        exists = frappe.db.exists('User Permission', {'user':doc.name, 'allow':"Department"})
        if exists:
            permission_doc = frappe.get_doc("User Permission",{'user':doc.name, 'allow':"Department"})
            if permission_doc.for_value != doc.department:
                permission_doc.for_value = doc.department
                permission_doc.save()
        else:
            user_permission = frappe.get_doc({
                
                "doctype" : "User Permission",
                "user" : doc.name,
                "allow" : "Department",
                "for_value" : doc.department,
                "apply_to_all_doctypes" : 1
            })
            
            
            user_permission.save()
            
    if doc.warehouse:
        exists = frappe.db.exists('User Permission', {'user':doc.name, 'allow':"Warehouse"})
        if exists:
            permission_doc = frappe.get_doc("User Permission",{'user':doc.name, 'allow':"Warehouse"})
            if permission_doc.for_value != doc.warehouse:
                permission_doc.for_value = doc.warehouse
                permission_doc.save()
        else:
            user_permission = frappe.get_doc({
                
                "doctype" : "User Permission",
                "user" : doc.name,
                "allow" : "Warehouse",
                "for_value" : doc.warehouse,
                "apply_to_all_doctypes" : 1
            })
            
            
            user_permission.save()