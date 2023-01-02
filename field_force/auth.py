import frappe
from field_force.response import build_custom_response
from frappe.auth import LoginManager
import frappe.core.doctype.user

@frappe.whitelist(allow_guest=True)
def login(username, password):
    login_manager = LoginManager()

    try:
        login_manager.authenticate(username, password)
        login_manager.post_login()
    except Exception as e:
        frappe.local.response['errors'] = e

    if frappe.response['message'] == 'Logged In':
        user = frappe.session.user
        user_doc = frappe.get_doc('User', user)

        del frappe.local.response['home_page']
        user = frappe.session.user

        frappe.local.response.data = {
            "user": user_doc.name,
            "full_name": frappe.local.response.pop('full_name'),
            "user_image": user_doc.user_image,
            "email": user_doc.email,
            "token": get_api_key_and_api_secret(user_doc),
            "allowed_doctypes": get_allowed_doctypes(user)
        }

        frappe.local.response['http_status_code'] = 200
    else:
        frappe.local.response['http_status_code'] = 401

    return build_custom_response(response_type='custom')


def get_api_key_and_api_secret(user_details):
    api_key = user_details.api_key
    api_secret = user_details.get_password('api_secret') if user_details.api_secret else None

    frappe.session.user = 'administrator'

    # if api key is not set generate api key
    if not api_key and not api_secret:
        api_key = frappe.generate_hash(length=15)
        api_secret = frappe.generate_hash(length=15)

        # frappe.only_for("System Manager")
        user_details.api_key = api_key
        user_details.api_secret = api_secret
        user_details.save()

    return f"{user_details.api_key}:{user_details.get_password('api_secret')}"

def get_allowed_doctypes(user):
    role_profile = frappe.db.get_value('User', user, 'role_profile_name')

    if role_profile:
        allowed_doctypes = frappe.db.get_value("App End Permission Role Profile",
                                               {"role_profile": role_profile}, "doctypes")
        if allowed_doctypes:
            return allowed_doctypes.split(',')

    return []
