# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt
import os
import random

from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

import frappe
import datetime
from frappe.model.document import Document
from frappe.core.doctype.communication import email

import openpyxl

class Requisition(Document):
    def validate(self):
        self.set_user()
        self.set_customer_info()
        self.set_brand_and_image_to_requisition_items()
        self.validate_delivery_date()
        self.validate_items()

    # def before_save(self):
    #     generate_requisition_excel_and_attach(self)

    def on_submit(self):
        if self.docstatus == 1:
            frappe.db.set_value(self.doctype, self.name, 'status', 'Submitted')

        generate_requisition_excel_and_attach(self)

    def on_cancel(self):
        if self.docstatus == 2:
            frappe.db.set_value(self.doctype, self.name, 'status', 'Cancelled')

    def validate_delivery_date(self):
        if self.transaction_date > self.delivery_date:
            frappe.throw("Expected delivery date should be after Requisition date")

        for item in self.items:
            if not item.delivery_date:
                item.delivery_date = self.delivery_date

    def set_user(self):
        if not self.user:
            self.user = frappe.session.user
            self.user_fullname = frappe.db.get_value('User', self.user, 'full_name')

    def set_customer_info(self):
        if not self.customer_name or not self.distributor:
            customer_name, distributor= frappe.db.get_value('Customer', self.customer, ['customer_name', 'distributor'])

            if not self.customer_name and customer_name:
                self.customer_name = customer_name

            if not self.distributor and distributor:
                self.distributor = distributor

    def set_brand_and_image_to_requisition_items(self):
        for item in self.items:
            if not item.brand or not item.image:
                item.brand, item.image = frappe.db.get_value('Item', item.item_code, ['brand', 'image'])

    def validate_items(self):
        commission_brand_list = frappe.get_list('Customer Brand Commission',
                                                {'parent': self.customer}, ['brand', 'commission_rate'])
        commission_brand_dict = {}

        for commission in commission_brand_list:
            commission_brand_dict[commission.brand] = commission.commission_rate

        total_items = 0
        total_qty = 0
        total = 0

        if self.items:
            for item in self.items:
                if not item.qty:
                    frappe.throw(f"Please give quantity of item <b>{item.item_name}</b>")

                if not item.discount_percentage:
                    item.discount_percentage = commission_brand_dict.get(item.brand, 0)

                if not item.price_list_rate:
                    item.price_list_rate = frappe.db.get_value("Item Price", {"item_code": item.item_code,
                                                                              "selling": 1}, ["price_list_rate"])
                if not item.price_list_rate and not item.rate:
                    frappe.throw(f"There is no selling rate of item <b>{item.item_name}</b>")

                elif item.price_list_rate or item.rate:
                    if (item.price_list_rate and not item.rate) or (item.price_list_rate == item.rate):
                        if item.discount_percentage:
                            item.discount_amount = item.price_list_rate * (float(item.discount_percentage) / 100)
                        else:
                            item.discount_amount = 0

                        item.rate = item.price_list_rate - item.discount_amount

                    item.amount = item.qty * item.rate
                    total += item.amount

                total_items += 1
                total_qty += item.qty
                self.validate_accepted_qty(item)
        else:
            frappe.throw("Items are required")

        if total:
            self.total = total
            self.net_total = total
            self.grand_total = total

        if total_items and total_qty:
            self.total_qty = total_qty
            self.total_items = total_items

    def validate_accepted_qty(self, item):
        if not item.accepted_qty:
            item.accepted_qty = item.qty


def generate_requisition_excel_and_attach(requisition):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.name = requisition.name

    columns = ['[Product #]', '[Product Name]', '[UOM]', '[Quantity]', '[Unit Price]', '[Discount]', '[Nett Price]',
               '[Amount]', '[Tax Code]']

    generate_row(worksheet, 1, columns, font=default_font)
    row_count = 2

    for item in requisition.items:
        item_row_data = [item.item_code, item.item_name, item.uom, item.qty, item.price_list_rate,
                         item.discount_amount, f'=E{row_count}-F{row_count}',
                         f'=D{row_count}*G{row_count}', 'NA']

        generate_row(worksheet, row_count, item_row_data, font=default_font)
        row_count += 1

    file_name = f"Requisition_{requisition.name}.xlsx"
    file_path = get_directory_path('requisition/')
    absolute_path = file_path + file_name
    worksheet.sheet_view.zoomScale = 90
    workbook.save(absolute_path)

    file = attach_file(requisition, absolute_path, file_name)
    requisition.requisition_excel = file.file_url
    requisition.requisition_excel_file = f'<a class="attached-file-link" href="{file.file_url}"' \
                                         f' target="_blank">{file_name}</a>'
        # + f"?file={random.randint(100, 1000)}"

def attach_file(requisition, file_path, file_name):
    with open(file_path, "rb") as data:
        content = data.read()

    file = frappe.get_doc({
        "doctype": "File",
        "attached_to_doctype": requisition.doctype,
        "attached_to_name": requisition.name,
        "attached_to_field": 'requisition_excel',
        "folder": 'Home/Attachments',
        "file_name": file_name,
        "file_url": '',
        "is_private": 0,
        "content": content
    })
    file.save()
    return file

def generate_row(ws, row_count, column_values, font=None, font_size=None, color=None, height=None):
    cells = []
    amount_columns = [5, 7, 8]
    column_widths = [15, 15, 15,15, 15, 15,15, 15, 15,]

    for i, value in enumerate(column_values):
        column_number = i + 1
        cell = ws.cell(row=row_count, column=column_number)
        cell.value = value

        if font:
            cell.font = font
        elif font_size:
            cell.font = Font(size=font_size)
        if color:
            cell.fill = PatternFill(fgColor=color, fill_type='solid')

        # if isinstance(value, int):
        #     cell.number_format = "#,##0"
        # elif isinstance(value, float):
        if i+1 in amount_columns:
            cell.number_format = "#,##0.00"

        ws.column_dimensions[get_column_letter(i + 1)].width = column_widths[i]
        cell.alignment = Alignment(vertical='center')
        cells.append(cell)

    if height:
        ws.row_dimensions[row_count].height = height

    set_column_width(ws)
    return cells

def get_directory_path(directory_name):
    site_name = frappe.local.site
    cur_dir = os.getcwd()
    file_path = os.path.join(cur_dir, site_name, f'private/files/{directory_name}')
    os.makedirs(file_path, exist_ok=True)
    return file_path

default_font = Font(name='Calibri(Body)', size=11, bold=False, italic=False,  strike=False, underline='none')

def set_column_width(worksheet, column=None, width=None):
    if column and width:
        worksheet.column_dimensions[get_column_letter(column)].width = width
    else:
        for i, width_ in enumerate([12, 15, 12, 12, 12, 15]):
            worksheet.column_dimensions[get_column_letter(i + 1)].width = width_


@frappe.whitelist()
def get_brands_commission(customer, brand=None):
    customer = frappe.get_doc('Customer', customer)

    if customer.customer_group == "Retail Shop":
        distributor = frappe.get_doc("Distributor", customer.distributor)
        brand_wise_commission_dict = get_commissions_in_dict(distributor.commissions)
    else:
        brand_wise_commission_dict = get_commissions_in_dict(customer.commissions)

    if brand:
        return brand_wise_commission_dict.get(brand, 0)

    return brand_wise_commission_dict

def get_commissions_in_dict(commissions):
    brand_wise_commission_dict = {}

    for commission in commissions:
        brand_wise_commission_dict[commission.brand] = commission.commission_rate

    return brand_wise_commission_dict