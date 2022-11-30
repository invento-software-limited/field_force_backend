// Copyright (c) 2022, Invento Software Limited and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Requisition Summary Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname": "group_by",
			"label": __("Group By"),
			"fieldtype": "Select",
			"width": "100",
			"options": [
				"Distributor",
				"Customer",
				"Created By"
			],
			"default": "Distributor"
		},
		{
			"fieldname": "distributor",
			"label": __("Distributor"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Distributor",
			"depends_on": 'eval:doc.group_by=="Distributor"'
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Customer",
			"depends_on": 'eval:doc.group_by=="Customer"'
		},
		{
			"fieldname": "user",
			"label": __("Created By"),
			"fieldtype": "Link",
			"width": "100",
			"options": "User",
			"depends_on": 'eval:doc.group_by=="Created By"'
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"width": "100",
			"options": [
				"Draft",
				"Submitted",
				"Cancelled"
			],
			"default": "Submitted"
		},
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
	]
};
