frappe.ui.form.on('User', {
    refresh : function(frm) {
        if (frappe.user.has_role('Admin')) {
            frm.add_custom_button(__('Generate Keys'), function(){
                frappe.call({
                    method: "field_force.field_force.hook_functions.user.generate_keys",
                    args: {
                        user: frm.doc.name,
                    },
                    callback: function (r) {
                        if (r.message) {
                            frappe.msgprint(__("Save API Secret: {0}", [r.message.api_secret]));
                            frm.reload_doc();
                        }
                    },
                });
            });
        }   
    },
    onload: function (frm){
        console.log("Custom js working");
        frm.set_value("time_zone", "Asia/Dhaka")
    }
})