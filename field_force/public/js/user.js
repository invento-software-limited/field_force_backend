frappe.ui.form.on('User', {
    refresh : function(frm) {
        if (frappe.user.has_role('Admin')) {
            frm.add_custom_button(__('Log Out From App'), function(){
                frappe.call({
                    method: "field_force.field_force.hook_functions.user.generate_keys",
                    args: {
                        user: frm.doc.name,
                    },
                    callback: function (r) {
                        if (r.message) {
                            frappe.msgprint(__("<strong>{0}</strong> Has Been Logged Out From App",[frm.doc.name]));
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
    },
    type: function (frm){
      if (frm.doc.type !== "Customer"){
        frm.set_value("department", null);
      }
      else if (frm.doc.type !== "Warehouse") {
        frm.set_value("warehouse", null);
      }
    }


})
