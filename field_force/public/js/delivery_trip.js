frappe.ui.form.on('Delivery Trip', {
    onload: function(frm) {
        // this.page.remove_button(__("Notify Customers via Email"));

        let queryString = frm.doc.custom_requisition_list;
        if (queryString){
            frappe.call({
                method: 'field_force.field_force.hook_functions.delivery_trip.get_requistion_for_delivery_trip',
                args: {
                    'requisitions': queryString
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
                        frm.set_value("custom_requisition_list","")
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
                delivery_trip_created: 0,
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
        frm.remove_custom_button('Notify Customers via Email');
    }, 10);
	},
    get_files : function(frm) {
        var url = `/api/method/field_force.field_force.hook_functions.delivery_trip.download_all_files`;
        url = url + `?doc_data=${frm.doc.name}`;
        window.open(url, '_blank');
	},
	after_workflow_action: function(frm) {
		frappe.call({
            method: 'field_force.field_force.hook_functions.delivery_trip.set_lead_time_and_action_user',
            args: {
                'doc_name': frm.doc.name
            },
        })
        if (frm.doc.workflow_state == "Pending") {
		    frm.set_value("created_at",frm.doc.creation)
		    frm.set_value("created_by",frm.doc.owner)
		}else if (frm.doc.workflow_state == "Scheduled") {
		    frm.set_value("logistic_approval",frappe.datetime.now_datetime())
		    frm.set_value("logistic_approved_by",frappe.session.user)
		}
    }

})

frappe.ui.form.on('Delivery Stop', {
    visited: function(frm,cdt,cdn) {
        let item = locals[cdt][cdn];
        if (item.visited == 1) {
            item.status = "Completed"
            item.custom_delivered_datetime = frappe.datetime.now_datetime()
            frm.refresh_field("custom_delivered_datetime")
        }else{
            item.status = frm.doc.workflow_state
        }
        frm.refresh_field("delivery_stops")
    }
})
