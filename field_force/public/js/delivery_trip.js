frappe.ui.form.on('Delivery Trip', {
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
		frappe.call({
            method:"field_force.field_force.hook_functions.delivery_trip.attach_pdf",
            args: {
                doc_data: frm.doc
              },
        });
	},
})

frappe.ui.form.on('Delivery Stop', {

    download_requisition: function(frm,cdt,cdn){
        let row = locals[cdt][cdn]
        if (row.requisition){
            var url = `/api/method/field_force.field_force.hook_functions.delivery_trip.attach_pdf`;
			url = url + `?doc_data=${row.requisition}`;
			window.open(url, '_blank');
        }
    },
    download_po: function(frm,cdt,cdn){
        let row = locals[cdt][cdn]
        if (row.requisition){
            frappe.db.get_value('Requisition', row.requisition, ['customer_po_file'], (result) => {
                if (result.customer_po_file) {
                    var url = `/api/method/field_force.field_force.hook_functions.delivery_trip.download_requisition_file`;
                    url = url + `?requisition_excel=${result.customer_po_file}`;
                    window.open(url, '_blank');
                }
            });
            
        }
    }

})
  