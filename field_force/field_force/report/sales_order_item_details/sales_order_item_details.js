// Copyright (c) 2023, Invento Software Limited and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Order Item Details"] = {
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
      "get_query" : function() {
				return {
					"doctype": "Sales Person",
					"filters": [
						["type", "=", ["Sales Representative", "or", "Merchandiser"]]
					]
				}
			}
		},
    {
			"fieldname": "supervisor",
			"label": __("Supervisor"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Sales Person",
      "get_query" : function() {
				return {
					"doctype": "Sales Person",
					"filters": [
						["type", "=", "Supervisor"]
					]
				}
			}
		},
    {
			"fieldname": "customer_group",
			"label": __("Customer Group"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Customer Group",
		},
    {
			"fieldname": "partner_group",
			"label": __("Partner Group"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Partner Group"

		},
    {
			"fieldname": "distributor",
			"label": __("Distributor"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Distributor"

		},
    {
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Customer",
			"get_query" : function() {
        let filters = [];

        if(frappe.query_report.get_filter_value('territory')){
          filters.push(["territory", "=", frappe.query_report.get_filter_value('territory')]);
        }
        if(frappe.query_report.get_filter_value('customer_group')){
          filters.push(["customer_group", "=", frappe.query_report.get_filter_value('customer_group')]);
        }
        if(frappe.query_report.get_filter_value('partner_group')){
          filters.push(["partner_group", "=", frappe.query_report.get_filter_value('partner_group')]);
        }
        if(frappe.query_report.get_filter_value('distributor')){
          filters.push(["distributor", "=", frappe.query_report.get_filter_value('distributor')]);
        }

				return {
					"doctype": "Customer",
					"filters": filters
				}
			}
		},
		{
			"fieldname": "brand",
			"label": __("Brand"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Brand",
		},
    {
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Item Group",
		},
    {
			"fieldname": "item",
			"label": __("Item"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Item",
      "get_query" : function() {
        let filters = [];

        if(frappe.query_report.get_filter_value('brand')){
          filters.push(["brand", "=", frappe.query_report.get_filter_value('brand')]);
        }
        if(frappe.query_report.get_filter_value('item_group')){
          filters.push(["item_group", "=", frappe.query_report.get_filter_value('item_group')]);
        }

				return {
					"doctype": "Item",
					"filters": filters
				}
			}
		},
		// {
		// 	"fieldname": "status",
		// 	"label": __("Status"),
		// 	"fieldtype": "Select",
		// 	"width": "100",
		// 	"options": [
    //     "",
		// 		"Draft",
		// 		"Submitted",
		// 		"Cancelled"
		// 	],
		// 	"default": "Submitted"
		// },
	]
};
