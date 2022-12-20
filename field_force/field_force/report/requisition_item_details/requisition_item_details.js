// Copyright (c) 2022, Invento Software Limited and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Requisition Item Details"] = {
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
		// {
		// 	"fieldname": "requisition",
		// 	"label": __("Requisition"),
		// 	"fieldtype": "Link",
		// 	"width": "100",
		// 	"options": "Requisition",
		// },
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
			"fieldname": "item",
			"label": __("Item"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Item",
		},
		{
			"fieldname": "delivery_date",
			"label": __("Delivery Date"),
			"fieldtype": "Date",
			"width": "100",
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
				"",
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
	],
	// "formatter":function (row, cell, value, columnDef, dataContext, default_formatter) {
	// 	value = default_formatter(row, cell, value, columnDef, dataContext);
	// 	if (dataContext.amount > 50) {
	// 		var $value = $(value).css("font-weight", "bold");
	// 		value = $value.wrap("<p></p>").parent().html();
	// 	}
	// 	return value;
	// }
};
