def execute():
    import frappe.api
    import frappe.geo.utils
    import field_force.api
    from field_force.field_force.hook_functions import geo_location
    from frappe.desk.doctype.number_card import number_card
    from field_force.api_methods import number_card as field_force_number_card

    # number card has_permission
    number_card.has_permission = field_force_number_card.has_permission

    #overriding the validate_auth function
    # frappe.api.validate_auth = field_force.api.validate_auth

    # overriding the handle function
    # frappe.api.handle = field_force.api.handle

    # Geo location methods
    frappe.geo.utils.get_coords = geo_location.get_coords
    frappe.geo.utils.convert_to_geojson = geo_location.convert_to_geojson
    frappe.geo.utils.merge_location_features_in_one = geo_location.merge_location_features_in_one
    frappe.geo.utils.return_location = geo_location.return_location
    frappe.geo.utils.return_coordinates = geo_location.return_coordinates

    print("======>> Hook Changes Applied <=======")
