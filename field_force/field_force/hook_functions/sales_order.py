import frappe

@frappe.whitelist()
def set_item_count(self, method):
    self.total_items = len(self.items)