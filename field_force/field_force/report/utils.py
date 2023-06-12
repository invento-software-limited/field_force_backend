import datetime
import os
import frappe
# import cv2

def set_user_link(doc):
    if doc.user:
        title = doc.user_fullname or doc.user
        doc['user'] = f'<a href="/app/user/{doc.user}" target="_blank">{title}</a>'

def set_link_to_doc(doc, field, doc_url='', label=None):
    doc[field] = f'<a href="/app/{doc_url}/{doc[field]}" ' \
                                  f'target="_blank">{label or doc[field]}</a>'

# def rotate_image(image_path):
#     # read an image as input using OpenCV
#     image = cv2.imread(image_path)
#
#     rotated_image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
#
#     cv2.imwrite(image_path, rotated_image)

    # image_path = image_path + f'?t={datetime.datetime.now().timestamp()}'
    # return image_path

def set_image_url(doc, site_directory=None, rotate=False):
    site_directory = site_directory or  get_site_directory_path()
    image_path = '/files/default-image.png'

    if doc.image:
        if 'private/files/' in doc.image:
            image_path = f"{site_directory}{doc.image}"
            # rotate_image(image_path)

        elif '/files/' in doc.image:
            image_path = f"{site_directory}/public{doc.image}"
            # rotate_image(image_path)

    if os.path.exists(image_path):
        doc.image = doc.image + f'?t={datetime.datetime.now().timestamp()}'
    else:
        doc.image = '/files/default-image.png'

download_button = '''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" style="margin-top:20px;"
                  class="bi bi-cloud-download" viewBox="0 0 16 16"><path d="M4.406 1.342A5.53 5.53 0 0 1 8 0c2.69 0
                   4.923 2 5.166 4.579C14.758 4.804 16 6.137 16 7.773 16 9.569 14.502 11 12.687 11H10a.5.5
                   0 0 1 0-1h2.688C13.979 10 15 8.988 15 7.773c0-1.216-1.02-2.228-2.313-2.228h-.5v-.5C12.188
                   2.825 10.328 1 8 1a4.53 4.53 0 0 0-2.941 1.1c-.757.652-1.153 1.438-1.153 2.055v.448l-.445.049C2.064
                   4.805 1 5.952 1 7.318 1 8.785 2.23 10 3.781 10H6a.5.5 0 0 1 0 1H3.781C1.708 11 0 9.366 0 7.318c0-1.763
                    1.266-3.223 2.942-3.593.143-.863.698-1.723 1.464-2.383z"/><path d="M7.646 15.854a.5.5 0 0 0 .708
                    0l3-3a.5.5 0 0 0-.708-.708L8.5 14.293V5.5a.5.5 0 0 0-1 0v8.793l-2.146-2.147a.5.5 0 0 0-.708.708l3 3z"/></svg>'''

def set_image_download_button(doc, site_directory=None):
    if doc.get('image'):
        doc.image_download = f'<a href="{doc.image}" download title="Click here to download the image">{download_button}</a>'

def get_site_directory_path():
    site_name = frappe.local.site
    cur_dir = os.getcwd()
    return os.path.join(cur_dir, site_name)


location_icon = '''<svg xmlns="http://www.w3.org/2000/svg" width="25" height="25" fill="currentColor"
                style="margin: 20 0 0 20;"
                class="bi bi-geo-alt" viewBox="0 0 16 16"> <path d="M12.166 8.94c-.524 1.062-1.234 2.12-1.96
                3.07A31.493 31.493 0 0 1 8 14.58a31.481 31.481 0 0 1-2.206-2.57c-.726-.95-1.436-2.008-1.96-3.07C3.304
                7.867 3 6.862 3 6a5 5 0 0 1 10 0c0 .862-.305 1.867-.834 2.94zM8 16s6-5.686 6-10A6 6 0 0 0 2
                6c0 4.314 6 10 6 10z"/><path d="M8 8a2 2 0 1 1 0-4 2 2 0 0 1 0 4zm0 1a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>
                </svg>'''

location_icon_2 = '''<svg xmlns="http://www.w3.org/2000/svg" width="25" height="25" fill="currentColor"
        class="bi bi-geo-alt-fill" viewBox="0 0 16 16" style="margin: 20 0 0 20;">
        <path d="M8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10zm0-7a3 3 0 1 1 0-6 3 3 0 0 1 0 6z"/></svg>'''

def set_google_map_location_button(doc):
    if doc.latitude and doc.longitude:
        google_map_url = f"https://maps.google.com/maps?q={doc.latitude}," \
                                f"{doc.longitude}&ll={doc.latitude},{doc.longitude}&z=13"

        location_button = f'<a href="{google_map_url}" target="_blank" title="View on Map">{location_icon}</a>'
        return location_button

    return ""

