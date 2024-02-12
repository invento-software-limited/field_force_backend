
import datetime
import frappe
import os
from frappe import _
from frappe.contacts.doctype.address.address import get_address_display
from frappe.model.document import Document
from frappe.utils import cint, get_datetime, get_link_to_form
from erpnext.stock.doctype.delivery_trip.delivery_trip import DeliveryTrip
from frappe import publish_progress
from frappe.core.api.file import create_new_folder
from frappe.utils.file_manager import save_file
from frappe.utils.weasyprint import PrintFormatGenerator


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

    def before_submit(self):
        self.set_mushak_unique_number()
        self.get_requisition_files()

    def on_submit(self):
        # self.set_mushak_unique_number()
        self.update_status()
        self.update_delivery_notes()

    def on_update_after_submit(self):
        self.update_status()

    def on_cancel(self):
        self.update_status()
        self.update_delivery_notes(delete=True)


    def get_requisition_files(self):
        if self.delivery_stops:
            for stop in self.delivery_stops:
                if stop.get("requisition"):
                    files = get_files_path_from_requisition(stop.get("requisition"))
                    print("-------------------------------------------------------",files)
                    for file in files:
                        if file.get("requisition_standard"):
                            stop.requisition_pdf = file.get("requisition_standard")
                        if file.get("requisition_mushak_6.3"):
                            stop.mushak_6_3_pdf = file.get("requisition_mushak_6.3")
                        if file.get("customer_po_file"):
                            stop.po_file = file.get("customer_po_file")
                        if file.get("additional_doc_1"):
                            stop.additional_doc_1 = file.get("additional_doc_1")
                        if file.get("additional_doc_2"):
                            stop.additional_doc_2 = file.get("additional_doc_2")
                        if file.get("additional_doc_3"):
                            stop.additional_doc_3 = file.get("additional_doc_3")
                        if file.get("additional_doc_4"):
                            stop.additional_doc_4 = file.get("additional_doc_4")

    def set_mushak_unique_number(self):
        if self.delivery_stops:
            for stop in self.delivery_stops:
                if stop.get("requisition") and not stop.get("mushak_serial"):
                    reg = frappe.get_doc("Requisition", stop.get("requisition"))
                    if not reg.mushak_serial:
                        serial =  frappe.db.get_single_value("Field Force Settings", "series")
                        latest_serial = frappe.db.get_single_value("Field Force Settings", "latest_series")
                        mushak_serial = f"{serial}{latest_serial + 1}"
                        frappe.client.set_value("Field Force Settings", "Field Force Settings", "latest_series", latest_serial+1 )

                        reg.delivery_trip_created = 1
                        reg.delivery_trip = self.name
                        reg.mushak_serial = mushak_serial
                        reg.save(ignore_permissions=True)

                        stop.mushak_serial = mushak_serial
                        stop.status = "Scheduled"

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

# For Download Print FOrmat Wise Requisition


def create_folder(folder, parent):
    """Make sure the folder exists and return it's name."""
    new_folder_name = "/".join([parent, folder])

    if not frappe.db.exists("File", new_folder_name):
        create_new_folder(folder, parent)

    return new_folder_name


def get_pdf_data(doctype, name, print_format: None, letterhead: None):
    """Document -> HTML -> PDF."""
    html = frappe.get_print(doctype, name, print_format, letterhead=letterhead)
    return frappe.utils.pdf.get_pdf(html)


def save_and_attach(content, to_doctype, to_name, folder,auto_name=None, to_field=None, to_field_as_link=None,mushak=None):
    """
    Save content to disk and create a File document.

    File document is linked to another document.
    """
    if mushak == "Yes":
        final_name = "Mushak-6.3-" + to_name
        file_name = "{to_name}.pdf".format(to_name=final_name)
    else:
        file_name = "{to_name}.pdf".format(to_name=to_name)

    file = save_file(file_name, content, to_doctype, to_name, folder=folder, is_private=0, df=to_field)
    # set_file_to_doctype(to_doctype, to_name, file.file_url, to_field, to_field_as_link)
    download_requisition_file(file.file_url)

def set_file_to_doctype(to_doctype, to_name, file_url=None, to_field=None, to_field_as_link=None):
    try:
        if to_field and file_url:
            frappe.db.set_value(to_doctype, to_name, to_field, file_url)
        if to_field_as_link and file_url:
            file_name = file_url.split('/')[-1]
            link = f'<a class="attached-file-link" href="{file_url}" target="_blank">{file_name}</a>'
            frappe.db.set_value(to_doctype, to_name, to_field_as_link, link)

    except:

        pass

@frappe.whitelist()
def download_requisition_file(requisition_excel):
    if requisition_excel:
        file_path = get_site_directory_path() + '/public' + requisition_excel
        with open(file_path, "rb") as file:
            frappe.local.response.filename = requisition_excel.split('/')[2]
            frappe.local.response.filecontent = file.read()
            frappe.local.response.type = "download"
    else:
        frappe.throw('Group file not found!')

    return {}

def get_site_directory_path():
    site_name = frappe.local.site
    cur_dir = os.getcwd()
    return os.path.join(cur_dir, site_name)


import io
from zipfile import ZipFile
import json

@frappe.whitelist()
def download_all_files(doc_data):

    doc = frappe.get_doc("Delivery Trip",doc_data)

    files = get_file_urls_from_delivery_stops(doc.delivery_stops)
    print("===========================================",files)
    zip_file_name = f"{doc.name}.zip"

    # Open StringIO to grab in-memory ZIP contents
    byte_data = io.BytesIO()
    # The zip compressor
    zf = ZipFile(byte_data, "w")

    for file in files:
        try:
            zf.write(file, os.path.basename(file))
        except:
            pass

    # Must close zip for all contents to be written
    zf.close()

    frappe.local.response.filename = zip_file_name
    frappe.local.response.filecontent = byte_data.getvalue()
    frappe.local.response.type = "download"

def get_file_urls_from_delivery_stops(delivery_stops):
    urls = []
    for stop in delivery_stops:
        if stop.get("requisition_pdf"):
            req = get_site_directory_path() + '/public' + stop.get("requisition_pdf")
            urls.append(req)
        if stop.get("mushak_6_3_pdf"):
            mu = get_site_directory_path() + '/public' + stop.get("mushak_6_3_pdf")
            urls.append(mu)
        if stop.get("po_file"):
            po_file_path = get_site_directory_path() + '/public' + stop.get("po_file")
            urls.append(po_file_path)

    return urls

def get_files_path_from_requisition(requisition):
    try:
        data = []
        print_format = ["Requisition Standard","Requisition Mushak 6.3"]
        doc = frappe.get_doc("Requisition",requisition)
        
        letter_head = None
        for x in print_format:
            fallback_language = frappe.db.get_single_value("System Settings", "language") or "en"
            args = {
                "doctype": doc.get("doctype"),
                "name": doc.get("name"),
                "title": "Standard",
                "lang": getattr(doc, "language", fallback_language),
                "show_progress": 1,
                "auto_name": "requisiton",
                "print_format": x,
                "letter_head": letter_head,
                "to_field": "file",
                "to_field_as_link": "order_file"
            }
            if x == "Requisition Mushak 6.3":
                args["mushak"] = "Yes"

            if args.get("lang"):
                frappe.local.lang = args.get("lang")
                # unset lang and jenv to load new language
                frappe.local.lang_full_dict = None
                frappe.local.jenv = None

            doctype_folder = create_folder(args.get("doctype"), "Home")
            title_folder = create_folder(args.get("title"), doctype_folder)


            if frappe.db.get_value("Print Format", args.get("print_format"), "print_format_builder_beta"):
                doc = frappe.get_doc(args.get("doctype"), args.get("name"))
                pdf_data = PrintFormatGenerator(args.get("print_format"), doc, letter_head).render_pdf()
            else:
                pdf_data = get_pdf_data(args.get("doctype"), args.get("name"), args.get("print_format"), letter_head)

            """
            Save content to disk and create a File document.

            File document is linked to another document.
            """
            if args.get("mushak") == "Yes":
                final_name = "Mushak-6-3-" + args.get("name")
                file_name = "{to_name}.pdf".format(to_name=final_name)
            else:
                file_name = "{to_name}.pdf".format(to_name=args.get("name"))

            file = save_file(file_name, pdf_data, args.get("doctype"), args.get("name"), folder=title_folder, is_private=0, df=args.get("to_field"))
            # set_file_to_doctype(to_doctype, to_name, file.file_url, to_field, to_field_as_link)
            label = x.replace(' ','_').lower()
            data.append({label : file.file_url})

        # Get And Insert PO File to zip
        fileds = ["customer_po_file","additional_doc_1","additional_doc_2","additional_doc_3","additional_doc_4"]
        for field_name in fileds:  
            if doc.get("{}".format(field_name)):
                try:
                    data.append({"{}".format(field_name): doc.get("{}".format(field_name))})
                except:
                    pass

        return data
    except:
        frappe.log_error(frappe.get_traceback(), 'pdf generatre failed')

@frappe.whitelist()
def get_requistion_for_delivery_trip(requisitions):
    try:
        requisitions = json.loads(requisitions)
    except:
        pass
    requisitions = requisitions.split(",")
    data = []
    for req in requisitions:
        requisition = frappe.get_doc("Requisition",req)
        data_dict = {}
        data_dict["requisition"] = requisition.name
        data_dict["customer"] = requisition.customer
        data_dict["total_qty"] = requisition.total_qty
        data_dict["grand_total"] = requisition.grand_total
        
        data.append(data_dict)

    return data

