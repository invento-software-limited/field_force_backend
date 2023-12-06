frappe.ui.form.on('Delivery Trip', {
    onload: function(frm) {
        let queryString = window.location.search;
        if (queryString){
            let queryStringWithoutQuestionMark = queryString.substring(1);
            frappe.call({
                method: 'field_force.field_force.hook_functions.delivery_trip.get_requistion_for_delivery_trip',
                args: {
                    'requisitions': queryStringWithoutQuestionMark
                },
                callback: function(r) {
                    if (r.message) {
                        r.message.forEach(function(row){
                            let tb_row = frm.add_child("delivery_stops")
                            tb_row.requisition = row.requisition;
                            tb_row.customer = row.customer;
                            tb_row.grand_total = row.grand_total
                            tb_row.total_qty = row.total_qty
                        })
                        frm.refresh_field("delivery_stops")
                    }
                }
            })
        }
        
    },
    refresh: function (frm) {
		if (frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Get Requisition'),
				function() {
					erpnext.utils.map_current_doc({
                        method: "field_force.field_force.doctype.requisition.requisition.make_delivery_trip",
                        source_doctype: "Requisition",
                        target: frm,
                        setters: {
                            customer : frm.doc.customer,
                            territory : frm.doc.territory,
                            expected_delivery_date : frm.doc.expected_delivery_date,
                            company: frm.doc.company
                        },
                        get_query_filters: {
                            docstatus: 1,
                            company: frm.doc.company,
                            territory : frm.doc.territory
                        }
                    })
				}
			);
		}
        setTimeout(() => {
            frm.remove_custom_button('Delivery Note','Get customers from');
            frm.remove_custom_button('Delivery Notes','View');
        }, 10);
	},
    get_files : function(frm) {
        var url = `/api/method/field_force.field_force.hook_functions.delivery_trip.download_all_files`;
        url = url + `?doc_data=${frm.doc.name}`;
        window.open(url, '_blank');
	},
})