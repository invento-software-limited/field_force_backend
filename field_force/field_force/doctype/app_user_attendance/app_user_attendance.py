# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt
import datetime

import frappe

from field_force.field_force.doctype.utils import set_cheat_status, set_location_to_map
from field_force.field_force.page.utils import get_time_in_12_hour_format
from frappe.core.doctype.communication.email import make
from frappe.model.document import Document


class AppUserAttendance(Document):
    def validate(self):
    # 	if frappe.session.user != 'administrator':
    # 		self.user = frappe.session.user

        if not self.email or not self.user_fullname:
            email, user_fullname = frappe.db.get_value('User', self.user, ['email', 'full_name'])

            if not self.email and email:
                self.email = email
            if not self.user_fullname and user_fullname:
                self.user_fullname = user_fullname

        # if not self.company:
        # 	self.company = frappe.defaults.get_user_defaults('Company')

        self.set_sales_person()
        self.set_employee()
        set_cheat_status(self)

    def before_save(self):
        set_location_to_map(self)

    def set_sales_person(self):
        if self.user and not self.sales_person and frappe.db.exists("Sales Person", {"user": self.user}):
            self.sales_person = frappe.db.get_value("Sales Person", {"user": self.user}, "name")

    def set_employee(self):
        if self.owner and not self.employee:
            if frappe.db.exists("Employee", {"user_id": self.owner}):
                employee, employee_name = frappe.db.get_value("Employee", {"user_id": self.owner},
                                                              ['name', 'employee_name'])
                self.employee = employee
                self.employee_name = employee_name

@frappe.whitelist()
def send_daily_attendance_mail():
    hr_settings = frappe.get_doc("HR Settings", "HR Settings")

    if not hr_settings.send_daily_attendance_report:
        return

    date = frappe.utils.today()
    time = "10:30:00"

    sales_person_groups, sales_persons_attendance = get_attendance_data(date, time)
    template = frappe.get_doc("Email Template", hr_settings.email_template)
    recipients = hr_settings.email_recipients.split('\n')

    context = {
        'date': datetime.datetime.strptime(str(date),  "%Y-%m-%d").strftime('%d %b, %Y'),
        'time': get_time_in_12_hour_format(time),
        'sales_person_groups': sales_person_groups,
        'sales_persons_attendance': sales_persons_attendance,
        'generated_at': get_time_in_12_hour_format(str(frappe.utils.nowtime()).split('.')[0])
    }

    subject = frappe.render_template(template.subject, context)
    message = frappe.render_template(template.response_html, context)

    frappe.sendmail(
        recipients= recipients,
        sender='fieldforce@best-inbrands.com',
        subject=subject,
        content=message,
    )
    frappe.db.commit()

def get_attendance_data(date, time):
    filters = {
        'server_date': date,
        'server_time': ['<=', time]
    }
    fields =  ['name', 'sales_person', 'server_date', 'server_time']
    sales_persons_fields = ['name', 'sales_person_group', 'type']
    sales_persons_filters = {
        'sales_person_group': ['in', ['GT', 'MT']],
        'enabled': 1
    }

    sales_persons = frappe.get_list("Sales Person", sales_persons_filters, sales_persons_fields, order_by='sales_person_group')
    sales_persons_attendance = frappe.get_list("App User Attendance", filters, fields,
                                               order_by='server_time', limit_page_length=1000)

    attendance_dict = {}

    sales_person_groups = {
        "GT": {
            "sales_person_group": "GT",
            "total_sales_person": 0,
            "total_present": 0,
            "total_absent": 0
        },
        "MT": {
            "sales_person_group": "MT",
            "total_sales_person": 0,
            "total_present": 0,
            "total_absent": 0
        },
        "Grand Total": {
            "sales_person_group": "Grand Total",
            "total_sales_person": 0,
            "total_present": 0,
            "total_absent": 0
        }
    }

    for attendance in sales_persons_attendance:
        if attendance.sales_person not in attendance_dict.keys():
            attendance.server_time = get_time_in_12_hour_format(attendance.server_time)
            attendance['status'] = 'Yes'
            attendance_dict[attendance.sales_person] = attendance

    for sales_person in sales_persons:
        sales_person_groups['Grand Total']['total_sales_person'] += 1
        sales_person_groups[sales_person.sales_person_group]['total_sales_person'] += 1

        if sales_person.name in attendance_dict.keys():
            sales_person.update(attendance_dict[sales_person.name])
            sales_person_groups[sales_person.sales_person_group]['total_present'] += 1
            sales_person_groups['Grand Total']['total_present'] += 1
        else:
            sales_person['server_time'] = 'No'
            sales_person['status'] = 'No'
            sales_person['sales_person'] = sales_person.name
            # attendance_dict[sales_person.name] = sales_person
            sales_person_groups[sales_person.sales_person_group]['total_absent'] += 1
            sales_person_groups['Grand Total']['total_absent'] += 1

    return sales_person_groups.values(), sales_persons
