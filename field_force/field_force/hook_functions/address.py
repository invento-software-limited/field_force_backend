import frappe

def validate(doc,method=None):
    if doc.links:
        for link in doc.links:
            if link.get("link_name"):
                doc.customer = link.get("link_name")
                break