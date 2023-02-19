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
				'filters': {'user': frappe.session.user, 'is_group':1},
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

var months =[
	"January",
	"February",
	"March",
	"April",
	"May",
	"June",
	"July",
	"August",
	"September",
	"October",
	"November",
	"December"
]

const d = new Date();
let month = d.getMonth();
let year = d.getFullYear();

frappe.query_reports["Sales Target vs Achievement Report"] = {
	"filters": [
		{
			"fieldname":"month",
			"label": __("Month"),
			"fieldtype": "Select",
			"default": months[month],
			"options": months,
			"width": "60px",
			"reqd": 1
		},
		{
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Select",
			"options": [2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030],
			"default": year,
			"width": "60px",
			"reqd": 1
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
						["is_group", "=", 1],
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
