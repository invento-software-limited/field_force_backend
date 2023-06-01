// Copyright (c) 2022, Invento Software Limited and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Requisition Details Report"] = {
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
			"fieldname": "distributor",
			"label": __("Distributor"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Distributor",
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Customer",
			"get_query" : function() {
				return {
					"doctype": "Customer",
					"filters": [
						["distributor", "!=", '']
					]
				}
			}
		},
    {
			"fieldname": "territory",
			"label": __("Territory"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Territory",
		},
		{
			"fieldname": "sales_person",
			"label": __("Sales Person"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Sales Person",
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
