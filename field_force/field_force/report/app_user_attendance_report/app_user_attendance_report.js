// Copyright (c) 2022, Invento Software Limited and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["App User Attendance Report"] = {
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
			"fieldname": "type",
			"label": __("Type"),
			"fieldtype": "Select",
			"width": "100",
			"options": [
				"",
				"Checkin",
				"Checkout",
			],
		}
	]
};
