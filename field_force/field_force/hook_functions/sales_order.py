import frappe

@frappe.whitelist()
def set_extra_values(self, method):
    self.total_items = len(self.items)

    for item in self.items:
        if not item.brand or not item.image:
            item.brand, item.image = frappe.db.get_value('Item', item.item_code, ['brand', 'image'])
