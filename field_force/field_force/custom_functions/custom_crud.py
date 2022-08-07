from pathlib import Path

import frappe
import json

from field_force.response import build_custom_response
from frappe import _
from frappe.permissions import has_permission
from frappe.utils.data import sbool
from frappe.api import get_request_form_data
from frappe.utils.response import build_response

file_path = str(Path(__file__).resolve().parent) + '/api_response_fields.json'
api_response_fields = json.loads(open(file_path, "r").read())

def execute(doctype=None, name=None):
    try:
        if name:
            if frappe.local.request.method == "GET":
                kwargs = {
                    "doctype": doctype,
                    "fieldname": api_response_fields.get(doctype, ['name']),
                    "filters": {"name":name},
                }
                doc = frappe.call(frappe.client.get_value, **kwargs)
                frappe.local.response.data = doc

            if frappe.local.request.method == "PUT":
                data = get_request_form_data()
                doc = frappe.get_doc(doctype, name, for_update=True)

                if "flags" in data:
                    del data["flags"]

                # Not checking permissions here because it's checked in doc.save
                doc.update(data)
                data = {}

                for field in api_response_fields.get(doctype, ['name']):
                    data[field] = doc.get(field)

                frappe.local.response.update({
                    "data": data
                })

                if doc.parenttype and doc.parent:
                    frappe.get_doc(doc.parenttype, doc.parent).save()

                frappe.db.commit()

            if frappe.local.request.method == "DELETE":
                # Not checking permissions here because it's checked in delete_doc
                frappe.delete_doc(doctype, name, ignore_missing=False)
                frappe.local.response.http_status_code = 202
                frappe.local.response.message = f"{doctype} {name} deleted"
                frappe.db.commit()

        elif doctype:
            if frappe.local.request.method == "GET":
                frappe.local.form_dict["fields"] = api_response_fields.get(doctype, ['name'])

                # set limit of records for frappe.get_list
                frappe.local.form_dict.setdefault(
                    "limit_page_length",
                    frappe.local.form_dict.limit or frappe.local.form_dict.limit_page_length or 20,
                )

                # convert strings to native types - only as_dict and debug accept bool
                for param in ["as_dict", "debug"]:
                    param_val = frappe.local.form_dict.get(param)
                    if param_val is not None:
                        frappe.local.form_dict[param] = sbool(param_val)

                if has_permission(doctype, 'read'):
                    # data = frappe.get_list(doctype, **frappe.local.form_dict)
                    data = frappe.call(frappe.client.get_list, doctype, **frappe.local.form_dict)
                    frappe.local.response.total_items = len(frappe.get_list(doctype, frappe.local.form_dict.get('filters')))
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

                # insert document from request data
                doc = frappe.get_doc(data).insert()
                data = {}

                for field in api_response_fields.get(doctype, ['name']):
                    data[field] = doc.get(field)

                # set response data
                frappe.local.response.update({"data": data})

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

    return build_custom_response(response_type='custom')