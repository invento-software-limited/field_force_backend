import frappe

@frappe.whitelist()
def set_customer_group(self, method):
    print(self)
    if self.distributor:
        self.customer_group = 'Retail Shop'

@frappe.whitelist()
def set_image(self, method):

    print(self)
    if self.image:
        print(self.image)
