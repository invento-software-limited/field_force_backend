from pathlib import Path

import frappe
import json
from frappe import _
from frappe.permissions import has_permission
from frappe.utils.data import sbool
from frappe.api import get_request_form_data

file_path = str(Path(__file__).resolve().parent) + '/api_response_fields.json'
api_response_fields = json.loads(open(file_path, "r").read())

def execute(doctype=None, name=None):
    if name:
        if frappe.local.request.method == "GET":
            kwargs = {
                "doctype": doctype,
                "fieldname": api_response_fields.get(doctype, ['name']),
                "filters": {"name":name},
            }
            doc = frappe.call(frappe.client.get_value, **kwargs)

            # if not doc.has_permission("read"):
            #     raise frappe.PermissionError
            frappe.local.response.update({"data": doc})

        if frappe.local.request.method == "PUT":
            data = get_request_form_data()

            doc = frappe.get_doc(doctype, name, for_update=True)

            if "flags" in data:
                del data["flags"]

            # Not checking permissions here because it's checked in doc.save
            doc.update(data)

            frappe.local.response.update({
                "data": doc.save().as_dict()
            })

            if doc.parenttype and doc.parent:
                frappe.get_doc(doc.parenttype, doc.parent).save()

            frappe.db.commit()

        if frappe.local.request.method == "DELETE":
            # Not checking permissions here because it's checked in delete_doc
            frappe.delete_doc(doctype, name, ignore_missing=False)
            frappe.local.response.http_status_code = 202
            frappe.local.response.message = "ok"
            frappe.db.commit()

    elif doctype:
        if frappe.local.request.method == "GET":
            # set fields for frappe.get_list
            # if frappe.local.form_dict.get("fields"):
            #     frappe.local.form_dict["fields"] = json.loads(frappe.local.form_dict["fields"])

            # assigning the fields from json
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
                data = frappe.get_list(doctype, **frappe.local.form_dict)
            else:
                frappe.throw(_("Not permitted"), frappe.PermissionError)

            # set frappe.get_list result to response
            frappe.local.response.update({
                "response": 200,
                "message": "OK",
                "error": None,
                "data": data
            })

        if frappe.local.request.method == "POST":
            # fetch data from from dict
            data = get_request_form_data()
            data.update({"doctype": doctype})

            # insert document from request data
            doc = frappe.get_doc(data).insert()

            # set response data
            frappe.local.response.update({"data": doc.as_dict()})

            # commit for POST requests
            frappe.db.commit()
    else:
        raise frappe.DoesNotExistError