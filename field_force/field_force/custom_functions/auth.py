import frappe
from frappe.auth import LoginManager
import frappe.core.doctype.user
from frappe.core.doctype.user.user import generate_keys

# def auth(name):
#     if name == 'get-access-token':
#         get_api_access_token()

@frappe.whitelist()
def callback():
    print(frappe.request)

@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    login_manager = LoginManager()
    login_manager.authenticate(usr,pwd)
    login_manager.post_login()

    if frappe.response['message'] == 'Logged In':
        user = frappe.session.user
        user_doc = frappe.get_doc('User', user)
        frappe.local.response.update({
            "token": get_api_key_and_api_secret(user_doc),
        })

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


    #     instructor = frappe.db.get_value("Instructor", {"user": login_manager.user}, "name")
    #     if instructor: return instructor
#
# def get_api_access_token():

#     user = frappe.session.user
#     user_doc = frappe.get_doc('User', user)
#     print("=======>>", user_doc.api_key)