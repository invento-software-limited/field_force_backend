// Copyright (c) 2022, Invento Software Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('API DocType', {
	// refresh: function(frm) {

	// }
});

cur_frm.fields_dict.fields.get_query = function(doc) {
	return{
		filters:{
			'doctype': cur_frm.doctype.doc.value
		}
	}
}

