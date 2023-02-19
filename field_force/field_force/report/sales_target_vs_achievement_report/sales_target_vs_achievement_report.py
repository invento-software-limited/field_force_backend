# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
from field_force.field_force.doctype.sales_target.sales_target import get_sales_persons
from frappe import _
import datetime, calendar
# import pandas as pd


def get_currency_symbol():
    frappe.defaults.get_user_default('Currency')
    return frappe.db.get_value("Currency", "BDT", "symbol", cache=True)

def execute(filters=None):
    global currency_symbol
    currency_symbol = get_currency_symbol()

    columns = get_columns(filters)
    conditions = get_conditions(filters)

    month = filters.get('month')
    year = filters.get("year")
    sales_person = get_current_sales_person(filters)
    data = []

    if sales_person:
        if sales_person.type in ['Channel Manager', 'Manager', None] and filters.get('type') == 'By Supervisor':
            sales_persons = get_sales_persons(sales_person.name, type='Supervisor')

            for sales_person_ in sales_persons:
                if sales_person_.type == 'Supervisor' and sales_person_.is_group:
                    conditions_, sales_person_names  = add_sales_person_to_condition(conditions, sales_person_,
                                                                                     all_child=True)
                    if sales_person_names and conditions_:
                        data_ = get_data(conditions_, month, year, sales_person_names)

                        if data_:
                            row = make_sum_and_push_to_data_list(data, data_, sales_person_, is_group=True)
                            make_bold(row)

        elif sales_person.type in ['Channel Manager', None] and filters.get('type') == 'By Manager':
            sales_persons = get_sales_persons(sales_person.name, all_child=True, type='Manager')

            for sales_person_ in sales_persons:
                if sales_person_.type == 'Manager' and sales_person_.is_group:
                    get_data_by_supervisor(conditions, data, sales_person_.sales_person, month, year, all_child=True)

        elif sales_person and filters.get('type') == 'Individual':
            conditions_, sales_person_names = add_sales_person_to_condition(conditions, sales_person, all_child=True)
            data = get_data(conditions_, month, year, sales_person_names)

            for row in data:
                set_format(row, average_percentage=False)

    return columns, data

def get_data_by_supervisor(conditions, data,  sales_person_name, month, year, all_child=True,
                           type=None, including_self=False):
    sales_persons = get_sales_persons(sales_person_name, all_child=True, type=type)
    total_row = {
        "sales_person": sales_person_name,
        "target_amount": 0,
        "achievement_amount": 0,
        "achievement_percentages": [],
        "achievement_percentage": 0
    }
    data.append(total_row)

    for sales_person_ in sales_persons:
        if sales_person_.type == 'Supervisor' and sales_person_.is_group:
            conditions_, sales_person_names = add_sales_person_to_condition(conditions, sales_person_,
                                                                            including_self=True, all_child=all_child)
            if conditions_:
                data_ = get_data(conditions_, month, year, sales_person_names)

                if data_:
                    sub_row = make_sum_and_push_to_data_list([], data_, sales_person_)
                    calculate_sum(total_row, sub_row)
                    data.append(sub_row)

    if total_row['achievement_percentages']:
        set_format(total_row)
        make_bold(total_row)

    return total_row

def make_sum_and_push_to_data_list(data, data_, sales_person_, is_group=False):
    average_amount_row = {
        "sales_person": f"<b>{sales_person_.sales_person}</b>" if is_group else sales_person_.sales_person,
        "target_amount": 0,
        "achievement_amount": 0,
        "achievement_percentages": []
    }

    for sales_person_data in data_:
        calculate_sum(average_amount_row, sales_person_data)
        set_format(sales_person_data, average_percentage=False)

    set_format(average_amount_row)
    data.append(average_amount_row)
    data.extend(data_)
    return average_amount_row


def get_columns(filters):
    """ Columns of Report Table"""

    columns = [
        {"label": _("Sales Person"), "fieldname": "sales_person",  "fieldtype": "Link",
		 			"options":"Sales Person", "width": 200},
        {"label": _("Target Amount"), "fieldname": "target_amount", "fieldtype": "Data", "width": 200},
        {"label": _("Achievement Amount"), "fieldname": "achievement_amount", "fieldtype": "Data", "width": 200},
        {"label": _("Achievement(%)"), "fieldname": "achievement_percentage", "fieldtype": "Data", "precision":2, "width": 200},
	]

    return columns

def get_data(conditions, month, year, sales_person_names):
    requisition_query = """select sum(requisition.grand_total) as achievement_amount, requisition.sales_person, 
                    requisition.customer from `tabRequisition` requisition %s group by requisition.sales_person
                    order by achievement_amount desc""" % conditions

    sales_target = """select sales_target.sales_person, sales_target.target_amount from `tabSales Person Target`
                    sales_target where sales_target.sales_person in %s and sales_target.month='%s'
                     and sales_target.year='%s'""" % (sales_person_names, month, year)

    main_query = """select sales_person.name as sales_person, IFNULL(sales.achievement_amount, 0)as achievement_amount,
                    IFNULL(sales_target.target_amount, 0)as target_amount,
                    (CASE WHEN sales_target.target_amount is not null
                           THEN 100/(sales_target.target_amount/sales.achievement_amount)
                           ELSE 0 END) as achievement_percentage from `tabSales Person` sales_person 
                    left join (%s) sales on sales_person.name = sales.sales_person left join (%s) sales_target
                    on sales_person.name=sales_target.sales_person where sales_person.name in %s""" % (
                    requisition_query, sales_target, sales_person_names)

    query_result = frappe.db.sql(main_query, as_dict=1, debug=0)
    return query_result


def get_conditions(filters):
    month = filters.get('month')
    year = filters.get('year')
    from_date, to_date = get_from_date_and_to_date(month, year)
    print(from_date, to_date)

    conditions = ["requisition.docstatus=1"]
    # conditions = []

    if from_date:
        conditions.append("requisition.transaction_date >= '%s'" % from_date)
    if to_date:
        conditions.append("requisition.transaction_date <= '%s'" % to_date)
    # if sales_person:
    #     conditions.append("requisition.sales_person = '%s'" % sales_person)

    return " and ".join(conditions)

def add_sales_person_to_condition(conditions, sales_person, all_child=False, including_self=False):
    sales_person_name = sales_person.get('name') or sales_person.get('sales_person')
    conditions_ = ''

    if sales_person.is_group:
        sales_person_names = get_sales_persons_list(sales_person_name, all_child, including_self, as_tuple_str=True)
    else:
        sales_person_names = "('%s')" % sales_person_name


    if sales_person_names and conditions:
        conditions_ = conditions + ' and requisition.sales_person in ' + sales_person_names
        return ("where " + conditions_, sales_person_names)

    return (conditions_, None)


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

def get_default(value):
    if not value:
        return 0
    elif isinstance(value, str):
        return float(value.replace(',','').replace(f'{currency_symbol} ',''))

    return value
def set_format(total_row, average_percentage=True):
    # print("======>>", total_row['target_amount'])
    total_row['target_amount'] = currency_format(total_row['target_amount'])
    total_row['achievement_amount'] = currency_format(total_row['achievement_amount'])

    if average_percentage and total_row.get('achievement_percentages'):
        percentages = total_row.get('achievement_percentages')
        average = sum(percentages) / len(percentages)
        total_row['achievement_percentage'] = "{:.2f}".format(average)
    else:
        total_row['achievement_percentage'] = "{:.2f}".format(get_default(total_row.get('achievement_percentages')))

    return total_row

def calculate_sum(total_row, sales_person_row):
    total_row['target_amount'] += get_default(sales_person_row['target_amount'])
    total_row['achievement_amount'] += get_default(sales_person_row['achievement_amount'])
    total_row['achievement_percentages'].append(get_default(sales_person_row['achievement_percentage']))

def make_bold(row):
    row['sales_person'] = f"<b>{row['sales_person']}</b>"
    row['target_amount'] = f"<b>{row['target_amount']}</b>"
    row['achievement_amount'] = f"<b>{row['achievement_amount']}</b>"
    row['achievement_percentage'] = f"<b>{row['achievement_percentage']}</b>"

def currency_format(amount):
    return frappe.utils.fmt_money(get_default(amount), currency=get_currency_symbol())

def get_current_sales_person(filters):
    roles = frappe.get_roles(frappe.session.user)

    if frappe.db.exists("Sales Person", {'name': filters.get('sales_person')}):
        sales_person = frappe.get_doc("Sales Person", filters.get('sales_person'))
    elif frappe.db.exists('Sales Person', {'user': frappe.session.user}):
        sales_person = frappe.get_doc('Sales Person', {'user': frappe.session.user})
    elif 'System Manager' in roles:
        sales_person = frappe.get_doc("Sales Person", "Sales Team")
    else:
        sales_person = None

    return sales_person


def get_from_date_and_to_date(month, year):
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
              'August', 'September', 'October', 'November', 'December']

    # year = get_absolute_year(month, year)
    year = int(year)
    month = months.index(month) + 1
    from_date = datetime.datetime(year, month, 1).date()

    if month == 12:
        to_date = datetime.datetime(year, month, 31).date()
    else:
        to_date = (datetime.datetime(year, month + 1, 1) - datetime.timedelta(days=1)).date()

    return from_date, to_date

# def get_absolute_year(month, year):
#     fiscal_year = frappe.get_doc('Fiscal Year', year)
#     months = pd.date_range(fiscal_year.year_start_date, fiscal_year.year_end_date, freq='MS').strftime("%B-%Y").tolist()

#     for i, month_ in enumerate(months):
#         if month in month_:
#             return int(month_.split('-')[1])

#         elif month in months[-i]:
#             return int(month_.split('-')[1])

#     frappe.throw(f"'{month}' doesn't exist on Fiscal year '{fiscal_year.name}'")
