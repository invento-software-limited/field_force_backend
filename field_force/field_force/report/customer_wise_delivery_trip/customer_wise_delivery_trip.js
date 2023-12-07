// Copyright (c) 2023, Invento Software Limited and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customer Wise Delivery Trip"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "60px",
      "default":frappe.datetime.get_today()
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "60px",
      "default":frappe.datetime.get_today()
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": "60px"
		},
		{
			"fieldname": "territory",
			"label": __("Territory"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Territory",
		},
		{
			"fieldname": "driver",
			"label": __("Driver"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Driver",
		},
		{
			"fieldname": "vehicle",
			"label": __("Vehicle"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Vehicle",
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"width": "100",
			"options": [
				"",
				"Draft",
				"Scheduled",
				"In Transit",
				"Completed",
				"Cancelled"
			],
		}
	],
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.id == "status") {
			column.align = "left";
		}
		if (column.id == "status" && value === "Completed") {
			value = "<span style='color:green;'>" + value + "</span>";
		}else if (column.id == "status" && value === "Draft") {
			value = "<p style='color:brown;'>" + value + "</p>";
		}else if (column.id == "status" && value === "In Transit") {
			value = "<p style='color:blue;'>" + value + "</p>";
		}else if (column.id == "status" && value === "Cancelled") {
			value = "<p style='color:red;'>" + value + "</p>";
		}else if (column.id == "status" && value === "Scheduled") {
			value = "<p style='color:#b100c7;'>" + value + "</p>";
		}else if (column.id == "territory") {
			column.align = "left";
		}
		return value;
	}
};
