# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from field_force.field_force.doctype.sales_target.sales_target import get_sales_persons
from frappe import _
import datetime, calendar

def execute(filters=None):
    columns = get_columns(filters)
    conditions = get_conditions(filters)

    month_number = datetime.datetime.strptime(filters.get('from_date'), '%Y-%m-%d').month
    month = calendar.month_name[month_number]
    year = frappe.defaults.get_user_default("fiscal_year")

    all_child = False if filters.get('type') == 'Self Child' else True

    if frappe.db.exists('Sales Person', {'user': frappe.session.user}):
        sales_person_ = frappe.get_doc('Sales Person', {'user': frappe.session.user})
        sales_persons = get_sales_persons(sales_person_.name, False)

        data = []

        for sales_person in sales_persons:
            data_ = get_data(conditions, sales_person.sales_person, month, year)
            print(data_)
            data.append(data_[0])

        return columns, data
    else:
        frappe.msgprint("There is no sales person")

    # data = get_data(filters, sales_person_names)

    return columns, []


def get_columns(filters):
    """ Columns of Report Table"""

    columns = [
        {"label": _("Sales Person"), "fieldname": "sales_person",  "fieldtype": "Link",
		 			"options":"Sales Person", "width": 200},
        {"label": _("Target Amount"), "fieldname": "target_amount", "fieldtype": "Currency", "width": 200},
        {"label": _("Achievement Amount"), "fieldname": "achievement_amount", "fieldtype": "Currency", "width": 200},
        {"label": _("Achievement(%)"), "fieldname": "achievement_percentage", "fieldtype": "Float", "precision":2, "width": 200},
	]

    return columns

def get_data(conditions, sales_person, month, year):
    print("===>>", sales_person)
    conditions = add_sales_person_to_condition(conditions, sales_person, all_child=True, including_self=True)

    print(conditions)

    sales_order_query = """select sum(sales_order.grand_total) as achievement_amount, sales_order.sales_person, 
                    sales_order.customer from `tabSales Order` sales_order where %s group by sales_order.sales_person
                    order by achievement_amount desc""" % conditions

    sales_target_query = """select sum(sales.achievement_amount) as achievement_amount, sales.sales_person,
                            sum(sales_target.target_amount) as target_amount,
                            (CASE WHEN sum(sales_target.target_amount) is not null 
                                   THEN 100/(sum(sales_target.target_amount)/sum(sales.achievement_amount))
                                   ELSE 0
                            END) as achievement_percentage from (%s) sales left join `tabSales Person Target` 
                            sales_target on sales_target.sales_person=sales.sales_person where sales_target.month='%s'
                            and sales_target.year='%s'""" % (sales_order_query, month, year)

    query_result = frappe.db.sql(sales_target_query, as_dict=1, debug=0)
    return query_result


def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    sales_person = filters.get('sales_person')
    # user = filters.get('user')
    # customer = filters.get('customer')

    conditions = []

    if from_date:
        conditions.append("sales_order.transaction_date >= '%s'" % from_date)
    if to_date:
        conditions.append("sales_order.transaction_date <= '%s'" % to_date)
    if sales_person:
        conditions.append("sales_order.sales_person = '%s'" % sales_person)

    # if user:
    #     conditions.append("sales_order.user = '%s'" % user)
    # if customer:
    #     conditions.append("sales_order.customer = '%s'" % customer)

    return " and ".join(conditions)

def add_sales_person_to_condition(conditions, sales_person, all_child=False, including_self=False):
    sales_person_names = get_sales_persons_list(sales_person, all_child, including_self, as_tuple_str=True)
    print(sales_person_names)

    if sales_person_names:
        conditions += ' and sales_order.sales_person in ' + sales_person_names

    return conditions


def get_sales_persons_list(sales_person, all_child=False, including_self=False, as_tuple_str=False):
        sales_persons = get_sales_persons(sales_person, all_child)
        # sales_persons_tree = get_sales_persons(reporting_person.name, all_child, as_tree=True)

        if as_tuple_str and sales_persons:
            sales_person_names = [f"'{sales_person_.sales_person}'" for sales_person_ in sales_persons]

            if including_self:
                sales_person_names.append(f"'{sales_person}'")

            sales_person_names = "(" + ", ".join(sales_person_names) + ")"
            return sales_person_names
        else:
            return sales_persons