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

			if already_has_sales_target(target):
				messages += f"Target already exists of sales person <b>{target.sales_person}</b>" \
							f" for <b>{target.month}</b>, <b>{target.year}</b><br><hr>"

		if messages:
			frappe.throw(messages)


@frappe.whitelist()
def get_sales_persons(reporting_person, exclude_group=False, all_child=True, as_tree=False, type=None):
	sales_persons_list = []
	tree_dict = {}
	get_all_children(sales_persons_list, tree_dict, reporting_person, exclude_group, all_child, type=type)

	if as_tree:
		return tree_dict
	# print(sales_persons_list)
	return sales_persons_list

def get_all_children(sales_persons_list, tree_dict, parent, exclude_group=False, all_child=True, as_tree=False, type=None):
	sales_persons = get_child(parent)

	if parent not in tree_dict.keys():
		tree_dict[parent] = {}

	if not sales_persons:
		return

	for sales_person in sales_persons:
		if exclude_group and sales_person.is_group and all_child:
			get_all_children(sales_persons_list, tree_dict[parent], sales_person.sales_person, exclude_group, all_child)
		elif type:
			if sales_person.type == type:
				sales_persons_list.append(sales_person)
				tree_dict[parent][sales_person.sales_person] = {}
			else:
				if sales_person.is_group and all_child:
					get_all_children(sales_persons_list, tree_dict[parent], sales_person.sales_person, exclude_group, type=type)
		else:
			sales_persons_list.append(sales_person)
			tree_dict[parent][sales_person.sales_person] = {}

			if sales_person.is_group and all_child:
				get_all_children(sales_persons_list, tree_dict[parent], sales_person.sales_person, exclude_group)

def get_child(parent):
	return frappe.db.sql("""select name as sales_person, sales_person_name, employee, is_group, type
	 						from `tabSales Person` where parent_sales_person='%s'""" % parent, as_dict=1)


def already_has_sales_target(target):
	targets = frappe.db.sql('''select 
					sales_person,
					target_amount 
					from `tabSales Person Target` sales_person_target
					join `tabSales Target` sales_target on sales_person_target.parent = sales_target.name 
					where sales_target.docstatus = 1 
					and sales_person_target.name != "%s" 
					and sales_person_target.sales_person = "%s"
					and sales_person_target.month = "%s" 
					and sales_person_target.year = "%s"''' % (target.name, target.sales_person,
															  target.month, target.year), as_dict=1)
	return targets