# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SalesTarget(Document):
	def validate(self):
		for target in self.sales_persons_targets:
			target.month = self.month
			target.year = self.year



@frappe.whitelist()
def get_sales_persons(reporting_person):
	sales_persons_list = []

	get_all_children(sales_persons_list, reporting_person)
	# print(sales_persons_list)
	return sales_persons_list

def get_all_children(sales_persons_list, parent):
	sales_persons = get_child(parent)

	if not sales_persons:
		return

	for sales_person in sales_persons:
		sales_persons_list.append(sales_person)

		if sales_person.is_group:
			get_all_children(sales_persons_list, sales_person.sales_person)

def get_child(parent):
	return frappe.db.sql("""select name as sales_person, sales_person_name, employee, is_group from `tabSales Person` 
							where parent_sales_person='%s'""" % parent, as_dict=1)
