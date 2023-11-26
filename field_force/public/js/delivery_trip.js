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
  })
  