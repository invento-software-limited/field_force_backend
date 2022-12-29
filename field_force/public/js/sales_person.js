frappe.ui.form.on('Sales Person', {
    onload: function (frm){
        if (frm.doc.name.startsWith("new-sales-person")){
            cur_frm.set_value("employee", "");
            cur_frm.refresh_fields("employee");        
        }
    }
})