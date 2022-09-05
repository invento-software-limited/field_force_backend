# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt
import os

from openpyxl.styles import Font, PatternFill, Alignment

import frappe
import datetime
from frappe.model.document import Document
from frappe.core.doctype.communication import email

import openpyxl

class Requisition(Document):

    def validate(self):
        self.validate_delivery_date()
        self.validate_items()
        # generate_requisition_excel_and_upload(self)

    def on_submit(self):
        if self.docstatus == 1:
            self.status = "Submitted"

        self.send_email()

    def on_cancel(self):
        if self.docstatus == 2:
            self.status = "Cancelled"

    def validate_delivery_date(self):
        if self.transaction_date > self.delivery_date:
            frappe.throw("Expected delivery date should be after Requisition date")

        for item in self.items:
            if not item.delivery_date:
                item.delivery_date = self.delivery_date

    def validate_items(self):
        total_items = 0
        total_qty = 0
        total = 0

        if self.items:
            for item in self.items:
                if not item.qty:
                    frappe.throw(f"Please give quantity of item <b>{item.item_name}</b>")

                if not item.rate and not item.amount and item.qty:
                    rate = frappe.db.get_value("Item Price", {"item_code": item.item_code, "selling": 1}, ["price_list_rate"])

                    if rate:
                        item.rate = rate
                        item.amount = item.qty * rate
                        total += item.amount
                    else:
                        frappe.throw(f"There is no selling rate of item <b>{item.item_name}</b>")

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

    def send_email(self):
        sender = "bib.demo2@gmail.com"
        sender_full_name = "Best in Brands Private Ltd."
        recipients = "joyanto@invento.com.bd,"
        cc = "joyonto51@gmail.com,"
        bcc = None
        email_subject = f"Requisition: {self.name}"
        email_body = "Hello, jayanta"

        file = generate_requisition_excel_and_upload(self)
        attachments = [file.name]

        # calling frappe email sender function
        email.make(doctype = self.doctype, name = self.name, content = email_body, subject = email_subject, sent_or_received = "Sent",
        sender = sender, sender_full_name = sender_full_name, recipients = recipients, communication_medium = "Email", send_email = True,
        print_html = None, print_format = None, attachments = attachments, send_me_a_copy = False, cc = cc, bcc = bcc,
        read_receipt = None, print_letterhead = True, email_template = None, communication_type = None)

        print("email sent")

def generate_requisition_excel_and_upload(requisition):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.name = requisition.name
    # wb.remove(wb['Sheet'])
    worksheet.cell(row=1, column=1).value = requisition.name
    worksheet.merge_cells(start_row=1, start_column=2, end_row=1, end_column=4)

    file_name = f"Requisition_{requisition.name}.xlsx"
    file_path = get_directory_path('requisition/')
    os.makedirs(file_path, exist_ok=True)
    absolute_path = file_path + file_name

    workbook.save(absolute_path)

    file = frappe.get_doc({
        "doctype": "File",
        "attached_to_doctype": requisition.doctype,
        "attached_to_name": requisition.name,
        "attached_to_field": 'requisition_excel',
        "folder": '',
        "file_name": file_name,
        "file_url": file_path,
        "is_private": 1,
        "content": requisition.name
    })
    file.save()
    requisition.requisition_excel = file.file_url
    return file

def get_directory_path(directory_name):
    site_name = frappe.local.site
    cur_dir = os.getcwd()
    return os.path.join(cur_dir, site_name, f'private/files/{directory_name}')

def generate_row(ws, row_count, column_values, font=None, font_size=None, color=None, height=None):
    cells = []

    for i, value in enumerate(column_values):
        column_number = i + 1
        cell = ws.cell(row=row_count, column=column_number, value=value)

        if font:
            cell.font = font
        elif font_size:
            cell.font = Font(size=font_size)
        if color:
            cell.fill = PatternFill(fgColor=color, fill_type='solid')

        # if isinstance(value, int) or column_number in qty_columns:
        #     cell.number_format = "#,##0"
        # elif isinstance(value, float) or column_number in amount_columns:
        #     cell.number_format = "#,##0.00"

        cell.alignment = Alignment(vertical='center')
        cells.append(cell)

    if height:
        ws.row_dimensions[row_count].height = height

    return cells
