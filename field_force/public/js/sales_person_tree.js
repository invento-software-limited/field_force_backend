
frappe.treeview_settings["Sales Person"] = {
	fields: [
		{fieldtype:'Data', fieldname: 'sales_person_name',
			label:__('New Sales Person Name'), reqd:true},
		{fieldtype:'Data', fieldname:'employee_number',
			label:__('Employee Number'), reqd: 1,
			description: __("Please enter Employee Number of this sales person")},
		{fieldtype:'Check', fieldname:'is_group', label:__('Group Node'),
			description: __("Further nodes can be only created under 'Group' type nodes")}
	],
}
