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
			"fieldname": "partner_group",
			"label": __("Partner Group"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Partner Group",
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Customer",
			"get_query" : function() {
        let filters = [];
        var distributor = frappe.query_report.get_filter_value('distributor');
        var partner_group = frappe.query_report.get_filter_value('partner_group');

        if (distributor){
          filters.push(
            ['distributor', '=', distributor]
          )
        }
        if (partner_group){
          filters.push(
            ['partner_group', '=', partner_group]
          )
        }

				return {
					"doctype": "Customer",
					"filters": filters
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
