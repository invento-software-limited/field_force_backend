from . import __version__ as app_version

app_name = "field_force"
app_title = "Field Force"
app_publisher = "Invento Software Limited"
app_description = "Field Force App"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "fieldforce@invento.com.bd"
app_license = "MIT"

# Includes in <head>
# ------------------


# For applying the customization of api endpoints and methods
from field_force import custom_hooks
custom_hooks.execute()

# include js, css files in header of desk.html
# app_include_css = "/assets/field_force/css/field_force.css"
# app_include_js = "/assets/field_force/js/field_force.js"

# include js, css files in header of web template
# web_include_css = "/assets/field_force/css/field_force.css"
# web_include_js = "/assets/field_force/js/field_force.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "field_force/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"User" : "public/js/user.js",
	"Sales Order" : "public/js/sales_order.js",
	"Sales Person" : "public/js/sales_person.js"
}

doctype_list_js = {
	"Sales Order" : "public/js/sales_order_list.js",
	"Sales Person" : "public/js/sales_person_list.js"
}

doctype_tree_js = {
	"Sales Person" : "public/js/sales_person_tree.js",
    "Employee" : "public/js/employee_tree.js"

}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "field_force.install.before_install"
# after_install = "field_force.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "field_force.uninstall.before_uninstall"
# after_uninstall = "field_force.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "field_force.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	# "Item":{
	# 	"before_save": "field_force.field_force.hook_functions.item.set_item_name_to_description"
	# },
	"Customer": {
        "after_rename": "field_force.field_force.hook_functions.customer.after_rename",
		"validate": "field_force.field_force.hook_functions.customer.validate",
		"after_insert": "field_force.field_force.hook_functions.customer.after_insert",
        "before_save": "field_force.field_force.hook_functions.customer.before_save",
        "on_update": "field_force.field_force.hook_functions.customer.on_update",
        # "on_update": "field_force.field_force.hook_functions.customer.set_image",
    },
    "Distributor": {
        "after_rename": "field_force.field_force.doctype.distributor.distributor.after_rename"
    },
	"Sales Order": {
		"validate": [
			"field_force.field_force.hook_functions.sales_order.set_extra_values",
			"field_force.field_force.hook_functions.sales_order.add_sales_person"
		],
		"after_insert": "field_force.field_force.hook_functions.sales_order.after_insert",
		# "before_save": "field_force.field_force.hook_functions.sales_order.add_sales_person",
		# "on_update": "field_force.field_force.hook_functions.sales_order.add_amount_to_achievement"
	},
	"Sales Person": {
		"before_save": "field_force.field_force.hook_functions.sales_person.before_save",
		"after_insert": "field_force.field_force.hook_functions.sales_person.after_insert",
		"on_update": "field_force.field_force.hook_functions.sales_person.on_update",
	}

}

# override_doctype_class = {
#     "Sales Order": "field_force.field_force.overridden_doctypes.sales_order.CustomSalesOrder",
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
    "cron": {
        "35 10 * * *": [
            "field_force.field_force.doctype.app_user_attendance.app_user_attendance.send_daily_attendance_mail"
        ]
    },
# 	"all": [
# 		"field_force.tasks.all"
# 	],
# 	"daily": [
# 		"field_force.tasks.daily"
# 	],
# 	"hourly": [
# 		"field_force.tasks.hourly"
# 	],
# 	"weekly": [
# 		"field_force.tasks.weekly"
# 	]
# 	"monthly": [
# 		"field_force.tasks.monthly"
# 	]
}

# Testing
# -------

# before_tests = "field_force.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "field_force.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "field_force.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"field_force.auth.validate"
# ]

# Translation
# --------------------------------

# Make link fields search translated document names for these DocTypes
# Recommended only for DocTypes which have limited documents with untranslated names
# For example: Role, Gender, etc.
# translated_search_doctypes = []
