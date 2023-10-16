function check_role(){
  console.log(frappe.user.has_role("Customer"), !has_common(frappe.user_roles, ["System Manager"]),
    !window.location.href.includes('/customer-requisition'));

  if (frappe.user.has_role("Customer") && !frappe.user.has_role("System Manager")
      && !window.location.href.includes('/customer-requisition')) {
      let url = window.location.href;
	    window.location.href = url.replace("/requisition/", "/customer-requisition");
  }
}

frappe.listview_settings['Requisition'] = {
  refresh: function (){
    check_role();
  },
  primary_action: function () {
      frappe.new_doc("Requisition");

      if (frappe.user.has_role("Customer") && !frappe.user.has_role("System Manager")
      && !window.location.href.includes('/customer-requisition')) {
        let url = window.location.href;
        window.location.href = url.replace("/requisition/", "/customer-requisition/");
      }
  }
}
