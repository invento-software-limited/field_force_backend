// Copyright (c) 2022, Invento Software Limited and contributors
// For license information, please see license.txt
/* eslint-disable */

var sales_person = null;

function get_sales_person() {
	if (frappe.user.has_role("System Manager") !== undefined) {
		frappe.call({
			method: "frappe.client.get",
			async: false,
			args: {
				doctype: "Sales Person",
				name: "Sales Team",
			},
			callback(r) {
				if (r.message) {
					console.log(r.message)
					sales_person = r.message;
				}
			}
		});
	}
	else {
		frappe.call({
			method: 'frappe.client.get_value',
			async: false,
			args: {
				'doctype': 'Sales Person',
				'filters': {'user': frappe.session.user},
				'fieldname': ['name', 'type', 'lft', 'rgt']
			},
			callback: function (r) {
				if (!r.exc) {
					// console.log(r.message.name)
					sales_person = r.message;

					// if (!sales_person){
					// 	sales_person = frappe.get_doc("Sales Person", "Sales Team");
					// }
				}
			}
		})
	}
}

get_sales_person()


function get_type(sales_person) {
	console.log(sales_person);
	if (sales_person.type === 'Channel Manager') {
		return "By Manager"
	} else if (sales_person.type === "Manager") {
		return "By Supervisor"
	} else {
		return "Individual"
	}
}

frappe.query_reports["Sales Target vs Achievement Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_start(),
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
			"fieldname": "sales_person",
			"label": __("Reporting Person"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Sales Person",
			"default": sales_person.name,
			"get_query": function (){
				return {
					"filters": [
						// "parent_sales_person": sales_person.name
						["lft", ">=", sales_person.lft],
						["rgt", "<=", sales_person.rgt]
					]
				}
			}
		},
		{
			"fieldname": "type",
			"label": __("Type"),
			"fieldtype": "Select",
			"width": "100",
			"options": [
				"Individual",
				"By Supervisor",
				"By Manager",
			],
			"default": get_type(sales_person)
		}
	]
}

