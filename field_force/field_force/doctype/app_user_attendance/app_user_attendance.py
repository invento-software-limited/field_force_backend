# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt

import frappe
import datetime
import traceback
from frappe.model.document import Document

class AppUserAttendance(Document):
	def validate(self):
	# 	if frappe.session.user != 'administrator':
	# 		self.user = frappe.session.user

		if not self.email or not self.user_fullname:
			email, user_fullname = frappe.db.get_value('User', self.user, ['email', 'full_name'])

			if not self.email and email:
				self.email = email
			if not self.user_fullname and user_fullname:
				self.user_fullname = user_fullname

		try:
			device_datetime = datetime.datetime.strptime(f"{self.device_date} {self.device_time}", "%Y-%m-%d %H:%M:%S")
			server_datetime = datetime.datetime.strptime(f"{self.server_date} {self.server_time}", "%Y-%m-%d %H:%M:%S")
			time_difference = server_datetime - device_datetime if server_datetime > device_datetime \
				else device_datetime - server_datetime
			tolerance_time = 2 * 60

			if time_difference.seconds > tolerance_time:
				self.cheated = 1
			else:
				self.cheated = 0

		except Exception:
			frappe.log_error(traceback.format_exc(), "App User Attendance")

