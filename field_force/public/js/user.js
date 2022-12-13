frappe.ui.form.on('User', {
    onload: function (frm){
        console.log("Custom js working");
        frm.set_value("time_zone", "Asia/Dhaka")
    }
})