import frappe
import json
import time

from field_force.api_methods.custom_methods import CUSTOM_API_DOCTYPES ,get_custom_data, set_custom_data_before_creation
from field_force.response import build_custom_response
from frappe import _
from frappe.permissions import has_permission
from frappe.utils.data import sbool
from field_force.api_methods.utils import file_path, get_api_fields


def execute(doctype=None, name=None):
    api_response_fields = get_api_fields()

    try:
        if "run_method" in frappe.local.form_dict:
            method = frappe.local.form_dict.pop("run_method")
            doc = frappe.get_doc(doctype, name)
            doc.is_whitelisted(method)

            if frappe.local.request.method == "GET":
                if not doc.has_permission("read"):
                    frappe.throw(_("Not permitted"), frappe.PermissionError)
                frappe.local.response.update({"data": doc.run_method(method, **frappe.local.form_dict)})

            if frappe.local.request.method == "POST":
                if not doc.has_permission("write"):
                    frappe.throw(_("Not permitted"), frappe.PermissionError)

                doc = doc.run_method(method, **frappe.local.form_dict)
                frappe.db.commit()
                frappe.local.response.data = get_doc_permitted_fields(doctype, doc, api_response_fields)

        elif name:
            if frappe.local.request.method == "GET":
                doc = frappe.get_doc(doctype, name)

                if not doc.has_permission("read"):
                    raise frappe.PermissionError

                frappe.local.response.data = get_doc_permitted_fields(doctype, doc, api_response_fields)

            if frappe.local.request.method == "PUT":
                data = get_request_form_data()
                doc = frappe.get_doc(doctype, name, for_update=True)

                if "flags" in data:
                    del data["flags"]

                # Not checking permissions here because it's checked in doc.save
                doc.update(data)

                if doc.get('parenttype') and doc.get('parent'):
                    frappe.get_doc(doc.parenttype, doc.parent).save()

                doc.save()
                frappe.db.commit()
                frappe.local.response.data = get_doc_permitted_fields(doctype, doc, api_response_fields)
                frappe.local.response.message = f"{doctype} Updated"

            if frappe.local.request.method == "DELETE":
                # Not checking permissions here because it's checked in delete_doc
                frappe.delete_doc(doctype, name, ignore_missing=False)
                frappe.local.response.http_status_code = 202
                frappe.local.response.message = f"{doctype} {name} deleted"
                frappe.db.commit()

        elif doctype:
            if frappe.local.request.method == "GET":
                if not frappe.local.form_dict.get('fields'):
                    frappe.local.form_dict["fields"] = api_response_fields.get(doctype, ['name'])

                if not frappe.local.form_dict.get('order_by'):
                    frappe.local.form_dict['order_by'] = "modified desc"

                # set limit of records for frappe.get_list
                frappe.local.form_dict.setdefault(
                    "limit_page_length",
                    frappe.local.form_dict.limit or frappe.local.form_dict.limit_page_length or 500,
                )

                # convert strings to native types - only as_dict and debug accept bool
                for param in ["as_dict", "debug"]:
                    param_val = frappe.local.form_dict.get(param)
                    if param_val is not None:
                        frappe.local.form_dict[param] = sbool(param_val)

                if has_permission(doctype, 'read'):
                    if doctype in CUSTOM_API_DOCTYPES:
                        data = get_custom_data(doctype)
                    else:
                        # data = frappe.get_list(doctype, **frappe.local.form_dict)
                        data = frappe.call(frappe.client.get_list, doctype, **frappe.local.form_dict)
                        frappe.local.response.total_items = len(data)

                    # set frappe.get_list result to response
                    frappe.local.response.update({
                        "data": data
                    })
                else:
                    frappe.throw(_("Not permitted"), frappe.PermissionError)

            elif frappe.local.request.method == "POST":
                # fetch data form dict
                data = get_request_form_data()
                data.update({"doctype": doctype})
                set_custom_data_before_creation(doctype, data)

                # insert document from request data
                doc = frappe.get_doc(data).insert()
                data = get_doc_permitted_fields(doctype, doc, api_response_fields)

                # set response data
                frappe.local.response.update({"data": data})
                frappe.local.response.http_status_code = 201
                frappe.local.response.message = f"{doctype} Created"

                # commit for POST requests
                frappe.db.commit()
        else:
            raise frappe.DoesNotExistError

    except frappe.PermissionError:
        frappe.local.response.http_status_code = 403
        frappe.local.response.message = f"Permission Denied"
    except frappe.DoesNotExistError:
        frappe.local.response.http_status_code = 404
        frappe.local.response.message = f"Doctype {doctype} not found!"
    except frappe.DuplicateEntryError:
        frappe.local.response.http_status_code = 409
        frappe.local.response.message = f"Duplicate Entry!"
    except frappe.InvalidAuthorizationToken:
        frappe.local.response.http_status_code = 401
        frappe.local.response.message = f"Invalid Token!"

    return build_custom_response(response_type='custom')

def get_request_form_data():
    if frappe.local.form_dict.data is None:
        data = frappe.safe_decode(frappe.local.request.get_data())
    else:
        data = frappe.local.form_dict.data

    return frappe.parse_json(data)

def get_doc_permitted_fields(doctype, doc, api_response_fields):
    doc_ = doc.__dict__
    data = {}
    doc_api_response_fields = api_response_fields.get(doctype, ['name']) + api_response_fields.get(f"_{doctype}", [])

    for field in doc_api_response_fields:
        value = doc_.get(field)

        if isinstance(value, list):
            new_list = []
            try:
                for element in value:
                    api_response_fields_ = api_response_fields.get(element.doctype)

                    if api_response_fields_:
                        new_element = {}

                        for field_ in api_response_fields_:
                            new_element[field_] = element.get(field_)

                        new_list.append(new_element)
                    else:
                        new_list.append(element)

                data[field] = new_list
            except:
                data[field] = value
        else:
            data[field] = value

    return data
