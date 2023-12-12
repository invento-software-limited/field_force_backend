import frappe
import json
import datetime
from frappe import _
from frappe.utils import pretty_date
from field_force.field_force.page.utils import *
from field_force.field_force.page.utils import generate_excel_and_download, get_time_in_12_hour_format

@frappe.whitelist()
def execute(filters=None):
    columns = get_columns()
    data = get_absolute_data(filters)
    return data, columns

def get_absolute_data(filters, export=False):
    query_result = get_query_data(filters)

    for requisition in query_result:
        
        requisition['status'] = get_workflow_state_with_color(requisition)
        requisition['docname'] = requisition['id']
        requisition['ds_docname'] = requisition['ds_id']
        requisition['departure_date'] = frappe.format(requisition.departure_date, 'Date')
        change_color(requisition,"departure_date","#9b00d7")
        change_color(requisition,"contact_person","#00bf46")
        change_color(requisition,"contact_number","#8000cc")
        change_color(requisition,"customer_primary_address","#0600cc")

        if not export:
            user_role = frappe.get_roles(frappe.session.user)
            if "Customer" in user_role and "System Manager" not in user_role:
                change_color(requisition,"id","blue")
            else:
                set_link_to_doc(requisition, 'id','delivery-trip',val=requisition.id, color='blue')
                
            set_link_to_doc(requisition, 'requisition','requisition',val=requisition.requisition, color='#00918a')
            set_link_to_doc(requisition, 'customer','customer',val=requisition.customer, color='#0080ff')
            set_link_to_doc(requisition, 'territory','territory',val=requisition.territory, color='#0080ff	')
            set_link_to_doc(requisition, 'driver_name','driver',val=requisition.driver, color='#0080ff	')
            if requisition.get("vehicle"):
                vehicle = frappe.get_doc("Vehicle", requisition.get("vehicle"))
                labels = vehicle.name +","+ vehicle.model
                set_link_to_doc(requisition, 'vehicle','vehicle',val=vehicle.name,label=labels,color='#00918a')

        else:
            requisition['status'] = requisition.status

    return query_result

def get_conditions(filters):
    if not filters: filters = {}
    conditions = ''

    if filters.get("from_date"):
        conditions += ' and date(dt.departure_time) >= "{}"'.format(filters.get("from_date"))
    if filters.get("to_date"):
        conditions += ' and date(dt.departure_time) <= "{}"'.format(filters.get("to_date"))
    if filters.get("customer"):
        conditions += ' and ds.customer = "{}"'.format(filters.get("customer"))
    if filters.get("territory"):
        conditions += ' and dt.territory = "{}"'.format(filters.get("territory"))
    if filters.get("driver"):
        conditions += ' and dt.driver = "{}"'.format(filters.get("driver"))
    if filters.get("status"):
        conditions += ' and ds.status = "{}"'.format(filters.get("status"))
    if filters.get("vehicle"):
        conditions += ' and dt.vehicle = "{}"'.format(filters.get("vehicle"))
    if filters.get("requisition"):
        conditions += ' and ds.requisition = "{}"'.format(filters.get("requisition"))
    
    user_roles = frappe.get_roles(frappe.session.user)
    if "Customer" in user_roles and "System Manager" not in user_roles:
        conditions += ' and req.owner = "{}"'.format(frappe.session.user)
    return conditions


def get_query_data(filters):
    try:
        filters = json.loads(filters)
    except:
        pass

    conditions = get_conditions(filters)


    customers = frappe.get_list("Customer", filters={"disabled": 0}, pluck='name')
    customers_in_tuple_str = '("' + '", "'.join(customers) + '")'

    query = frappe.db.sql('''select dt.name as id, dt.driver_name, dt.driver, dt.territory, ds.requisition,
                        date(dt.departure_time) as departure_date, dt.vehicle, time(dt.departure_time) as departure_time,ds.requisition,
                         ds.status, ds.customer, ds.contact_person,ds.contact_number, ds.customer_primary_address, ds.total_qty,ds.name as ds_id
                        from `tabDelivery Stop` as ds left join `tabDelivery Trip` as dt on dt.name = ds.parent
                        left join `tabRequisition` as req on ds.requisition = req.name
                        where dt.name is not null and ds.customer in {} {}
                        order by departure_time desc'''.format(customers_in_tuple_str, conditions),as_dict=1)
    
    return query

def get_columns():
    columns =  [
        {'fieldname': 'check', 'label': '',"fieldtype":"Check", 'expwidth': 5, 'width': 20},
        {"label": _("ID"), "fieldtype": "Data", "fieldname": "id", "options": "Customer", "width": 120},
        {"label": _("Requisition"), "fieldtype": "Data", "fieldname": "requisition", "width": 120},
        {"label": _("Customer"), "fieldtype": "Data", "fieldname": "customer", "options": "Customer", "width": 180},
        {"label": _("Dep. Date"),"fieldtype": "Data","fieldname": "departure_date","width": 100},
        {"label": _("Territory"),"fieldtype": "Data","fieldname": "territory","options":"Territory","width": 120},
        {"label": _("Status"), "fieldtype": "Data","fieldname": "status", "width": 80},
        {"label": _("Vehicle"),"fieldtype": "Data","fieldname": "vehicle","width": 120},
        {"label": _("Driver Name"), "fieldtype": "Data", "fieldname": "driver_name", "width": 120},
        {"label": _("Address"),"fieldtype": "Data","fieldname":"customer_primary_address","width": 200},
        {"label": _("Contact Person"), "fieldtype": "Data", "fieldname": "contact_person", "width": 80},
        {"label": _("Contact Number"), "fieldtype": "Data", "fieldname": "contact_number", "width": 80},
        {"label": _("QTY"), "fieldtype": "Float", "fieldname": "total_qty", "width": 80},
    ]
    return columns
def get_appropiate_action_button(requisition):
    action = f'''<a href="/app/requisition/{requisition.get("name")} "id="{requisition.get("name")}_Approve" target="_blank" class="btn btn-success btn-sm"
                            style="width:50px;">View</a><br>'''
    return action

@frappe.whitelist()
def play_action(action):
    if action:
        requisition_name, action = tuple(action.split('_'))
        requisition = frappe.get_doc("Requisition", requisition_name)

        if requisition.workflow_state == 'Pending for Ops Team':
            if action == "Approve":
                requisition.workflow_state = 'Pending for Customer'
            else:
                requisition.workflow_state = 'Rejected by Ops Team'

        elif requisition.workflow_state == 'Pending for Customer':
            if action == "Approve":
                requisition.workflow_state = 'Approved'
            else:
                requisition.workflow_state = 'Rejected by Customer'


        elif requisition.workflow_state == 'Approved' and \
            frappe.has_permission("Requisition", "cancel", requisition.name) and action == 'Cancel':
            frappe.db.set_value("Requisition", requisition.name, 'workflow_state', 'Cancelled')
            frappe.db.set_value("Requisition", requisition.name, 'status', 'Cancelled')
            frappe.db.commit()

            requisition = frappe.get_doc("Requisition", requisition_name)
            requisition.cancel()

            return {
                'docname': requisition_name,
                'status': get_workflow_state_with_color(requisition),
                'action': ''
            }

        requisition.save()

        if requisition.workflow_state == "Approver" and requisition.docstatus == 0:
            requisition.submit()

        return {
            'docname': requisition_name,
            'status': get_workflow_state_with_color(requisition),
            'action': get_appropiate_action_button(requisition)
        }

def get_workflow_state_with_color(requisition):
    color = {
        "Scheduled" : "#ff5407",
        "In Transit" : "#005cef",
        "Completed" : "green",
        "Cancelled" : "red",
        "Draft" : "red"
    }
    return f'''<span style="color:{color.get(requisition.status)};">{requisition.status}</span>'''

def get_colors_dict(doctype):
    docs = frappe.get_list(doctype, fields=['name', 'color'])
    doc_colors_dict = {}

    for doc in docs:
        doc_colors_dict[doc.name] = doc.color

    return doc_colors_dict


def set_link_to_doc(doc, field, doc_url='',val=None, label=None, color=None):
    style = f'style="color:{color};"' if color else ''
    if val:
        doc[field] = f'''<a href="/app/{doc_url}/{val}" target="_blank" %s>
                        {label or doc[field]}
                    </a>
                ''' % style
    else:
        doc[field] = ''
    return doc[field]

def get_pdf_button(doctype, docname, label='', color=None):
    style = f'style="color:{color};"' if color else ''

    return f'''<a class="btn btn-sm" href="/app/print/{doctype}/{docname}" target="_blank" %s>
                        <svg class="icon  icon-sm" style="">
                            <use class="" href="#icon-printer"></use>
                        </svg>
                    </a>
            ''' % style

def custom_pretty_date(date):
    try:
        if isinstance(date, str):
            if '.' in date:
                date = date.split('.')[0]

            date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

        pretty_date_ = pretty_date(date)

        if pretty_date_:
            pretty_date_ = pretty_date_.split(' ')

            if pretty_date_[1][0:2] == "mo":
                pretty_date_ = f"{pretty_date_[0]}M"

            pretty_date_ = f"{pretty_date_[0]}{pretty_date_[1][0]}"
            return pretty_date_
    except:
        return ""

@frappe.whitelist()
def export_file(**filters):
    columns = get_columns()
    data = get_export_data(filters)
    file_name = 'Requisition_Report.xlsx'
    generate_excel_and_download(columns, data, file_name, height=30)

def get_export_data(filters):
    query_result = get_absolute_data(filters, export=True)
    return query_result

@frappe.whitelist()
def update_field(**kwargs):
    docname = kwargs.get('docname')
    fieldname = kwargs.get('fieldname')
    value = kwargs.get('value')
    leave_application = frappe.get_doc("Merchandising Picture", docname)

    if leave_application.get(fieldname) != value:
        leave_application.update({fieldname:value})
        leave_application.save()

    return True

def change_color(doc, field, color):
    style = f'style="color:{color};"' if color else ''

    doc[field] = f'''<span %s>{doc[field] or "" }</span>''' % style

    return doc[field]

@frappe.whitelist()
def update_delivery_stop_status(trips,value):
    if trips and value:
        try:
            trips = json.loads(trips)
            value = json.loads(value)
        except:
            pass

        for trip in trips:
            trip_split = trip.split("&")
            trip_doc = frappe.get_doc("Delivery Trip",trip_split[0])
            if trip_doc.delivery_stops:
                for stop in trip_doc.delivery_stops:
                    if stop.get("name") == trip_split[1]:
                        stop.status = value.get("status")
            trip_doc.save()