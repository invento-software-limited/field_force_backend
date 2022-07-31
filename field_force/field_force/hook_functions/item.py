import frappe
import frappe.api
from field_force.api import handle

@frappe.whitelist()
def set_item_name_to_description(item, method):
    item.item_description = item.item_name
    # print("hello")

# def handle():
#     print("hello")

@frappe.whitelist()
def set_handler():
    frappe.api.handle = handle

    # print(frappe.api.handle())