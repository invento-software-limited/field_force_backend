import datetime

import frappe
from field_force.response import build_custom_response
from field_force.auth import get_allowed_doctypes
import calendar

@frappe.whitelist()
def get_dashboard_data():
    today = datetime.datetime.today()
    today_date = today.date()
    month_start_date = today.replace(day=1)

    current_month, current_year = today.month, frappe.defaults.get_user_default('fiscal_year')
    current_month_name = calendar.month_name[current_month]

    sales_person_names = get_sales_person_names(frappe.session.user)
    sales_target = get_sales_target(sales_person_names, current_month_name, current_year,  month_start_date, today_date)
    monthly_sales = get_monthly_sales(sales_person_names, month_start_date, today_date)

    dashboard_data = {
        "month": current_month_name,
        "year": current_year,
        "daily_sold_items": get_daily_sold_items(sales_person_names, today_date) or 0,
        "daily_sales": get_daily_sales(sales_person_names, today_date) or 0,
        "daily_customers": get_daily_customers(sales_person_names, today_date) or 0,
        "monthly_target": sales_target or 0,
        "monthly_sales": monthly_sales or 0,
        # "monthly_sales": sales_target.achievement_amount if sales_target else 0,
        "progress_percentage": get_progress_percentage(sales_target, monthly_sales),
        "monthly_customers": get_monthly_customers(sales_person_names, month_start_date, today_date) or 0,
        "announcements": get_announcements(today_date),
        "allowed_doctypes": get_allowed_doctypes(frappe.session.user)
    }

    frappe.local.response.total_items = 0
    frappe.local.response.data = dashboard_data
    return build_custom_response(response_type='custom')

def get_sales_person_names(user):
    sales_person = frappe.get_list("Sales Person", {"user": user}, ['name', 'type'])

    if sales_person:
        sales_person = sales_person[0]

        if sales_person.type == "Supervisor":
            sales_persons = frappe.db.get_list("Sales Person", {"parent_sales_person": sales_person.name}, 'name')
            sales_person_names = (f"'{sales_person.name}'" for sales_person in sales_persons)
            return "(" + ", ".join(sales_person_names) + ")"
        else:
            return f"('{sales_person.name}')"

    return None


def get_sales_target(sales_person_names, month, year, month_start_date, today_date):
    if not sales_person_names:
        return 0

    sales_target = frappe.db.sql("""select SUM(IFNULL(target_amount, 0)) as target_amount from
                                    `tabSales Person Target` where docstatus=1 and sales_person in %s and month='%s'
                                    and year='%s'""" % (sales_person_names, month, year), as_dict=1)
    if sales_target:
        return sales_target[0].target_amount
    return 0

def get_daily_sales(sales_person_names, date):
    daily_sales = frappe.db.sql("""select sum(IFNULL(grand_total, 0)) as total from `tabRequisition` where docstatus=1 
                            and sales_person in %s and transaction_date='%s'""" % (sales_person_names, date), as_dict=1)
    if daily_sales:
        return daily_sales[0].total
    return 0

def get_monthly_sales(sales_person_names, month_start_date, today_date):
    monthly_sales = frappe.db.sql("""select sum(IFNULL(grand_total, 0)) as total from `tabRequisition` where sales_person in %s
                                 and docstatus=1 and transaction_date between '%s' and '%s'""" %
                                  (sales_person_names, month_start_date, today_date), as_dict=1)
    if monthly_sales:
        return monthly_sales[0].total
    return 0

def get_daily_customers(sales_person_names, date):
    daily_customers = frappe.db.sql("""select distinct count(IFNULL(customer, 0)) as total_customer from `tabRequisition`
                                where sales_person in %s and docstatus=1 and transaction_date='%s'""" % (sales_person_names, date), as_dict=1)
    if daily_customers:
        return daily_customers[0].total_customer
    return 0

def get_monthly_customers(sales_person_names, month_start_date, today_date):
    monthly_customers = frappe.db.sql("""select distinct count(IFNULL(customer, 0)) as total_customer from `tabRequisition` where 
                                sales_person in %s and docstatus=1 and transaction_date between '%s' and '%s'"""
                                % (sales_person_names, month_start_date, today_date), as_dict=1)
    if monthly_customers:
        return monthly_customers[0].total_customer
    return 0

def get_daily_sold_items(sales_person_names, date):
    daily_items = frappe.db.sql("""select sum(IFNULL(total_items, 0)) as total from `tabRequisition` where sales_person in %s
                                and docstatus=1 and transaction_date='%s'""" % (sales_person_names, date), as_dict=1)
    if daily_items:
        return daily_items[0].total
    return 0

def get_announcements(date):
    announcements = frappe.db.sql("""select name, announcement_date, announcement_message from `tabAnnouncement` where
                                    disabled=0 and from_date <= '%s' and to_date >= '%s' order by 
                                    announcement_date desc, creation desc """ % (date, date), as_dict=1)
    return announcements

def get_progress_percentage(monthly_target, monthly_sales):
    if  monthly_target and monthly_sales:
        return float("{:.2f}".format((monthly_sales / monthly_target) * 100))

    return 0