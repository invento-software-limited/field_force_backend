import frappe

def validate(self, method):
    if self.type != "Customer":
        self.department = None
    if self.type != "Warehouse":
        self.warehouse = None

def before_save(doc, method):
    pass

def on_update(doc, method=None):
    previous_doc = doc.get_doc_before_save()

    if previous_doc:
        if previous_doc.department and not doc.department:
            delete_user_permission(doc.name, "Customer Department", previous_doc.department)
        elif doc.department and previous_doc.department != doc.department:
            set_user_permission(doc.name, "Customer Department", doc.department)

        if previous_doc.warehouse and not doc.warehouse:
            delete_user_permission(doc.name, "Warehouse", previous_doc.warehouse)
        elif doc.warehouse and previous_doc.warehouse != doc.warehouse:
            set_user_permission(doc.name, "Warehouse", doc.warehouse)

    if doc.department:
        set_user_permission(doc.name, "Customer Department", doc.department)

    if doc.warehouse:
        set_user_permission(doc.name,"Warehouse",  doc.warehouse)

def set_user_permission(doc_name, allow_doc, field_value):
    if frappe.db.exists('User Permission', {'user':doc_name, 'allow':allow_doc}):
        permission_doc = frappe.get_doc("User Permission",{'user':doc_name, 'allow':allow_doc})

        if permission_doc.for_value != field_value:
            permission_doc.for_value = field_value
            permission_doc.save()
    else:
        user_permission = frappe.get_doc({
            "doctype" : "User Permission",
            "user" : doc_name,
            "allow" : allow_doc,
            "for_value" : field_value,
            "apply_to_all_doctypes" : 1
        })

        user_permission.save()

def delete_user_permission(doc_name, allow_doc, field_value):

    if frappe.db.exists('User Permission', {'user':doc_name, 'allow':allow_doc}):
        permission_doc = frappe.get_doc("User Permission", {'user':doc_name, 'allow':allow_doc})
        permission_doc.delete()


@frappe.whitelist()
def generate_keys(user):
    """
    generate api key and api secret

    :param user: str
    """
    frappe.only_for("Admin")
    user_details = frappe.get_doc("User", user)
    api_secret = frappe.generate_hash(length=15)
    # if api key is not set generate api key
    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key
    user_details.api_secret = api_secret
    user_details.save()

    return {"api_secret": api_secret}
