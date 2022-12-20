import frappe

role_profiles = {
    "Merchandiser": [
        "Merchandiser",
        "App User"
    ],
    "Sales Representative": [
        "Sales Representative",
        "App User"
    ],
    "Supervisor": [
        "Supervisor",
        "App User"
    ],
    "Manager": [
        "Manager",
    ],
    "Channel Manager": [
        "Channel Manager"
    ]
}

def execute():
    create_role_profile(role_profiles)

def create_role_profile(role_profiles):
    for role_profile, roles in role_profiles.items():
        if not frappe.db.exists("Role Profile", {"name": role_profile}):
            role_profile = frappe.get_doc({
                "doctype": "Role Profile",
                "role_profile": role_profile
            })

            role_profile.insert()
            # print(f"'{role_profile_name}'")

            for role in roles[role_profile]:
                role_profile.append('roles', {
                    "doctype": "Has Role",
                    "role": role
                })

            role_profile.save()

        print(f"Role Profile '{role_profile}' created")