frappe.listview_settings['Sales Person'] = {
    onload: function(listView) {
      listView.page.add_menu_item(__("Refresh All Sales Person's Customer List"), function () {
        frappe.call({
          method: "field_force.field_force.hook_functions.customer.enqueue_refresh_sales_person_customers",
          args: {},
          callback: function (r) {
            console.log(r.message);
          }
        }, ("Action"));
      });
    }
}
