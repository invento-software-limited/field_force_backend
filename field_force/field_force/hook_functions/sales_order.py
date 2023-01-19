import frappe
import calendar
import datetime

def after_insert(self, method):
    if self.created_from_app:
        self.submit()

@frappe.whitelist()
def set_extra_values(self, method):
    self.total_items = len(self.items)

    for item in self.items:
        if not item.brand or not item.image:
            item.brand, item.image = frappe.db.get_value('Item', item.item_code, ['brand', 'image'])

@frappe.whitelist()
def add_sales_person(self, method):
    if not self.sales_person and frappe.db.exists("Sales Person", {"user": self.owner}):
        self.sales_person, self.employee, self.user = frappe.db.get_value("Sales Person", {'user': self.owner},
                                                               ['name', 'employee', 'user'])
    if not self.sales_team and self.sales_person:
        self.append("sales_team", {
            "parent": self.name,
            "parenttype": "Sales Order",
            "sales_person": self.sales_person,
            "allocated_percentage": 100,
            "allocated_amount": self.grand_total,
            "employee": self.employee,
            "user": self.user
        })

    if not self.user:
        self.user = self.owner

    # add_amount_to_achievement(self, method)

def add_amount_to_achievement(self, method):
    # print("======>>", method)
    month, year = get_month_and_year(self)
    achievement_amount = get_default(self.grand_total) - get_default(self.achievement_amount)
    set_amount_to_sales_target(self.sales_person, achievement_amount, month, year)

    if self.achievement_amount or self.achievement_amount == 0:
        self.achievement_amount += achievement_amount
    else:
        self.achievement_amount = achievement_amount

def subtract_achievement_amount(self, method):
    month, year = get_month_and_year(self)
    achievement_amount = -self.achievement_amount
    set_amount_to_sales_target(self.sales_person, achievement_amount, month, year)

def set_amount_to_sales_target(sales_person, achievement_amount, month, year):
    filters = {
        "sales_person": sales_person,
        "month": calendar.month_name[month],
        "year": year
    }
    if frappe.db.exists("Sales Person Target", filters):
        sales_target = frappe.get_doc("Sales Person Target", filters)
        sales_target.achievement_amount += achievement_amount
        sales_target.save()

def get_default(value):
    if value:
        return value
    return 0

def get_month_and_year(sales_order):
    year = frappe.defaults.get_user_default('fiscal_year')

    if isinstance(sales_order.transaction_date, datetime.date):
        return sales_order.transaction_date.month, year
    elif isinstance(sales_order.transaction_date, str):
        month =  datetime.datetime.strptime(sales_order.transaction_date, "%Y-%m-%d").month
        return month, year
    return None, None