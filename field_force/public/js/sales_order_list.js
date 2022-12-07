frappe.listview_settings['Sales Order'] = {
    get_indicator: function (){
        console.log("Ignored all indicators..");
    },

	// onload: function(listview) {
	// 	var method = "erpnext.selling.doctype.sales_order.sales_order.close_or_unclose_sales_orders";
	//
	// 	listview.page.add_menu_item(__("Close"), function() {
	// 		listview.call_for_selected_items(method, {"status": "Closed"});
	// 	});
	//
	// 	listview.page.add_menu_item(__("Re-open"), function() {
	// 		listview.call_for_selected_items(method, {"status": "Submitted"});
	// 	});
	// }
}