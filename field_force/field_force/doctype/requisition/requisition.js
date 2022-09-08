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


frappe.ui.form.on('Requisition', {
	on_load: function (){
		if (frm.doc.requisition_excel === null){
			frm.set_df_property("requisition_excel", "hidden", true);
		}
		else {
			frm.set_df_property("requisition_excel", "hidden", false);
		}
	},
    // setup: function (frm){
    //     frm.add_fetch('customer', 'tax_id', 'tax_id');
    // },
    delivery_date: function(frm) {
		$.each(frm.doc.items || [], function(i, d) {
			if(!d.delivery_date) d.delivery_date = frm.doc.delivery_date;
		});
		refresh_field("items");
	},
	before_submit: function (frm){
		open_email_dialog(frm)
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
					'price_list_rate'
				]
			},
			callback: function(r) {
				if (!r.exc) {
					// code snippet
					console.log(r.message);
					let item = r.message;
					// row.rate = item.price_list_rate;
					frappe.model.set_value(cdt, cdn, "rate", item.price_list_rate);
				}
			}
		});
	},
	qty: function(frm, cdt, cdn){
		var row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "amount", row.qty * row.rate);
		set_absolute_values(frm);
	},
	rate: function(frm, cdt, cdn){
		var row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "amount", row.qty * row.rate);
		set_absolute_values(frm);
	},
	delivery_date: function(frm, cdt, cdn) {
		if(!frm.doc.delivery_date) {
			erpnext.utils.copy_value_in_all_rows(frm.doc, cdt, cdn, "items", "delivery_date");
		}
	}
});
