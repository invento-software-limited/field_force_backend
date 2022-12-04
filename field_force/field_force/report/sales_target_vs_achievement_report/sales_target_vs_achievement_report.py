# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt
from numpy import mean

import frappe
from field_force.field_force.doctype.sales_target.sales_target import get_sales_persons
from frappe import _
import datetime, calendar


def get_currency_symbol():
    frappe.defaults.get_user_default('Currency')
    return frappe.db.get_value("Currency", "BDT", "symbol", cache=True)

def execute(filters=None):
    global currency_symbol
    currency_symbol = get_currency_symbol()

    columns = get_columns(filters)
    conditions = get_conditions(filters)

    month_number = datetime.datetime.strptime(filters.get('from_date'), '%Y-%m-%d').month
    month = calendar.month_name[month_number]
    year = frappe.defaults.get_user_default("fiscal_year")
    sales_person = get_current_sales_person(filters)
    data = []

    if sales_person:
        # print(sales_person.type, filters.get('type'))

        if sales_person.type in ['Channel Manager', 'Manager', None] and filters.get('type') == 'By Supervisor':
            sales_persons = get_sales_persons(sales_person.name, type='Supervisor')
            # print("=====>>>", sales_persons)

            for sales_person_ in sales_persons:
                if sales_person_.type == 'Supervisor' and sales_person_.is_group:
                    conditions_, sales_person_names  = add_sales_person_to_condition(conditions, sales_person_,
                                                                                     all_child=True, including_self=True)
                    # print("====>>", sales_person_.sales_person, sales_person_names, conditions_)
                    if sales_person_names and conditions_:
                        data_ = get_data(conditions_, month, year, sales_person_names, group_wise=False)

                        if data_:
                            row = make_sum_and_push_to_data_list(data, data_, sales_person_, is_group=True)
                            make_bold(row)

        elif sales_person.type in ['Channel Manager', None] and filters.get('type') == 'By Manager':
            sales_persons = get_sales_persons(sales_person.name, all_child=True, type='Manager')
            # print(sales_persons)

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
                data_ = get_data(conditions_, month, year, sales_person_names, group_wise=False)

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

def get_data(conditions, month, year, sales_person_names, group_wise=False):
    sales_order_query = """select sum(sales_order.grand_total) as achievement_amount, sales_order.sales_person, 
                    sales_order.customer from `tabSales Order` sales_order %s group by sales_order.sales_person
                    order by achievement_amount desc""" % conditions

    # target_query = """select sales_target.sales_person, sales_target.target_amount from `tabSales Person Target`
    #                 sales_target where sales_target.sales_person in %s and sales_target.month='%s'
    #                 and sales_target.year='%s'""" % (sales_person_names, month, year)

    if group_wise:
        sales_target_query = """select sum(sales.achievement_amount) as achievement_amount, sales.sales_person,
                                sum(sales_target.target_amount) as target_amount,
                                (CASE WHEN sum(sales_target.target_amount) is not null 
                                       THEN 100/(sum(sales_target.target_amount)/sum(sales.achievement_amount))
                                       ELSE 0
                                END) as achievement_percentage from (%s) sales left join `tabSales Person Target` 
                                sales_target on sales_target.sales_person=sales.sales_person where sales_target.month='%s'
                                and sales_target.year='%s'""" % (sales_order_query, month, year)
    else:
        sales_target_query = """select sales.achievement_amount as achievement_amount, sales.sales_person,
                                sales_target.target_amount as target_amount,
                                (CASE WHEN sales_target.target_amount is not null 
                                       THEN 100/(sales_target.target_amount/sales.achievement_amount)
                                       ELSE 0
                                END) as achievement_percentage from (%s) sales left join `tabSales Person Target` 
                                sales_target on sales_target.sales_person=sales.sales_person where sales_target.month='%s'
                                and sales_target.year='%s'""" % (sales_order_query, month, year)

    # print(sales_target_query)
    query_result = frappe.db.sql(sales_target_query, as_dict=1, debug=0)
    return query_result


def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    # sales_person = filters.get('sales_person')

    conditions = ["sales_order.docstatus=1"]
    # conditions = []

    if from_date:
        conditions.append("sales_order.transaction_date >= '%s'" % from_date)
    if to_date:
        conditions.append("sales_order.transaction_date <= '%s'" % to_date)
    # if sales_person:
    #     conditions.append("sales_order.sales_person = '%s'" % sales_person)

    return " and ".join(conditions)

def add_sales_person_to_condition(conditions, sales_person, all_child=False, including_self=False):
    sales_person_name = sales_person.get('name') or sales_person.get('sales_person')
    conditions_ = ''

    if sales_person.is_group:
        sales_person_names = get_sales_persons_list(sales_person_name, all_child, including_self, as_tuple_str=True)
    else:
        sales_person_names = "('%s')" % sales_person_name


    if sales_person_names and conditions:
        conditions_ = conditions + ' and sales_order.sales_person in ' + sales_person_names
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

    if average_percentage:
        total_row['achievement_percentage'] = "{:.2f}".format(mean(total_row['achievement_percentages']))
    else:
        total_row['achievement_percentage'] = "{:.2f}".format(total_row['achievement_percentage'])

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
    return frappe.utils.fmt_money(amount, currency=get_currency_symbol())

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

# # @frappe.whitelist()
# # def sales_persons(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
# #     # sales_person = get_current_sales_person({'sales_person': None})
# #     return get_sales_persons('Sales Team')
#
# @frappe.whitelist()
# # @frappe.validate_and_sanitize_search_inputs
# def sales_persons(doctype, txt, searchfield, start, page_len, filters):
#     sales_person_names = get_sales_persons_list(sales_person.sales_person, all_child, including_self, as_tuple_str=True)
#
#
#     conditions = []
#     fields = get_fields("Sales Person", ["name", "parent_sales_person"])
#
#     return frappe.db.sql("""select {fields} from `tabSales Person`
# 		where ({key} like %(txt)s
# 				or name like %(txt)s)
# 			{fcond} {mcond}
# 		order by
# 			if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
# 			idx desc,
# 			name
# 		limit %(start)s, %(page_len)s""".format(**{
#         'fields': ", ".join(fields),
#         'key': searchfield,
#         'fcond': get_filters_cond(doctype, filters, conditions),
#         'mcond': get_match_cond(doctype)
#         }), {
#          'txt': "%%%s%%" % txt,
#          '_txt': txt.replace("%", ""),
#          'start': start,
#          'page_len': page_len
#      })
