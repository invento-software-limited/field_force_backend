# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
import datetime
from frappe.model.document import Document

class Requisition(Document):

	def validate(self):
		self.validate_delivery_date()
		self.validate_items()

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
						frappe.throw(f"There is not selling rate of item <b>{item.item_name}</b>")

				total_items += 1
				total_qty += item.qty
		else:
			frappe.throw("Items are required")

		if total:
			self.total = total
			self.net_total = total
			self.grand_total = total

		if total_items and total_qty:
			self.total_qty = total_qty
			self.total_items = total_items

	def on_submit(self):
		if self.docstatus == 1:
			self.status = "Submitted"

	def on_cancel(self):
		if self.docstatus == 2:
			self.status = "Cancelled"