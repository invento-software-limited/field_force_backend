// Copyright (c) 2023, Invento Software Limited and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Delivery Trip Report"] = {
	"filters": [
		{
			"fieldname":"departure_date",
			"label": __("Departure Date"),
			"fieldtype": "Date",
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
		if (column.id == "status" && value === "Completed") {
			value = "<span style='color:green;'>" + value + "</span>";
		}else if (column.id == "status" && value === "Draft") {
			value = "<span style='color:brown;'>" + value + "</span>";
		}else if (column.id == "status" && value === "In Transit") {
			value = "<span style='color:blue;'>" + value + "</span>";
		}else if (column.id == "status" && value === "Cancelled") {
			value = "<span style='color:red;'>" + value + "</span>";
		}else if (column.id == "status" && value === "Scheduled") {
			value = "<span style='color:#b100c7;'>" + value + "</span>";
		}
		return value;
	}
};
