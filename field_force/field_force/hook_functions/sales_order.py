import frappe

@frappe.whitelist()
def set_extra_values(self, method):
    self.total_items = len(self.items)

    for item in self.items:
        if not item.brand or not item.image:
            item.brand, item.image = frappe.db.get_value('Item', item.item_code, ['brand', 'image'])

def add_sales_person(self, method):
    print("======>>", method)

    if not self.sales_person and frappe.db.exists("Sales Person", {"user": self.owner}):
        self.sales_person, self.employee, self.user = frappe.db.get_value("Sales Person", {'user': self.owner},
                                                               ['name', 'employee', 'user'])
    if not self.sales_team and self.sales_person:
        self.append("sales_team", {
            "parent": self.name,
            "parenttype": "Sales Order",
            "sales_person": self.sales_person,
            "allocated_percentage": 100,
            "allocated_amount": self.grand_total,
            "employee": self.employee,
            "user": self.user
        })

    if not self.user:
        self.user = self.owner

    # self.save()