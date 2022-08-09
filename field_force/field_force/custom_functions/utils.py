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
