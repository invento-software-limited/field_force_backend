frappe.ui.form.on('User', {
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
