frappe.ui.form.on('Sales Person', {
    onload: function (frm){
        if (frm.doc.name.startsWith("new-sales-person")){
            cur_frm.set_value("employee", "");
            cur_frm.refresh_fields("employee");        
        }

        // frm.fields_dict['customers'].grid.get_field('customer').get_query = function(doc, cdt, cdn) {
		//   	return {
		// 		filters: {
		// 			sales_person: frm.doc.name
		// 		}
		//   	};
		// };
    }
})
