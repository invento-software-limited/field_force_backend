frappe.pages['requisition-report'].on_page_load = function (wrapper) {

	var page = frappe.ui.make_app_page({
	  parent: wrapper,
	  title: 'Requisition Report',
	  single_column: true
	})
  
	set_background_color();

	
  
	new RequisitionReport(page)
  }
  
  class RequisitionReport {
	constructor(page) {
	  this.page = page;
	  this.make_form();
	  this.make_menu();
	  // this.initialize_modal();
	  // this.open_image_modal()
	  // this.initialize_events();
	}
  
	initialize_events = () => {
	  this.fetch_and_render();
	}
  
	make_menu = () => {
  
	  this.page.add_action_icon("refresh", () => {
		this.fetch_and_render(true);
	  }, "Refresh");
  
	  // this.page.add_action_item("PDF", () => {
		  // 	frappe.set_route('query-report', 'Employee Leave Balance Summary Report');
	  // })
  
	}
	make_form = () => {
	  this.form = new frappe.ui.FieldGroup({
		fields: [
			{

				fieldname: 'from_date',
				label: __('From Date'),
				fieldtype: 'Date',
				default: frappe.datetime.add_days(frappe.datetime.get_today(), -30),
				change: () => this.fetch_and_render()
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
				fieldname:"customer",
				label: __("Customer"),
				fieldtype: "Link",
				options: "Customer",
				change: () => this.fetch_and_render(),
			},
			{
				fieldtype: 'Column Break'
			},
			{

				fieldname: 'territory',
				label: __('Territory'),
				fieldtype: 'Link',
				options: "Territory",
				change: () => this.fetch_and_render()
			},
			{
				fieldtype: 'Column Break'
			},
			{

				fieldname: 'status',
				label: __('Status'),
				fieldtype: 'Link',
				options: "Workflow State",
				"get_query": () => {
					return {
						filters: {
							"name": ["in" , ["Pending for Ops Team","Pending for Customer","Approved","Rejected by Customer","Rejected by Ops Team","Cancelled"]]
						}
					}
				},
				change: () => this.fetch_and_render()
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
	  this.fetch_and_render()
	}
	fetch_and_render = (refresh=false) => {
	  	let filters= this.form.get_values();


    let data = window.location.search;
    if (!filters.status){
		if (data) {
			function getParameterValue(url, parameterName) {
				const urlParams = new URLSearchParams(url);
				return urlParams.get(parameterName);
			}
			let workflowStateValue = getParameterValue(data, 'workflow_state');
			let decodedValue = decodeURIComponent(workflowStateValue);
			filters['status'] = decodedValue
			$('[data-fieldname="status"]').val(decodedValue)
			window.history.replaceState({}, document.title, window.location.pathname);

		}
    }



	  // to prevent the duplicate call
	  if (refresh === false && JSON.stringify(this.filters) === JSON.stringify(filters)){
		return;
	  }
	  this.filters = this.form.get_values();

	  if (!filters.from_date) {
		this.form.get_field('preview').html('');
		return;
	  }
  
	  this.form.get_field('preview').html(`
			  <div class="text-muted margin-top">
				  ${__("Fetching...")}
			  </div>
		  `);
	  frappe.call('field_force.field_force.page.requisition_report.requisition_report.execute', {
		filters: filters,
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
	  let scrollable_view = this.form.get_values()['scrollable_view']
  
	  this.form.get_field('preview').html(
		`<div>
				<table class="table table-bordered" id="export_excel">
					${table_header}${table_body}
				</table>
			</div>
		`);
	  
	}
	table_header = (headers) => {
	  let table_header = `<thead><tr>`;
  
	  headers.forEach(function (field, index) {
		table_header += `<th scope="col" style="width:${field.width}px !important;">${field.label || ''}</th>`;
	  })
  
	  table_header += `</tr>`;
	  return table_header;
	}
  
	table_body = (diff, fields) => {
	  var html = `<tbody>`;
	  var serial_number = 1;
  
	  diff.forEach(function (data, index) {
		html += `<tr>`;
  
		fields.forEach(function (field, indx) {
		  if (field.fieldname === 'sl') {
			data['sl'] = index + 1;
			html += get_absolute_format_and_html(field, data);
		  } else if (field.editable) {
			html += `<td id="${data.docname}_${field.fieldname}" class="editable-field parent-container"
					  data-fieldname="${field.fieldname}" data-name="${data.docname}">${data[field.fieldname] || ''}</td>`
		  }
		  else {
			html += get_absolute_format_and_html(field, data);
		  }
		})
  
		html += `</tr>`;
		serial_number = serial_number + 1;
	  })
  
	  html += `</tbody>`;
	  return html
	}
  
	export_excel = () => {
	  let filters= this.form.get_values();
	  let url = `/api/method/field_force.field_force.page.requisition_report.requisition_report.export_file`;
  
	  if (filters){
		url += `?`;
  
		for (const field in filters) {
		  url += `${field}=${filters[field]}&`;
		}
	  }
	  window.open(url, '_blank');
	}
  }
  
//   amjad kalir bazar life general hospital
  function play_action(action) {
	frappe.xcall("field_force.field_force.page.requisition_report.requisition_report.play_action",
		{action: action}
	  ).then((response) => {
		let statusFieldID = response.docname + '_status';
		document.getElementById(response.docname).innerHTML = response.action;
		document.getElementById(statusFieldID).innerHTML = response.status;
	  });
  }
  
  function get_absolute_format_and_html(field, data, width = 50) {
	let docname = data.docname;
	let value = data[field.fieldname];
  
	if (field.fieldtype === "Image") {
	  return get_image_html(value);
	} else if (field.fieldtype === "Currency") {
	  return get_currency_format(value);
	} else if (field.fieldtype === "Data") {
	  return `<td id="${docname}_${field.fieldname}">${value || ''}</td>`;
	} else {
	  return `<td id="${docname}_${field.fieldname}">${value || ''}</td>`;
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
  
  function set_background_color(){
	let current_theme = document.documentElement.getAttribute("data-theme")
	if (current_theme === 'light'){
		$('.page-body').css('background', '#FFFFFF');
	} else{
		$('.page-body').css('background', 'black');
	}
  }
  function dateFormat(input_D, format_D) {
    const date = new Date(input_D);
    const day = date.getDate();
    const month = date.getMonth() + 1;
    const year = date.getFullYear();
    format_D = format_D.replace("MM", month.toString().padStart(2,"0"));
    if (format_D.indexOf("yyyy") > -1) {
        format_D = format_D.replace("yyyy", year.toString());
    } else if (format_D.indexOf("yy") > -1) {
        format_D = format_D.replace("yy", year.toString().substr(2,2));
    }
    format_D = format_D.replace("dd", day.toString().padStart(2,"0"));
    return format_D;
}
  