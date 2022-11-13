import datetime

import frappe
from field_force.response import build_custom_response
import calendar

@frappe.whitelist()
def get_dashboard_data():
    today_date = datetime.datetime.today()
    current_month, current_year = today_date.month, frappe.defaults.get_user_default('fiscal_year')
    current_month_name = calendar.month_name[current_month]

    sales_target = get_sales_target(current_month_name, current_year)
    daily_sales = get_daily_sales(today_date.date())
    daily_customer = get_daily_customers(today_date.date())

    print(daily_customer)

    dashboard_data = {
        "month": current_month,
        "year": current_year,
        "monthly_target": sales_target.target_amount if sales_target else 0,
        "monthly_sales": sales_target.achievement_amount if sales_target else 0,
        "daily_sales": daily_sales.total if daily_sales else 0,
        "daily_customers": daily_customer.total if daily_customer else 0,
        "monthly_customer": 0,
    }

    frappe.local.response.total_items = 0
    frappe.local.response.data = dashboard_data
    return build_custom_response(response_type='custom')

def get_sales_target(month, year):
    filters = {
        "user": frappe.session.user,
        "month": month,
        "year": year
    }

    if frappe.db.exists("Sales Person Target", filters):
        sales_target = frappe.get_doc("Sales Person Target", filters)
        return sales_target

    return None

def get_daily_sales(date):
    daily_sales = frappe.db.sql("""select name, sum(grand_total) as total from `tabSales Order` where user='%s'
                                and transaction_date='%s' group by user""" % (frappe.session.user, date), as_dict=1)

    if daily_sales:
        return daily_sales[0]

    return 0

def get_daily_customers(date):
    daily_customer = frappe.db.sql("""select count(distinct customer) as total from `tabSales Order`
                                where user='%s' and transaction_date='%s' group by 
                                user""" % (frappe.session.user, date), as_dict=1)

    if daily_customer:
        return daily_customer[0]
    return None