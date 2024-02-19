
frappe.listview_settings['Customer'] = {
	onload: function(listview) {
		var method = "field_force.field_force.hook_functions.customer.generate_customer_id_if_not_exist";
    listview.page.add_menu_item(__("Generate Retail Customer's ID"), function () {
      frappe.call({
        method: method,
        args: {},
        callback: function (r) {
          console.log(r.message);
        }
      }, ("Action"));
    });
	}
}
