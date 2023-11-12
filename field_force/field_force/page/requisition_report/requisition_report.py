import frappe
import json
import datetime
from frappe.utils import pretty_date, now, add_to_date

@frappe.whitelist()
def execute(filters=None):
    columns = get_columns()
    data = get_absolute_data(filters)
    return data, columns

def get_absolute_data(filters, export=False):
    query_result = get_query_data(filters)

    for requisition in query_result:
        requisition['action'] = get_appropiate_action_button(requisition)
        requisition['status'] = get_workflow_state_with_color(requisition)
        requisition['date'] = frappe.format(requisition.transaction_date, 'Date')
        requisition['delivery_date'] = frappe.format(requisition.delivery_date, 'Date')
        requisition['expected_delivery_date'] = frappe.format(requisition.expected_delivery_date, 'Date')
        requisition['pretty_date'] = custom_pretty_date(requisition.modified)

        if not export:
            set_link_to_doc(requisition, 'customer', 'customer', color='dodgerblue')
            set_link_to_doc(requisition, 'territory', 'territory', color='teal')
            requisition['print'] = get_pdf_button("Requisition", requisition['name'])

        else:
            requisition['status'] = requisition.workflow_state
    
    # frappe.msgprint(str(query_result))

    return query_result
def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    customer = filters.get('customer')
    status = filters.get('status')
    territory = filters.get('territory')

    conditions = {}

    if from_date and to_date:
        conditions["transaction_date"] = ["between", [from_date, to_date]]
    if customer:
        conditions["customer"] = customer
    if status:
        conditions['workflow_state'] = status
    if territory:
        conditions['territory'] = territory

    # return " and ".join(conditions)
    return conditions

def get_query_data(filters):
    try:
        filters = json.loads(filters)
    except:
        pass

    conditions = get_conditions(filters)


    fields = ['name', 'modified','owner','grand_total','transaction_date', 'customer', 'delivery_date','expected_delivery_date',
              'workflow_state', 'territory']

    query_result = frappe.get_list("Requisition", filters=conditions, fields=fields,
                                  order_by='modified desc', page_length=100)
    return query_result

def get_columns():
    columns =  [
        {'fieldname': 'date', 'label': 'Date',"fieldtype":"Date", 'expwidth': 15, 'width': 100},
        {'fieldname': 'customer', 'label': 'Customer',"fieldtype":"Link","options" : "Customer",'expwidth': 15, 'width': 180},
        {'fieldname': 'territory', 'label': 'Territory', 'expwidth': 13, 'width': 160},
        {'fieldname': 'delivery_date', 'label': 'Req Delivery Date',"fieldtype":"Date", 'expwidth': 13, 'width': 160, 'editable': False},
        {'fieldname': 'expected_delivery_date', 'label': 'Exp Delivery Date',"fieldtype":"Date", 'expwidth': 15, 'width': 140},
        {'fieldname': 'status', 'label': 'Status', 'fieldtype': 'Data', 'expwidth': 15, 'width': 140},
        {'fieldname': 'grand_total', 'label': 'Grand Total', 'fieldtype': 'Currency', 'width':100, 'export': False},
        {'fieldname': 'action', 'label': 'Action', 'fieldtype': 'Button', 'width':100, 'export': False},
        {'fieldname': 'print', 'label': 'Print', 'fieldtype': 'Button', 'width':50, 'export': False},
        {'fieldname': 'pretty_date', 'label': '', 'fieldtype': 'Data', 'width':50, 'export': False},
    ]
    return columns
def get_appropiate_action_button(requisition):
    user_roles = frappe.get_roles(frappe.session.user)
    owner = requisition.get("owner")
    action = ''
    if requisition.get("workflow_state") == "Pending for Ops Team" and "Operation" in user_roles:
        action = f'''<div id="{requisition.get("name")}">
                        <button id="{requisition.get("name")}_Approve" class="btn btn-primary btn-sm" onclick="play_action(this.id)"
                            style="width:80px;">Approve</button><br>
                        <button id="{requisition.get("name")}_Reject" class="btn btn-danger btn-sm" onclick="play_action(this.id)"
                            style="width:80px; margin-top:5px;">Reject</button>
                    </div>
                '''
    elif requisition.get("workflow_state") == "Pending for Customer" and "Customer" in user_roles and frappe.session.user == owner:
        action = f'''<div id="{requisition.get("name")}">
                        <button id="{requisition.get("name")}_Approve" class="btn btn-primary btn-sm" onclick="play_action(this.id)"
                            style="width:80px;">Approve</button><br>
                        <button id="{requisition.get("name")}_Reject" class="btn btn-danger btn-sm" onclick="play_action(this.id)"
                            style="width:80px; margin-top:5px;">Reject</button>
                    </div>
                '''
    elif requisition.workflow_state == "Approved" and \
        frappe.has_permission("Requisition", "cancel", requisition.name):

        action = f'''<div id="{requisition.get("name")}">
                        <button id="{requisition.get("name")}_Cancel" class="btn btn-danger btn-sm" onclick="play_action(this.id)"
                            style="width: 80px;">Cancel</button>
                    </div>
                '''
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
        "Pending for Ops Team" : "blueviolet",
        "Pending for Customer" : "gold",
        "Approved" : "green",
        "Rejected by Customer" : "red",
        "Rejected by Ops Team" : "red",
        "Approved by Ops Team" : "green",
        "Cancelled" : "red"
    }
    return f'''<span style="color:{color.get(requisition.workflow_state)};">{requisition.workflow_state}</span>'''

def get_colors_dict(doctype):
    docs = frappe.get_list(doctype, fields=['name', 'color'])
    doc_colors_dict = {}

    for doc in docs:
        doc_colors_dict[doc.name] = doc.color

    return doc_colors_dict


def set_link_to_doc(doc, field, doc_url='', label=None, color=None):
    style = f'style="color:{color};"' if color else ''

    doc[field] = f'''<a href="/app/{doc_url}/{doc[field]}" target="_blank" %s>
                        {label or doc[field]}
                    </a>
                ''' % style

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