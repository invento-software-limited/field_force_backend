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
			"fieldname": "user",
			"label": __("User"),
			"fieldtype": "Link",
			"width": "100",
			"options": "User",
		},
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "submitted",
			"label": __("Is Submitted"),
			"fieldtype": "Check",
			"width": "100",
			"default": 1,
		},
	]
};
