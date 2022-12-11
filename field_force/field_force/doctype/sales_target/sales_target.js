// Copyright (c) 2022, Invento Software Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Target', {
    // onload: function (frm) {
    //     let button = $("[data-fieldname=get_sales_persons]");
    //     button.css('margin-top', '22px');
    //     button.css('margin-bottom', '7px');
    // },
	// refresh: function(frm) {

	// }

    setup: function(frm) {
		frm.set_query("reporting_person", function() {
			return {
				filters: [
					["Sales Person","is_group", "=", 1]
				]
			}
		});
	},

    get_sales_persons: function (frm){
        get_sales_persons(frm)
    }
});


function get_sales_persons(frm) {
    if (frm.doc.brand_group !== "") {
        frappe.call({
            method: "field_force.field_force.doctype.sales_target.sales_target.get_sales_persons",
            args: {
                reporting_person: frm.doc.reporting_person,
                exclude_group: true
            },
            callback: function (r) {
                if (r.message) {
                    frm.set_value('sales_persons_targets', r.message);
                    frm.refresh();
                } else {
                    frappe.msgprint(`Brands of '${frm.doc.brand_group}' not found!`)
                }
            }
        });
    } else {
        frappe.msgprint("Please select a brand group and try again")
    }
}