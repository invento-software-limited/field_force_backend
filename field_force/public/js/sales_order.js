frappe.ui.form.on('Sales Order', {
    sales_person: function (frm){
        console.log("Custom js working");

        if (frm.doc.sales_person !=="" ){
            let row = frm.add_child('sales_team', {
                sales_person: frm.doc.sales_person,
                allocated_percentage: 100,
                employee: frm.doc.employee,
                user: frm.doc.user,
            });

            frm.refresh_fields("sales_team");
        }
    }
})