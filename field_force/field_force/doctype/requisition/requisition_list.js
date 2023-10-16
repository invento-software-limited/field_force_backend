function check_role(){
  if (frappe.user.has_role("Customer") && !frappe.user.has_role("System Manager")
      && !window.location.href.includes('/customer-requisition/')) {
      let url = window.location.href;
	    window.location.href = url.replace("/requisition/", "/customer-requisition/");
  }
}

frappe.listview_settings['Requisition'] = {
  onload: function (){
    check_role();
  },
  primary_action: function () {
    frappe.new_doc("Requisition");
			let url = window.location.href;
			window.location.href = url.replace("/requisition/", "/customer-requisition/");
  }
}
