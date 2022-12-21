// Copyright (c) 2022, Invento Software Limited and contributors
// For license information, please see license.txt
function open_email_dialog(frm){
	let message = "hello";

	new frappe.views.CommunicationComposer({
		doc: frm.doc,
		frm: frm,
		sender: 'bib.demo2@gmail.com',
		subject: __(frm.meta.name) + ': ' + frm.docname,
		recipients: frm.doc.email_address || frm.doc.email,
		cc: "joyonto@gmail.com,",
		bcc: "hello@gmail.com,",
		attach_document_print: false,
		message: message
	});
}

var brand_commissions = {};

function get_brands_commissions(customer, brand=null){
	let response = null;

	frappe.call({
		method: 'field_force.field_force.doctype.requisition.requisition.get_brands_commission',
		args: {
			'customer': customer,
			'brand': brand,
		},
		callback: function(r) {
			if (!r.exc) {
				// code snippet
				console.log("=====>>>", r.message);
				brand_commissions = r.message;
			}
			else{
				console.log("====>>", r)
			}
		}
	});
	return response
}


frappe.ui.form.on('Requisition', {
	on_load: function (){
		if (frm.doc.requisition_excel === null){
			frm.set_df_property("requisition_excel", "hidden", true);
		}
		else {
			frm.set_df_property("requisition_excel", "hidden", false);
		}
	},
	refresh: function (frm){
		if (frm.doc.customer){
			brand_commissions = get_brands_commissions(frm.doc.customer)
		}
	},
	// before_submit: function (frm){
		// open_email_dialog(frm)
	// },
    // setup: function (frm){
    //     frm.add_fetch('customer', 'tax_id', 'tax_id');
    // },
	partner_group: function (frm){
		frm.set_value("customer", null);

		frm.set_query("customer", function() {
			return {
				filters: [
					["Customer","partner_group", "=", frm.doc.partner_group]
				]
			}
		});
	},
	customer: function (frm){
		if (frm.doc.customer) {
			brand_commissions = get_brands_commissions(frm.doc.customer)
		}
	},

    delivery_date: function(frm) {
		$.each(frm.doc.items || [], function(i, d) {
			if(!d.delivery_date) d.delivery_date = frm.doc.delivery_date;
		});
		refresh_field("items");
	},
	sales_person: function (frm){
        console.log("Custom js working");

        if (frm.doc.sales_person !=="" ){
            let row = frm.add_child('sales_team', {
                sales_person: frm.doc.sales_person,
                allocated_percentage: 100,
                employee: frm.doc.employee,
                user: frm.doc.user,
            });

            frm.refresh_fields("sales_team");
        }
    }

});

function set_absolute_values(frm){
	let total = 0;
	let total_qty = 0;
	let total_items = 0;

	if(frm.doc.items?.length) {
		$.each(frm.doc.items, function(index, item) {
			if (item.amount) {
				total += item.amount;
				total_qty += item.qty;
			}
			total_items += 1;
		})
	}
	frm.set_value("total", total);
	frm.set_value("net_total", total);
	frm.set_value("grand_total", total);
	frm.set_value("total_qty", total_qty);
	frm.set_value("total_items", total_items);
	frm.refresh_fields();
}

frappe.ui.form.on("Requisition Item", {
	item_code: function(frm,cdt,cdn) {
		console.log("Item added");
		console.log("======>>>", brand_commissions);

		var row = locals[cdt][cdn];
		if (frm.doc.delivery_date) {
			row.delivery_date = frm.doc.delivery_date;
			refresh_field("delivery_date", cdn, "items");
		} else {
			frm.script_manager.copy_from_first_row("items", row, ["delivery_date"]);
		}

		frappe.call({
			method: 'frappe.client.get_value',
			args: {
				'doctype': 'Item Price',
				'filters': {'item_code': row.item_code, 'selling': 1},
				'fieldname': [
					'item_name',
					'price_list_rate',
					'brand'
				]
			},
			callback: function(r) {
				if (!r.exc) {
					// console.log(r.message);
					let item = r.message;
					frappe.model.set_value(cdt, cdn, "price_list_rate", item.price_list_rate);

					if (item.brand) {
						// console.log("commission ===>>", brand_commissions);
						if (brand_commissions[item.brand] !== undefined){
							frappe.model.set_value(cdt, cdn, "discount_percentage", brand_commissions[item.brand])
						}
						else{
							frappe.model.set_value(cdt, cdn, "discount_percentage", 0);
						}
					}
					set_absolute_values(frm);
				}
			}
		});
	},
	qty: function(frm, cdt, cdn){
		set_amount(frm, cdt, cdn);
	},
	discount_percentage: function (frm, cdt, cdn){
		set_rate_and_amount(frm, cdt, cdn);
	},
	discount_amount: function(frm, cdt, cdn){
		let row = locals[cdt][cdn];
		let rate = row.price_list_rate - row.discount_amount

		if (row.price_list_rate && row.discount_amount){
			let discount_percentage = 100 * (row.discount_amount / row.price_list_rate)
			frappe.model.set_value(cdt, cdn, "discount_percentage", discount_percentage);
		}

		frappe.model.set_value(cdt, cdn, "rate", rate);
		set_absolute_values(frm);
	},
	rate: function(frm, cdt, cdn){
		set_rate_and_amount(frm, cdt, cdn);
	},
	delivery_date: function(frm, cdt, cdn) {

		if(!frm.doc.delivery_date) {
			erpnext.utils.copy_value_in_all_rows(frm.doc, cdt, cdn, "items", "delivery_date");
		}
	}
});

function set_rate_and_amount(frm, cdt, cdn){
	let row = locals[cdt][cdn];
	// console.log("rate====>>>", row.rate);
	// console.log("prate====>>>", row.price_list_rate);

	if (row.discount_percentage > 0){
		let discount_amount = (row.price_list_rate * (row.discount_percentage/100));
		row.rate = row.price_list_rate - discount_amount
		frappe.model.set_value(cdt, cdn, "discount_amount", discount_amount);
		frappe.model.set_value(cdt, cdn, "rate", row.rate);
	}
	else if (row.rate === 0 || row.rate === null || row.rate === undefined){
		frappe.model.set_value(cdt, cdn, "rate", row.price_list_rate);
	}

	frappe.model.set_value(cdt, cdn, "amount", row.qty * row.rate);
	set_absolute_values(frm);
}

function set_amount(frm, cdt, cdn){
	var row = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "amount", row.qty * row.rate);
	set_absolute_values(frm);
}
