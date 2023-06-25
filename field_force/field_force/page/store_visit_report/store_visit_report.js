frappe.pages['store-visit-report'].on_page_load = function(wrapper) {
  frappe.require("assets/field_force/css/page_modal.css");

    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Store Visit Report',
        single_column: true
    });

    window.addEventListener("click", function(event) {
      if (event.target.id !== "image") {
        document.getElementById('modal_section').style.display = 'none';
      }
    });

    $('.page-body').css('background', '#FFFFFF');
    new DailyAppUserAttendanceReport(page);
};

class DailyAppUserAttendanceReport {
    constructor(page) {
        this.page = page;
        this.make_form();
        this.make_menu();
        this.initialize_modal();
        // this.open_image_modal()
    }

    make_menu = () => {
        this.page.add_action_icon("refresh", () => {
            this.fetch_and_render();
        });
        this.page.add_menu_item("Export", ()=>{
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
                    fieldname: 'sales_person',
                    label: __('Sales Person'),
                    fieldtype: 'Link',
                    options: 'Sales Person',
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
                    fieldtype: 'Column Break'
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
        let {from_date, to_date, sales_person, customer} = this.form.get_values();
        if (!from_date) {
            this.form.get_field('preview').html('');
            return;
        }
        this.form.get_field('preview').html(`
        	<div class="text-muted margin-top">
        		${__("Fetching...")}
        	</div>
        `);
        frappe.call('field_force.field_force.page.store_visit_report.store_visit_report.execute', {
            filters: {
                from_date: from_date,
                to_date: to_date,
                sales_person: sales_person,
                customer: customer
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
        this.form.get_field('preview').html(`<table class="table table-bordered" id="export_excel">${table_header}${table_body}</table>`);
    }
    table_header = (headers) => {
        let table_header = `<thead><tr>`;

        headers.forEach(function (data, index){
            table_header += `<th scope="col" width="${data.width}">${data.label || ''}</th>`;
        })

        table_header += `</tr>`;
        return table_header;
    }

    table_body = (diff, fields) => {
        var html = `<tbody>`;
        var serial_number = 1;

        diff.forEach(function (data, index) {
            html += `<tr>`;

            fields.forEach(function (field, index){
              if (field.fieldname === 'sl'){
                html += get_absolute_format_and_html(field, serial_number);
              }
              else {
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
        let {from_date, to_date, sales_person, customer} = this.form.get_values();
        let url = `/api/method/field_force.field_force.page.store_visit_report.store_visit_report.export_file`;
        url += `?from_date=${from_date||''}&to_date=${to_date||''}&sales_person=${sales_person||''}&customer=${customer||''}`;
        window.open(url, '_blank');
    }
}

function get_absolute_format_and_html(field, value){
    if (field.fieldtype === "Image"){
        return get_image_html(value);
    }
    else if (field.fieldtype === "Currency"){
        return get_currency_format(value);
    }
    else if (field.fieldtype ==="Data") {
        return `<td>${value || ''}</td>`;
    }
    else {
        return `<td>${value || ''}</td>`;
    }
}

function get_image_html(image_url) {
    let rotate = "transform: rotate(-90deg)"

    if (image_url === "/files/default-image.png"){
        rotate = '';
    }

    return `
        <td style="height:100px; width:120px;">
            <a href="#">
                <img style="height:100%; width:100%;" src="${image_url}" id="image" img-path="${image_url}" onclick="(
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

function get_currency_format(value){
    const company = frappe.defaults.get_user_default("company");
    const currency = frappe.get_doc(":Company", company).default_currency;
    let value_in_currency = format_currency(value, currency);
    return `<td>${value_in_currency || ''}</td>`
}
