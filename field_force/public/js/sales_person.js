frappe.ui.form.on('Sales Person', {
  onload: function (frm) {
    if (frm.doc.name.startsWith("new-sales-person")) {
      cur_frm.set_value("employee", "");
      cur_frm.refresh_fields("employee");
    }

    // frm.fields_dict['customers'].grid.get_field('customer').get_query = function(doc, cdt, cdn) {
    //   	return {
    // 		filters: {
    // 			sales_person: frm.doc.name
    // 		}
    //   	};
    // };

    frm.set_query('distributor', function () {
      return {
        filters: {
          // Define your filter condition here
          customer_group: 'Distributor'
        }
      };
    });
  },
  distributor: function (frm) {
    if (frm.doc.distributor) {
      frappe.call({
        method: 'frappe.client.get_list',
        args: {
          doctype: 'Customer',
          filters: {
            distributor: frm.doc.distributor
          },
          fields: ['name as customer', 'partner_group', 'customer_group'],
          limit_page_length: 10000
        },
        callback: function (response) {
          // Process the retrieved documents
          var result = response.message;
          frm.set_value('customers', result)
        },
        error: function (err) {
          // Handle error, if any
          console.log(err);
        }
      });
    }
  }
})
