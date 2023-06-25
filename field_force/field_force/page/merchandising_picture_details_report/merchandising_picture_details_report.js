frappe.pages['merchandising-picture-details-report'].on_page_load = function (wrapper) {
  frappe.require("assets/field_force/css/page_modal.css");
  var page = frappe.ui.make_app_page({
    parent: wrapper,
    title: 'Merchandising Picture Details Report',
    single_column: true
  });

  $('.page-body').css('background', '#FFFFFF');

  window.addEventListener("click", function(event) {
      if (event.target.id !== "image") {
        document.getElementById('modal_section').style.display = 'none';
      }
  });

  new MerchandisingPictureDetailsReport(page)
  applyEditableFieldsEvent();
}

function applyEditableFieldsEvent(){
  $(document).on('click', '.editable-field', function (e) {
    var $field = $(this);
    var value = $field.text();
    var fieldname = $field.attr('data-fieldname');
    var docname = $field.attr('data-name');
    // console.log($field, value, fieldname, docname);

    // Open an input field for inline editing
    var $input = $('<textarea autocomplete="off" class="fill-textarea input" ' +
      'data-fieldtype="Small Text" data-fieldname="details" placeholder="" data-doctype="Merchandising ' +
      'Picture"></textarea>')
      .attr('type', 'text')
      .val(value)
      .appendTo($field.empty())
      .focus();

    // Save the updated value on input blur
    $input.on('blur', function () {
      updateValue($field, $input, docname, fieldname);
    });

    // Save the updated value on input Enter
    $input.on('keypress', function (e) {
      if (e.key === 'Enter'){
        updateValue($field, $input, docname, fieldname);
      }
    });
  })
}

function updateValue(field, input, docname, fieldname){
  var updatedValue = input.val();
  field.text(updatedValue);

  // Make an AJAX request to update the field value
  frappe.call({
    method: 'field_force.field_force.page.merchandising_picture_details_report.merchandising_picture_details_report.update_field',
    args: {
      docname: docname,
      fieldname: fieldname,
      value: updatedValue
    },
    callback: function (response) {
      if (response.message) {
        // Refresh the report after successful update
        console.log("feedback updated");
      } else {
        // Handle update failure
        frappe.msgprint('Failed to update feedback');
      }
    }
  });
}


class MerchandisingPictureDetailsReport {
  constructor(page) {
    this.page = page;
    this.make_form();
    this.make_menu();
    this.initialize_modal();
    // this.open_image_modal()
    // this.initialize_events();
  }

  initialize_events = () => {

  }

  make_menu = () => {
    this.page.add_action_icon("refresh", () => {
      this.fetch_and_render();
    });
    this.page.add_menu_item("Export", () => {
      this.export_excel()
    })
  }
  make_form = () => {
    this.form = new frappe.ui.FieldGroup({
      fields: [
        {

          fieldname: 'from_date',
          label: __('From Date'),
          fieldtype: 'Date',
          default: frappe.datetime.get_today(),
          change: () => this.fetch_and_render(),
          reqd: 1,
        },
        {
          fieldtype: 'Column Break'
        },
        {
          fieldname: 'to_date',
          label: __('To Date'),
          fieldtype: 'Date',
          default: frappe.datetime.get_today(),
          change: () => this.fetch_and_render(),
        },
        {
          fieldtype: 'Column Break'
        },
        {
          fieldname: 'brand',
          label: __('Brand'),
          fieldtype: 'Link',
          options: 'Brand',
          change: () => this.fetch_and_render(),
        },
        {
          fieldtype: 'Column Break'
        },
        {
          fieldname: 'customer',
          label: __('Customer'),
          fieldtype: 'Link',
          options: 'Customer',
          change: () => this.fetch_and_render(),
        },
        {
          fieldtype: 'Column Break'
        },
        {
          fieldname: 'sales_person',
          label: __('Sales Person'),
          fieldtype: 'Link',
          options: 'Sales Person',
          change: () => this.fetch_and_render(),
        },
        {
          fieldtype: 'Section Break'
        },
        {
          fieldtype: 'HTML',
          fieldname: 'preview'
        }
      ],
      body: this.page.body
    });
    this.form.make();
  }
  initialize_modal = () => {
    let html = `<div id="modal_section" class="modal_">
        <div class="modal-image">
        <img class="modal-content_" id="img" alt="img">
        </div>
      </div>`
    // this.form.body.append(html);
    $('.main-section').append(html)
  }
  fetch_and_render = () => {
    let {from_date, to_date, brand, customer, sales_person} = this.form.get_values();
    if (!from_date) {
      this.form.get_field('preview').html('');
      return;
    }
    this.form.get_field('preview').html(`
        	<div class="text-muted margin-top">
        		${__("Fetching...")}
        	</div>
        `);
    frappe.call('field_force.field_force.page.merchandising_picture_details_report.merchandising_picture_details_report.get_merchandising_picture_data', {
      filters: {
        from_date: from_date,
        to_date: to_date,
        sales_person: sales_person,
        customer: customer,
        brand: brand
      },
      freeze: true
    }).then(r => {
      let diff = r.message[0];
      let fields = r.message[1];
      this.render(diff, fields);
    });
  }

  render = (diff, fields) => {
    let table_header = this.table_header(fields);
    let table_body = this.table_body(diff, fields);
    this.form.get_field('preview').html(
      `<div>
            <table class="table table-bordered" id="export_excel">
                  ${table_header}${table_body}
            </table>
          </div>`);
    //Add event listener for inline editing
  }
  table_header = (headers) => {
    let table_header = `<thead><tr>`;

    headers.forEach(function (field, index) {
      table_header += `<th scope="col" width="${field.width}">${field.label || ''}</th>`;
    })

    table_header += `</tr>`;
    return table_header;
  }

  table_body = (diff, fields) => {
    var html = `<tbody>`;
    var serial_number = 1;

    diff.forEach(function (data, index) {
      html += `<tr>`;

      fields.forEach(function (field, index) {
        if (field.fieldname === 'sl') {
          html += get_absolute_format_and_html(field, serial_number);
        } else if (field.editable) {
          html += `<td class="editable-field parent-container" data-fieldname="${field.fieldname}"
                   data-name="${data.docname}">${data[field.fieldname] || ''}</td>`
        } else {
          html += get_absolute_format_and_html(field, data[field.fieldname]);
        }
      })

      html += `</tr>`;
      serial_number = serial_number + 1;
    })

    html += `</tbody>`;
    return html
  }

  export_excel = () => {
    let {from_date, to_date, brand, customer, sales_person} = this.form.get_values();
    let url = `/api/method/field_force.field_force.page.merchandising_picture_details_report.merchandising_picture_details_report.export_file`;
    url += `?from_date=${from_date || ''}&to_date=${to_date || ''}&brand=${brand || ''}&customer=${customer || ''}&sales_person=${sales_person || ''}`;
    window.open(url, '_blank');
  }
}

function get_absolute_format_and_html(field, value, width = 50) {
  if (field.fieldtype === "Image") {
    return get_image_html(value);
  } else if (field.fieldtype === "Currency") {
    return get_currency_format(value);
  } else if (field.fieldtype === "Data") {
    return `<td width="${width}px">${value || ''}</td>`;
  } else {
    return `<td width="${width}px">${value || ''}</td>`;
  }
}

function get_image_html(image_url) {
  return `
        <td style="height:100px; width:120px;">
            <a href="#">
                <img style="height:100%; width:100%" id="image" src="${image_url}" onclick="(
                    function(e){
                        document.getElementById(\'modal_section\').style.display=\'block\';
                        var nAgt = navigator.userAgent;
                        if (nAgt.indexOf('Safari') !== -1) {
                            document.getElementById(\'img\').src=e.target.currentSrc;
                        }else{
                            document.getElementById(\'img\').src=e.path[0].currentSrc;
                        }
                        return false;
                    }
                )(arguments[0]);
                return false;">
            </a>
        </td>`;
}

function get_currency_format(value) {
  const company = frappe.defaults.get_user_default("company");
  const currency = frappe.get_doc(":Company", company).default_currency;
  let value_in_currency = format_currency(value, currency);
  return `<td>${value_in_currency || ''}</td>`
}
