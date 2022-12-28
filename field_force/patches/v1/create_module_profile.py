import frappe

def execute():
    create_field_force_module_profile()

def create_field_force_module_profile():
    if not frappe.db.exists("Module Profile", {"name": "Field Force"}):
        module_profile = frappe.get_doc({
            "doctype": "Module Profile",
            "module_profile_name": "Field Force"
        }).insert()

        block_modules = get_block_modules()

        for module in block_modules:
            module_profile.append("block_modules", {
                "doctype": "Block Module",
                "module": module
            })

        module_profile.save()
        frappe.db.commit()
        print("'Field Force' module profile created")
        
def get_block_modules():
    block_modules = [
        "Core",
        "Website",
        "Workflow",
        "Email",
        "Custom",
        "Geo",
        "Desk",
        "Integrations",
        "Printing",
        "Contacts",
        "Data Migration",
        "Social",
        "Automation",
        "Event Streaming",
        "Accounts",
        "CRM",
        "Buying",
        "Projects",
        "Selling",
        "Setup",
        "HR",
        "Manufacturing",
        "Stock",
        "Support",
        "Utilities",
        "Assets",
        "Portal",
        "Maintenance",
        "Regional",
        "Healthcare",
        "Restaurant",
        "ERPNext Integrations",
        "Hotels",
        "Hub Node",
        "Quality Management",
        "Communication",
        "Loan Management",
        "Payroll",
        "Telephony",
        "E-commerce",
        "Agriculture",
        "Education",
        "Non Profit"
    ]
    return block_modules