import os, io
from pathlib import Path

import frappe
import json

file_path = str(Path(__file__).resolve().parent) + '/api_response_fields.json'

class JsonFile():
    def __init__(self):
        self.file_path = file_path

        if not os.path.isfile(self.file_path) and not os.access(self.file_path, os.R_OK):
            with io.open(self.file_path, 'w+') as db_file:
                db_file.write(json.dumps({}))

    def get_data(self):
        file = open(self.file_path, "r")
        data = json.loads(file.read())
        file.close()
        return data

    def get(self, key, default=None):
        data = self.get_data()
        return data.get(key, default)

    def set(self, key, value):
        data = self.get_data()
        data[key] = value
        json_object = json.dumps(data, indent=4)

        with open(self.file_path, "w") as outfile:
            outfile.write(json_object)
            outfile.close()

        return value


def set_doctype_fields_to_json(doctype, value):
    api_response_fields = JsonFile()
    api_response_fields.set(doctype, value)

def get_api_fields(doctype=None, with_child_fields=False):
    api_response_fields = frappe.cache().get_value('api_fields')

    if not api_response_fields:
        api_response_fields = json.loads(open(file_path, "r").read())

    if doctype:
        if with_child_fields:
            return api_response_fields.get(doctype, ['name']), api_response_fields.get(f'_{doctype}', ['name'])

        return api_response_fields.get(doctype, ['name'])

    return api_response_fields

def get_api_fields_from_json():
    api_response_fields = json.loads(open(file_path, "r").read())
    return api_response_fields

