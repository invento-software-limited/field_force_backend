import http

import frappe
import json
from werkzeug.wrappers import Response
from frappe.utils.response import make_logs, json_handler
from frappe.utils.response import (as_csv, as_txt, as_raw, as_json, as_page, as_pdf, as_binary, redirect)


def build_custom_response(response_type=None):
    if "docs" in frappe.local.response and not frappe.local.response.docs:
        del frappe.local.response["docs"]

    response_type_map = {
        'csv': as_csv,
        'txt': as_txt,
        'download': as_raw,
        'json': as_json,
        'pdf': as_pdf,
        'page': as_page,
        'redirect': redirect,
        'binary': as_binary,
        'custom': as_custom,
    }

    return response_type_map[frappe.response.get('type') or response_type]()


def as_custom():
    make_logs()
    response = Response()

    if frappe.local.response.http_status_code:
        response.status_code = frappe.local.response['http_status_code']
        del frappe.local.response['http_status_code']

    response.mimetype = 'application/json'
    response.charset = 'utf-8'

    limit_start = frappe.local.form_dict.limit_start or 0
    limit_page_length = frappe.local.form_dict.limit or frappe.local.form_dict.limit_page_length or 20

    data = {
        "status_code": response.status_code,
        "message": "OK",
        "errors": "",
        "total_items": 0,
        'limit_start': int(limit_start),
        'limit_page_length': int(limit_page_length)
    }

    data.update(frappe.local.response)

    response.data = json.dumps(data, default=json_handler, separators=(',', ':'))
    return response