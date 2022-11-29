from __future__ import unicode_literals

import frappe

from pymysql import InternalError

CUSTOM_DOCTYPES = {
	"App User Route": {
		"fields": ['name', 'user', 'user_fullname', 'location', 'server_date',
					   'server_time', 'latitude', 'longitude'],
		"info_text": ['<b>%s</b><br>%s<br>%s', 'user_fullname', 'server_date', 'server_time']
	},
	"App User Attendance": {
		"fields": ['name', 'user', 'user_fullname', 'location',  'server_date',
					  'type', 'server_time', 'latitude', 'longitude'],
		"info_text": ['<b>%s</b><br>%s<br>%s<br>%s', 'user_fullname', 'type', 'server_date', 'server_time']
	}
}


@frappe.whitelist()
def get_coords(doctype, filters, type):
	'''Get a geojson dict representing a doctype.'''
	filters_sql = get_coords_conditions(doctype, filters)[4:]

	coords = None
	if type == 'location_field':
		coords = return_location(doctype, filters_sql)
	elif type == 'coordinates':
		coords = return_coordinates(doctype, filters_sql)

	out = convert_to_geojson(type, coords, doctype)
	return out

def convert_to_geojson(type, coords, doctype=None):
	'''Converts GPS coordinates to geoJSON string.'''
	geojson = {"type": "FeatureCollection", "features": None}

	if type == 'location_field':
		geojson['features'] = merge_location_features_in_one(coords, doctype)
	elif type == 'coordinates':
		geojson['features'] = create_gps_markers(coords)

	return geojson

def merge_location_features_in_one(coords, doctype=None):
	'''Merging all features from location field.'''
	geojson_dict = []

	for element in coords:
		geojson_loc = frappe.parse_json(element['location'])

		if not geojson_loc:
			continue

		for coord in geojson_loc['features']:
			coord['properties']['name'] = get_info_text(doctype, element)

			# if doctype in CUSTOM_DOCTYPES.keys():
			# 	for field in CUSTOM_DOCTYPES[doctype]:
			# 		coord['properties'][field] = element[field]

			geojson_dict.append(coord.copy())

	return geojson_dict


def create_gps_markers(coords, doctype=None):
	'''Build Marker based on latitude and longitude.'''
	geojson_dict = []
	for i in coords:
		node = {"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": None}}
		node['properties']['name'] = i.name
		node['geometry']['coordinates'] = [i.latitude, i.longitude]
		geojson_dict.append(node.copy())

	return geojson_dict

def return_location(doctype, filters_sql):
	'''Get name and location fields for Doctype.'''
	fields, fields_str = get_fields(doctype)

	if filters_sql:
		try:
			coords = frappe.db.sql('''SELECT {} FROM `tab{}`  WHERE {}'''.format(fields_str, doctype,
																				 filters_sql), as_dict=True)
		except InternalError:
			frappe.msgprint(frappe._('This Doctype does not contain location fields'), raise_exception=True)
			return
	else:
		print(doctype, fields)
		coords = frappe.get_all(doctype, fields=fields)
	return coords


def return_coordinates(doctype, filters_sql):
	fields, fields_str = get_fields(doctype)

	'''Get name, latitude and longitude fields for Doctype.'''
	if filters_sql:
		try:
			coords = frappe.db.sql('''SELECT {} FROM `tab{}`  WHERE {}'''.format(fields_str, doctype,
																				 filters_sql), as_dict=True)
		except InternalError:
			frappe.msgprint(frappe._('This Doctype does not contain latitude and longitude fields'), raise_exception=True)
			return
	else:
		coords = frappe.get_all(doctype, fields=fields)
	return coords


def get_coords_conditions(doctype, filters=None):
	'''Returns SQL conditions with user permissions and filters for event queries.'''
	from frappe.desk.reportview import get_filters_cond
	if not frappe.has_permission(doctype):
		frappe.throw(frappe._("Not Permitted"), frappe.PermissionError)

	return get_filters_cond(doctype, filters, [], with_match_conditions=True)

def get_info_text(doctype, element):
	if doctype in CUSTOM_DOCTYPES.keys():
		info_text_list = CUSTOM_DOCTYPES[doctype]['info_text']
		data = [element[key] for key in info_text_list[1:]]
		info_text = info_text_list[0] % tuple(data)
		return info_text

	return element['name']

def get_fields(doctype):
	if doctype in CUSTOM_DOCTYPES.keys():
		fields = CUSTOM_DOCTYPES[doctype]['fields']
		fields_str = ", ".join(fields)
	else:
		fields = ['name', 'latitude', 'longitude']
		fields_str = "name, latitude, longitude"

	return (fields, fields_str)