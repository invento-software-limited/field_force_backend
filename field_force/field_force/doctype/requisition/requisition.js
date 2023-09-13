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
				brand_commissions = r.message;
			}
			// else{
			// 	console.log("====>>", r)
			// }
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
		frm.fields_dict['items'].grid.get_field('item_code').get_query = function(doc, cdt, cdn) {
			let item = locals[cdt][cdn];

		  	return {
			  	query: "erpnext.controllers.queries.item_query",
				args: {
			  		'txt': item.item_code
				},
				searchfield: 'product_id',
				filters: {}
		  	};
		};

		frm.add_custom_button(__('New Requisition'), () => {
			frappe.new_doc("Requisition");
	    }, "fa fa-plus", "btn-default","new_requisition");

		// frappe.ui.keys.add_shortcut("Alt+N", function() {
		// 	btn.trigger("click");
		// }, "Requisition","new_requisition");

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
		var filters_ = [];

		if (frm.doc.partner_group!=='' && frm.doc.partner_group!==null && frm.doc.partner_group !== undefined) {
			filters_ = [
				["Customer", "partner_group", "=", frm.doc.partner_group]
			]
		}
		frm.set_query("customer", function () {
			return {
				filters: filters_
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
		if (!is_sales_person_exists(frm) && frm.doc.sales_person !==""){
            frm.add_child('sales_team', {
                sales_person: frm.doc.sales_person,
                allocated_percentage: 100,
                employee: frm.doc.employee,
                user: frm.doc.user,
            });
            frm.refresh_fields("sales_team");
        }
    },

	scan_barcode: function(frm) {
		let transaction_controller= new erpnext.TransactionController({frm:frm});
		transaction_controller.scan_barcode();
	},
  po_file: function (frm){
      if (!frm.doc.po_file){
        return
      }

      frappe.call({
            method:"field_force.field_force.doctype.utils.get_data_from_pdf",
            args: {
                url: frm.doc.po_file
              },

            callback: function(r) {
                if(r.message) {
                    frm.doc.items = [];
                    r.message.forEach((item, i) => {
                      if (i >= 0){
                        let row = frm.add_child("items", item);
                        // frappe.model.set_value(row.doctype, row.name, 'item_code', item.item_code);
                        // frappe.model.set_value(row.doctype, row.name, 'qty', item.qty);
                        // frappe.model.set_value(row.doctype, row.name, 'rate', item.rate);
                      }
                    });
                    refresh_field("items");
                }

                // if(r.message){
                //     console.log((r.message));
                //
                //     // frm.set_value('items', r.message);
                //     // frm.refresh_field("items");
                // }
            }
        });
    },

});

function is_sales_person_exists(frm) {
	var exists = false;

	if (frm.doc.sales_te){
		frm.doc.sales_team.forEach(function (data) {
			if (frm.doc.sales_person === data.sales_person) {
				exists = true;
				return 0;
			}
		})
	}
	return exists;
}

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

var item_data = {}

frappe.ui.form.on("Requisition Item", {
	item_code: function(frm,cdt,cdn) {
		let row = locals[cdt][cdn];
		let item_str = cdt + cdn

		if (row.item_code && !frm.doc.customer){
			frappe.model.set_value(cdt, cdn, "item_code");
			frm.refresh_field(cdt, cdn, "item_code");
			frappe.throw("Please specify: Customer. It is needed to fetch Item Details.\n")
		}

		if (frm.doc.delivery_date) {
			row.delivery_date = frm.doc.delivery_date;
			refresh_field("delivery_date", cdn, "items");
		} else {
			frm.script_manager.copy_from_first_row("items", row, ["delivery_date"]);
		}

		if (row.item_code !== '' && row.item_code !== null
			&& row.item_code !== undefined && row.item_code !== item_data[item_str]){
			get_and_set_item_details(frm, cdt,cdn, row);
		}
	},
	price_list_rate: function (frm, cdt, cdn){
		set_rate_and_amount(frm, cdt, cdn);
	},
	qty: function(frm, cdt, cdn){
		parse_value_to_float(cdt, cdn, 'qty');
		set_amount(frm, cdt, cdn);
		set_absolute_values(frm);
	},
	discount_percentage: function (frm, cdt, cdn){
		parse_value_to_float(cdt, cdn, 'discount_percentage');
		set_rate_and_amount(frm, cdt, cdn);
	},
	discount_amount: function(frm, cdt, cdn){
		parse_value_to_float(cdt, cdn, 'rate');

		let row = locals[cdt][cdn];
		let rate = row.price_list_rate - row.discount_amount

		if (row.price_list_rate && row.discount_amount){
			let discount_percentage = 100 * (row.discount_amount / row.price_list_rate)

			if (row.discount_percentage != discount_percentage){
				frappe.model.set_value(cdt, cdn, "discount_percentage", discount_percentage);
			}
		}

		frappe.model.set_value(cdt, cdn, "rate", rate);
		set_absolute_values(frm);
	},
	rate: function(frm, cdt, cdn){
		parse_value_to_float(cdt, cdn, 'rate');
		set_amount(frm, cdt, cdn);
		calculate_discount_and_amount(frm, cdt, cdn);
		// set_rate_and_amount(frm, cdt, cdn);
	},
	delivery_date: function(frm, cdt, cdn) {
		if(!frm.doc.delivery_date) {
			erpnext.utils.copy_value_in_all_rows(frm.doc, cdt, cdn, "items", "delivery_date");
		}
	}
});

function set_rate_and_amount(frm, cdt, cdn){
	let row = locals[cdt][cdn];
	// if (row.discount_percentage > 0){
	// 	console.log(row.discount_percentage);

	let discount_amount = (row.price_list_rate * (row.discount_percentage/100));
	let rate = row.price_list_rate - discount_amount

	if (row.discount_amount != discount_amount) {
		frappe.model.set_value(cdt, cdn, "discount_amount", discount_amount);
	}
	if (row.rate != rate) {
		frappe.model.set_value(cdt, cdn, "rate", rate);
	}
	// }
	// else if (row.rate === 0 || row.rate === null || row.rate === undefined){
	// 	frappe.model.set_value(cdt, cdn, "rate", row.price_list_rate);
	// 	frappe.model.set_value(cdt, cdn, "discount_amount", 0);
	// 	console.log(row.discount_amount)
	// }

	frappe.model.set_value(cdt, cdn, "amount", row.qty * row.rate);
	set_absolute_values(frm);
}

function set_discount_percentage(frm, cdt, cdn, item){
	if (item.brand) {
		if (brand_commissions[item.brand] !== undefined){
			frappe.model.set_value(cdt, cdn, "discount_percentage", brand_commissions[item.brand])
		}
		else{
			frappe.model.set_value(cdt, cdn, "discount_percentage", 0);
		}
		frm.refresh_field(cdt, cdn, "discount_percentage")
	}
}

function set_amount(frm, cdt, cdn) {
	var row = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "amount", row.qty * row.rate);
}

function calculate_discount_and_amount(frm, cdt, cdn) {
	let row = locals[cdt][cdn];

	if (row.price_list_rate && row.rate){
		let discount_amount = row.price_list_rate - row.rate;
		let discount_percentage = (discount_amount / row.price_list_rate) * 100;
		frappe.model.set_value(cdt, cdn, 'discount_amount', discount_amount);
		frappe.model.set_value(cdt, cdn, 'discount_percentage', discount_percentage);
		frm.refresh_fields()
	}
}

function parse_value_to_float(cdt, cdn, field){
	let item = locals[cdt][cdn]

	if(typeof item[field] === 'string'){
		frappe.model.set_value(cdt, cdn, field, parseFloat(item[field]));
	}
}

function get_and_set_item_details(frm, cdt, cdn, row){
	frappe.call({
		method: 'field_force.field_force.doctype.requisition.requisition.get_item_details',
		args: {
			'item_code': row.item_code
		},
		callback: function(r) {
			if (!r.exc) {
				let item = r.message;
				// console.log(item, row.item_code, frappe.model.get_value(cdt, cdn, 'item_code'));

				if (row.item_code !== item.name){
					let item_str = cdt + cdn;
					item_data[item_str] = item.item_code;

					frappe.model.set_value(cdt, cdn, "item_code", item.item_code);
					frm.refresh_field(cdt, cdn, "item_code");
				}

				set_item_values(frm, cdt, cdn, row, item);
				set_discount_percentage(frm, cdt, cdn, item);
				set_absolute_values(frm)
			}
		}
	})
}

function set_item_values(frm, cdt, cdn, row, item){
	frappe.model.set_value(cdt, cdn, "product_id", item.product_id);
	frappe.model.set_value(cdt, cdn, "item_name", item.item_name);
  frappe.model.set_value(cdt, cdn, "qty", 1);
	frappe.model.set_value(cdt, cdn, "brand", item.brand);
	frappe.model.set_value(cdt, cdn, "price_list_rate", item.price_list_rate);
	frm.refresh_fields(cdt, cdn);
}

