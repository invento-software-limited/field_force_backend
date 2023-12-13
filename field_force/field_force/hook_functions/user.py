import frappe

def on_update(doc,method=None):
    if doc.department:
        set_user_permission(doc.department,"Department",doc.name)
            
    if doc.warehouse:
        set_user_permission(doc.warehouse,"Warehouse",doc.name)
            
def set_user_permission(field_value,allow,doc_name):
    exists = frappe.db.exists('User Permission', {'user':doc_name, 'allow':allow})
    if exists:
        permission_doc = frappe.get_doc("User Permission",{'user':doc_name, 'allow':allow})
        if permission_doc.for_value != field_value:
            permission_doc.for_value = field_value
            permission_doc.save()
    else:
        user_permission = frappe.get_doc({
            
            "doctype" : "User Permission",
            "user" : doc_name,
            "allow" : allow,
            "for_value" : field_value,
            "apply_to_all_doctypes" : 1
        })
        
        
        user_permission.save()