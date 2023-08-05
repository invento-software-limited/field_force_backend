# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from field_force.api_methods.utils import set_doctype_fields_to_json, get_api_fields_from_json

class APIDocConfig(Document):
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.api_docs:
            for doc in self.api_docs:
                fields = doc.fields.replace(' ', '').split(',')
                columns = frappe.db.sql("SHOW COLUMNS FROM `tab%s`" % doc.doc, as_dict=True)
                columns = [column['Field'] for column in columns]

                valid_fields = []
                invalid_fields = []
                child_table_fields = []

                for field in fields:
                    if field and field in columns:
                        if field not in valid_fields:
                            valid_fields.append(field)
                    elif field and frappe.db.field_exists(doc.doc, field):
                        if field not in child_table_fields:
                            child_table_fields.append(field)
                    else:
                        if field and field not in invalid_fields:
                            invalid_fields.append(field)

                if invalid_fields:
                    frappe.throw(f"The fields <b>{invalid_fields}</b> doesn't exists on <b>{doc.doc}</b>")

                set_doctype_fields_to_json(doc.doc, valid_fields)

                if child_table_fields:
                    set_doctype_fields_to_json(f"_{doc.doc}", child_table_fields)

            frappe.cache().set_value('api_fields', get_api_fields_from_json())
