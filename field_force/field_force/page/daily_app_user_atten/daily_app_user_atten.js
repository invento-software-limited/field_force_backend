frappe.pages['daily-app-user-atten'].on_page_load = (wrapper) => {
    frappe.require("assets/field_force/css/page_modal.css");

    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Daily App User Attendance Report',
        single_column: true
    });

    $('.page-body').css('background', '#FFFFFF');
    new AppUserAttendanceReport(page);
};

class AppUserAttendanceReport {
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
                    fieldname: 'user',
                    label: __('User'),
                    fieldtype: 'Link',
                    options: 'User',
                    change: () => this.fetch_and_render(),
                },
                {
                    fieldtype: 'Column Break'
                },
                // {
                //     fieldname: 'type',
                //     label: __('Type'),
                //     fieldtype: 'Select',
                //     options: [
                //         {"value": "Checkin", "label": __("Check In")},
                //         {"value": "Checkout", "label": __("Check Out")},
                //     ],
                //     change: () => this.fetch_and_render(),
                // },
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
        let html = '<div id="modal_section" class="modal">\n' +
            '  <div class="modal-image">\n' +
            '  <img class="modal-content" id="img01" alt="img">\n' +
            '  <span class="close" onclick="document.getElementById(\'modal_section\').style.display=\'none\'">&times;</span>\n' +
            '  </div>\n' +
            '</div>'
        // this.form.body.append(html);
        $('.main-section').append(html)
    }
    fetch_and_render = () => {
        let {from_date, to_date, user, type} = this.form.get_values();
        if (!from_date) {
            this.form.get_field('preview').html('');
            return;
        }
        this.form.get_field('preview').html(`
        	<div class="text-muted margin-top">
        		${__("Fetching...")}
        	</div>
        `);
        frappe.call('field_force.field_force.page.daily_app_user_atten.daily_app_user_atten.get_user_attendance_data', {
            filters: {
                from_date: from_date,
                to_date: to_date,
                user: user,
                type: type
            },
            freeze: true
        }).then(r => {
            let diff = r.message;
            this.render(diff);
        });
    }

    render = (diff) => {
        let table_header = this.table_header();
        let table_body = this.table_body(diff);
        this.form.get_field('preview').html(`<table class="table table-bordered" id="export_excel">${table_header}${table_body}</table>`);
    }

    table_header = () => {
        let table_header = '<thead>\n' +
            '    <tr>\n' +
            '      <th scope="col" >SL</th>\n' +
            '      <th scope="col">Date</th>\n' +
            '      <th scope="col">Name</th>\n' +
            '      <th scope="col">User</th>\n' +
            '      <th scope="col">Checkin Time</th>\n' +
            '      <th scope="col">Checkout Time</th>\n' +
            '      <th scope="col">Checkin Device Time</th>\n' +
            '      <th scope="col">Checkout Device Time</th>\n' +
            '      <th scope="col">Checkin Image</th>\n' +
            '      <th scope="col">Checkout Image</th>\n' +
            '    </tr>\n' +
            '  </thead>\n';
        return table_header;
    }
    table_body = (diff) => {
        var html = "<tbody>";
        diff.forEach(function (data, index) {
            html += `<tr>`;
            html += '<td>' + data.sl + '</td>';
            html += '<td>' + `${data.server_date || ''}` + '</td>';
            html += '<td>' + `${data.name || ''}` + '</td>';
            html += '<td>' + `${data.user || ''}` + '</td>';
            html += '<td>' + `${data.server_time || ''}` + '</td>';
            html += '<td>' + `${data.checkout_time || ''}` + '</td>';
            html += '<td>' + `${data.device_time || ''}` + '</td>';
            html += '<td>' + `${data.checkout_device_time || ''}` + '</td>';
            html += '<td style="height:100px; width:120px;"><a href="#"><img style="height:100%; width:100%" ' + 'src="' + data.checkin_image + '" onclick="(function(e){document.getElementById(\'modal_section\').style.display=\'block\';' + 'document.getElementById(\'img01\').src=e.path[0].currentSrc;return false;})(arguments[0]);return false;"></a></td>';
            html += '<td style="height:100px; width:120px;"><a href="#"><img style="height:100%; width:100%" ' + 'src="' + data.checkout_image + '" onclick="(function(e){document.getElementById(\'modal_section\').style.display=\'block\';' + 'document.getElementById(\'img01\').src=e.path[0].currentSrc;return false;})(arguments[0]);return false;"></a></td>';
            html += `</tr>`;
        })
        html += "</tbody>";
        return html
    }
};