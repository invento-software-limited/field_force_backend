# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SalesTarget(Document):
	def validate(self):
		messages = ''

		for target in self.sales_persons_targets:
			target.month = self.month
			target.year = self.year

			filters = {
				"sales_person": target.sales_person,
				"month": target.month,
				"year": target.year
			}

			if frappe.db.exists("Sales Person Target", filters):
				messages += f"Target already exists of sales person <b>{target.sales_person}</b>" \
							f" for <b>{target.month}</b>, <b>{target.year}</b><br><hr>"

		if messages:
			frappe.throw(messages)


@frappe.whitelist()
def get_sales_persons(reporting_person, all_child=True, as_tree=False):
	sales_persons_list = []
	tree_dict = {}
	get_all_children(sales_persons_list, tree_dict,  reporting_person, all_child)

	if as_tree:
		return tree_dict
	# print(sales_persons_list)
	return sales_persons_list

def get_all_children(sales_persons_list, tree_dict, parent, all_child=True, as_tree=False):
	sales_persons = get_child(parent)

	if parent not in tree_dict.keys():
		tree_dict[parent] = {}

	if not sales_persons:
		return

	for sales_person in sales_persons:
		sales_persons_list.append(sales_person)
		tree_dict[parent][sales_person.sales_person] = {}

		if sales_person.is_group and all_child:
			get_all_children(sales_persons_list, tree_dict[parent], sales_person.sales_person, tree_dict)


def get_child(parent):
	return frappe.db.sql("""select name as sales_person, sales_person_name, employee, is_group from `tabSales Person` 
							where parent_sales_person='%s'""" % parent, as_dict=1)
