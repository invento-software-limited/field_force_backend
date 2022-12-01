import os
import frappe
import datetime

def set_user_link(doc):
    if doc.user:
        title = doc.user_fullname or doc.user
        doc['user'] = f'<a href="/app/user/{doc.user}" target="_blank">{title}</a>'
        
def set_link_to_doc(doc, field, doc_url=''):
    doc[field] = f'<a href="/app/{doc_url}/{doc[field]}" ' \
                                  f'target="_blank">{doc[field]}</a>'

def set_image_url(doc, site_directory=None):
    site_directory = site_directory or  get_site_directory_path()

    if not doc.image or '/files/' not in doc.image:
        doc.image = '/files/default-image.png'

    elif '/files/' in doc.image:
        image_path = f"{site_directory}/public{doc.image}"

        if not os.path.exists(image_path):
            doc.image = '/files/default-image.png'

def get_site_directory_path():
    site_name = frappe.local.site
    cur_dir = os.getcwd()
    return os.path.join(cur_dir, site_name)