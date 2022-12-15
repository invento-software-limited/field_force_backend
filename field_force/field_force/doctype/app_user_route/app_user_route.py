# Copyright (c) 2022, Invento Software Limited and contributors
# For license information, please see license.txt
import json

import frappe
from frappe.model.document import Document
from field_force.field_force.doctype.utils import set_employee, set_sales_person

class AppUserRoute(Document):
	def validate(self):
	# 	if frappe.session.user != 'administrator':
	# 		self.user = frappe.session.user

		if not self.email or not self.user_fullname:
			email, user_fullname = frappe.db.get_value('User', self.user, ['email', 'full_name'])

			if not self.email and email:
				self.email = email
			if not self.user_fullname and user_fullname:
				self.user_fullname = user_fullname

		set_sales_person(self)
		set_employee(self)
		self.set_location()

	def set_location(self):
		location = {
			"type": "FeatureCollection",
			"features": [
				get_location(self.latitude, self.longitude)
			]
		}

		filters = {
			'user': self.user,
			'server_date': self.server_date
		}

		if frappe.db.exists("App User Route", filters):
			routes = frappe.get_list('App User Route', filters, ['name', 'latitude', 'longitude'])
			location['features'].append({
				"type": "Feature",
				"properties": {},
				"geometry": {
					"type": "LineString",
					"coordinates": [
						[
							self.latitude,
							self.longitude
						]
					]
				}
			})

			for route in routes:
				location['features'].append(get_location(route.latitude, route.longitude))
				location['features'][1]['geometry']['coordinates'].append([route.latitude, route.longitude])

		self.location = json.dumps(location)

def get_location(latitude, longitude):
	return {
		"type": "Feature",
		"properties": {},
		"geometry": {
			"type": "Point",
			"coordinates": [
				latitude,
				longitude
			]
		}
	}

# location = {
# 	"type":"FeatureCollection",
# 	"features":[
# 		{
# 			"type":"Feature",
# 			"properties":{},
# 			"geometry": {
# 				"type":"Point",
# 				"coordinates":[
# 					90.393662,
# 					23.778498
# 				]
# 			}
# 		},
# 		{
# 			"type": "Feature",
# 			"properties": {},
# 			"geometry": {
# 				"type":"Point",
# 				"coordinates":[
# 					90.394092,
# 					23.779352
# 				]
# 			}
# 		},
# 		{
# 			"type": "Feature",
# 			"properties":{},
# 			"geometry": {
# 				"type":"Point",
# 				"coordinates":[
# 					90.392037,
# 					23.679165
# 				]
# 			}
# 		},
# 		{
# 			"type":"Feature",
# 			"properties":{},
# 			"geometry": {
# 				"type": "LineString",
# 				"coordinates": [
# 					[
# 						90.3752,
# 					 	23.778625
# 					],
# 					[
# 						90.394092,
# 						23.779504
# 					],
# 					[
# 						90.302037,
# 					 	23.709298
# 					]
# 				]
# 			}
# 		}
# 	]
# }