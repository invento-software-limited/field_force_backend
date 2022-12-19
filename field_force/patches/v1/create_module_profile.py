import frappe

def execute():
    create_field_force_module_profile()

def create_field_force_module_profile():
    if not frappe.db.exists("Module Profile", {"name": "Field Force"}):
        module_profile = frappe.get_doc({
            "doctype": "Module Profile",
            "module_profile": ['Field Force']
        }).insert()

        modules = ["Field Force"]

        for module in modules:
            module_profile.append('block_modules', {
                "doctype": "Block Module",
                "module": module
            })

        module_profile.save()
        print("'Field Force' module profile created")
