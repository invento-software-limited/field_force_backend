// Copyright (c) 2022, Invento Software Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Store Visit Assign', {
	onload: function (frm){
		frm.fields_dict['destinations'].grid.get_field('customer').get_query = function(doc, cdt, cdn) {
		  	return {
				filters: {
					sales_person: frm.doc.sales_person
				}
		  	};
		};
	},

	refresh: function(frm) {
        console.log("it works!");
	}
});

frappe.ui.form.on("Store Visit Destination", {
	refresh: function(frm) {
        console.log("child table!")
	},
    // exp_hour: function(frm, cdt, cdn) {
    //     console.log(locals[cdt][cdn])
    // },
    // exp_minute: function(frm, cdt, cdn){
    //     console.log(locals[cdt][cdn])
    // },
    // exp_format: function(frm, cdt, cdn){
    //     console.log(locals[cdt][cdn])
    // },
    // time_till_hour: function(frm, cdt, cdn){
    //     console.log(locals[cdt][cdn])
    // },
    // time_till_minute: function(frm, cdt, cdn){
    //     console.log(locals[cdt][cdn])
    // },
    // time_till_format: function(frm, cdt, cdn){
    //     console.log(locals[cdt][cdn])
    // }
});
