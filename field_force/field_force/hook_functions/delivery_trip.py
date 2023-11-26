
import datetime

import frappe
from frappe import _
from frappe.contacts.doctype.address.address import get_address_display
from frappe.model.document import Document
from frappe.utils import cint, get_datetime, get_link_to_form
from erpnext.stock.doctype.delivery_trip.delivery_trip import DeliveryTrip

class UpdateDeliveryTrip(DeliveryTrip):
    def __init__(self, *args, **kwargs):
        super(UpdateDeliveryTrip, self).__init__(*args, **kwargs)

        # Google Maps returns distances in meters by default
        self.default_distance_uom = (
            frappe.db.get_single_value("Global Defaults", "default_distance_unit") or "Meter"
        )
        self.uom_conversion_factor = frappe.db.get_value(
            "UOM Conversion Factor", {"from_uom": "Meter", "to_uom": self.default_distance_uom}, "value"
        )

    def validate(self):
        if self._action == "submit" and not self.driver:
            frappe.throw(_("A driver must be set to submit."))

        # self.validate_stop_addresses()

    def on_submit(self):
        self.update_status()
        self.update_delivery_notes()

    def on_update_after_submit(self):
        self.update_status()

    def on_cancel(self):
        self.update_status()
        self.update_delivery_notes(delete=True)

    def validate_stop_addresses(self):
        for stop in self.delivery_stops:
            if not stop.customer_address:
                stop.customer_address = get_address_display(frappe.get_doc("Address", stop.address).as_dict())

    def update_status(self):
        status = {0: "Draft", 1: "Scheduled", 2: "Cancelled"}[self.docstatus]

        if self.docstatus == 1:
            visited_stops = [stop.visited for stop in self.delivery_stops]
            if all(visited_stops):
                status = "Completed"
            elif any(visited_stops):
                status = "In Transit"

        self.db_set("status", status)

    def update_delivery_notes(self, delete=False):
        """
        Update all connected Delivery Notes with Delivery Trip details
        (Driver, Vehicle, etc.). If `delete` is `True`, then details
        are removed.

        Args:
                delete (bool, optional): Defaults to `False`. `True` if driver details need to be emptied, else `False`.
        """

        delivery_notes = list(
            set(stop.delivery_note for stop in self.delivery_stops if stop.delivery_note)
        )

        update_fields = {
            "driver": self.driver,
            "driver_name": self.driver_name,
            "vehicle_no": self.vehicle,
            "lr_no": self.name,
            "lr_date": self.departure_time,
        }

        for delivery_note in delivery_notes:
            note_doc = frappe.get_doc("Delivery Note", delivery_note)

            for field, value in update_fields.items():
                value = None if delete else value
                setattr(note_doc, field, value)

            note_doc.flags.ignore_validate_update_after_submit = True
            note_doc.save()

        delivery_notes = [get_link_to_form("Delivery Note", note) for note in delivery_notes]
        frappe.msgprint(_("Delivery Notes {0} updated").format(", ".join(delivery_notes)))

    @frappe.whitelist()
    def process_route(self, optimize):
        """
        Estimate the arrival times for each stop in the Delivery Trip.
        If `optimize` is True, the stops will be re-arranged, based
        on the optimized order, before estimating the arrival times.

        Args:
                optimize (bool): True if route needs to be optimized, else False
        """

        departure_datetime = get_datetime(self.departure_time)
        route_list = self.form_route_list(optimize)

        # For locks, maintain idx count while looping through route list
        idx = 0
        for route in route_list:
            directions = self.get_directions(route, optimize)

            if directions:
                if optimize and len(directions.get("waypoint_order")) > 1:
                    self.rearrange_stops(directions.get("waypoint_order"), start=idx)

                # Avoid estimating last leg back to the home address
                legs = directions.get("legs")[:-1] if route == route_list[-1] else directions.get("legs")

                # Google Maps returns the legs in the optimized order
                for leg in legs:
                    delivery_stop = self.delivery_stops[idx]

                    delivery_stop.lat, delivery_stop.lng = leg.get("end_location", {}).values()
                    delivery_stop.uom = self.default_distance_uom
                    distance = leg.get("distance", {}).get("value", 0.0)  # in meters
                    delivery_stop.distance = distance * self.uom_conversion_factor

                    duration = leg.get("duration", {}).get("value", 0)
                    estimated_arrival = departure_datetime + datetime.timedelta(seconds=duration)
                    delivery_stop.estimated_arrival = estimated_arrival

                    stop_delay = frappe.db.get_single_value("Delivery Settings", "stop_delay")
                    departure_datetime = estimated_arrival + datetime.timedelta(minutes=cint(stop_delay))
                    idx += 1

                # Include last leg in the final distance calculation
                self.uom = self.default_distance_uom
                total_distance = sum(
                    leg.get("distance", {}).get("value", 0.0) for leg in directions.get("legs")
                )  # in meters
                self.total_distance = total_distance * self.uom_conversion_factor
            else:
                idx += len(route) - 1

        self.save()

    def form_route_list(self, optimize):
        """
        Form a list of address routes based on the delivery stops. If locks
        are present, and the routes need to be optimized, then they will be
        split into sublists at the specified lock position(s).

        Args:
                optimize (bool): `True` if route needs to be optimized, else `False`

        Returns:
                (list of list of str): List of address routes split at locks, if optimize is `True`
        """
        if not self.driver_address:
            frappe.throw(_("Cannot Calculate Arrival Time as Driver Address is Missing."))

        home_address = get_address_display(frappe.get_doc("Address", self.driver_address).as_dict())

        route_list = []
        # Initialize first leg with origin as the home address
        leg = [home_address]

        for stop in self.delivery_stops:
            leg.append(stop.customer_address)

            if optimize and stop.lock:
                route_list.append(leg)
                leg = [stop.customer_address]

        # For last leg, append home address as the destination
        # only if lock isn't on the final stop
        if len(leg) > 1:
            leg.append(home_address)
            route_list.append(leg)

        route_list = [[sanitize_address(address) for address in route] for route in route_list]

        return route_list

    def rearrange_stops(self, optimized_order, start):
        """
        Re-arrange delivery stops based on order optimized
        for vehicle routing problems.

        Args:
                optimized_order (list of int): The index-based optimized order of the route
                start (int): The index at which to start the rearrangement
        """

        stops_order = []

        # Child table idx starts at 1
        for new_idx, old_idx in enumerate(optimized_order, 1):
            new_idx = start + new_idx
            old_idx = start + old_idx

            self.delivery_stops[old_idx].idx = new_idx
            stops_order.append(self.delivery_stops[old_idx])

        self.delivery_stops[start : start + len(stops_order)] = stops_order

    def get_directions(self, route, optimize):
        """
        Retrieve map directions for a given route and departure time.
        If optimize is `True`, Google Maps will return an optimized
        order for the intermediate waypoints.

        NOTE: Google's API does take an additional `departure_time` key,
        but it only works for routes without any waypoints.

        Args:
                route (list of str): Route addresses (origin -> waypoint(s), if any -> destination)
                optimize (bool): `True` if route needs to be optimized, else `False`

        Returns:
                (dict): Route legs and, if `optimize` is `True`, optimized waypoint order
        """
        if not frappe.db.get_single_value("Google Settings", "api_key"):
            frappe.throw(_("Enter API key in Google Settings."))

        import googlemaps

        try:
            maps_client = googlemaps.Client(key=frappe.db.get_single_value("Google Settings", "api_key"))
        except Exception as e:
            frappe.throw(e)

        directions_data = {
            "origin": route[0],
            "destination": route[-1],
            "waypoints": route[1:-1],
            "optimize_waypoints": optimize,
        }

        try:
            directions = maps_client.directions(**directions_data)
        except Exception as e:
            frappe.throw(_(str(e)))

        return directions[0] if directions else False
    
def sanitize_address(address):
	"""
	Remove HTML breaks in a given address

	Args:
	        address (str): Address to be sanitized

	Returns:
	        (str): Sanitized address
	"""

	if not address:
		return

	address = address.split("<br>")

	# Only get the first 3 blocks of the address
	return ", ".join(address[:3])