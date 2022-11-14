import datetime

import frappe
from field_force.response import build_custom_response
import calendar

@frappe.whitelist()
def get_dashboard_data():
    today = datetime.datetime.today()
    today_date = today.date()
    month_start_date = today.replace(day=1)

    current_month, current_year = today.month, frappe.defaults.get_user_default('fiscal_year')
    current_month_name = calendar.month_name[current_month]

    sales_target = get_sales_target(current_month_name, current_year,  month_start_date, today_date)
    daily_sales = get_daily_sales(today_date)
    daily_customers = get_daily_customers(today_date)
    monthly_customers = get_monthly_customers(month_start_date, today_date)

    dashboard_data = {
        "month": current_month_name,
        "year": current_year,
        "daily_sold_items": get_daily_sold_items(today_date),
        "daily_sales": daily_sales.total if daily_sales else 0,
        "daily_customers": daily_customers.total if daily_customers else 0,
        "monthly_target": sales_target.target_amount if sales_target else 0,
        # "monthly_sales": sales_target.achievement_amount if sales_target else 0,
        "monthly_sales": get_monthly_sales(month_start_date, today_date),
        "monthly_customers": monthly_customers.total if monthly_customers else 0,
        "announcements": get_announcements(today_date)
    }

    frappe.local.response.total_items = 0
    frappe.local.response.data = dashboard_data
    return build_custom_response(response_type='custom')

def get_sales_target(month, year, month_start_date, today_date):
    filters = {
        "user": frappe.session.user,
        "month": month,
        "year": year
    }

    if frappe.db.exists("Sales Person Target", filters):
        sales_target = frappe.get_doc("Sales Person Target", filters)

        # if not sales_target.achievement_amount:
        #     sales_target.achievement_amount = get_monthly_sales(month_start_date, today_date)
        #     sales_target.save()

        return sales_target

    return None

def get_daily_sales(date):
    daily_sales = frappe.db.sql("""select name, sum(grand_total) as total from `tabSales Order` where user='%s'
                                 and docstatus!=2 and transaction_date='%s' group by user""" % (frappe.session.user,
                                                                                                date), as_dict=1)

    if daily_sales:
        return daily_sales[0]
    return 0

def get_monthly_sales(month_start_date, today_date):
    monthly_sales = frappe.db.sql("""select name, sum(grand_total) as total from `tabSales Order` where user='%s'
                                 and docstatus!=2 and transaction_date between '%s' and '%s' group by user""" %
                                  (frappe.session.user, month_start_date, today_date), as_dict=1)
    if monthly_sales:
        return monthly_sales[0].total
    return 0

def get_daily_customers(date):
    daily_customers = frappe.db.sql("""select count(distinct customer) as total from `tabSales Order`
                                where user='%s' and docstatus!=2 and transaction_date='%s' group by 
                                user""" % (frappe.session.user, date), as_dict=1)

    if daily_customers:
        return daily_customers[0]
    return None

def get_monthly_customers(month_start_date, today_date):
    monthly_customers = frappe.db.sql("""select count(distinct customer) as total from `tabSales Order`
                                where user='%s' and docstatus!=2 and transaction_date between '%s' and '%s' group by 
                                user""" % (frappe.session.user, month_start_date, today_date), as_dict=1)

    if monthly_customers:
        return monthly_customers[0]
    return None

def get_daily_sold_items(date):
    daily_items = frappe.db.sql("""select sum(total_items) as total from `tabSales Order` where user='%s' and 
                                    docstatus!=2 and transaction_date='%s' group by 
                                   user""" % (frappe.session.user, date), as_dict=1)
    if daily_items:
        return daily_items[0].total
    return 0

def get_announcements(date):
    announcements = frappe.db.sql("""select name, announcement_date, announcement_message from `tabAnnouncement` where
                                    disabled=0 and from_date <= '%s' and to_date >= '%s'  
                                    order by announcement_date desc, creation desc """ % (date, date), as_dict=1)

    return announcements