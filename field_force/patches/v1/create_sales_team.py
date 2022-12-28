import frappe

def execute():
    print("=====>> Creating Sales Team..")

    if not frappe.db.exists({"doctype": "Sales Person", "sales_person_name": "Sales Team", "is_group": 1}):
        frappe.db.sql('''insert into `tabSales Person` (name, sales_person_name, is_group, lft, rgt)
                         values ("Sales Team", "Sales Team", 1, 0, 2)''')
        frappe.db.commit()

        print("=====>> Sales Person 'Sales Team' Created")