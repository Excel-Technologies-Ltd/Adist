app_name = "adist_erp"
app_title = "Adist Erp"
app_publisher = "sohan.dev@excelbd.com"
app_description = "ADIST ERP"
app_email = "sohan.dev@excelbd.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/adist_erp/css/adist_erp.css"
# app_include_js = "/assets/adist_erp/js/adist_erp.js"

# include js, css files in header of web template
# web_include_css = "/assets/adist_erp/css/adist_erp.css"
# web_include_js = "/assets/adist_erp/js/adist_erp.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "adist_erp/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "adist_erp.utils.jinja_methods",
# 	"filters": "adist_erp.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "adist_erp.install.before_install"
# after_install = "adist_erp.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "adist_erp.uninstall.before_uninstall"
# after_uninstall = "adist_erp.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "adist_erp.utils.before_app_install"
# after_app_install = "adist_erp.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "adist_erp.utils.before_app_uninstall"
# after_app_uninstall = "adist_erp.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "adist_erp.notifications.get_notification_config"

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

override_doctype_class = {
	"Customer": "adist_erp.overrides.customer.newCustomer",
	"Sales Invoice": "adist_erp.overrides.sales_invoice.NewSalesInvoice"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Sales Invoice": {
		"on_submit": "adist_erp.doc_events.sales_invoice.send_sales_invoice_sms",
		"on_cancel": "adist_erp.doc_events.sales_invoice.send_sales_invoice_sms",
		
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"adist_erp.tasks.all"
# 	],
# 	"daily": [
# 		"adist_erp.tasks.daily"
# 	],
# 	"hourly": [
# 		"adist_erp.tasks.hourly"
# 	],
# 	"weekly": [
# 		"adist_erp.tasks.weekly"
# 	],
# 	"monthly": [
# 		"adist_erp.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "adist_erp.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "adist_erp.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "adist_erp.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["adist_erp.utils.before_request"]
# after_request = ["adist_erp.utils.after_request"]

# Job Events
# ----------
# before_job = ["adist_erp.utils.before_job"]
# after_job = ["adist_erp.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"adist_erp.auth.validate"
# ]

fixtures = [
	{
        "dt": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                [
                    "Sales Order-adist_last_payment_amount",
                    "Sales Order-adist_last_payment_date",
                    "Sales Order-adist_customer_outstanding_balance",
                    "Sales Invoice-adist_last_payment_amount",
                    "Sales Invoice-adist_last_payment_date",
                    "Sales Invoice-adist_customer_outstanding_balance",
                    "Sales Invoice-adist_sales_person_phone_no",
                    "Sales Invoice-adist_sales_person",
                    "Sales Order-adist_sales_person_phone_no",
                    "Sales Order-adist_sales_person",
                    "Sales Person-adist_sales_person_email",
                    "Sales Person-adist_sales_person_phone_no",
                    "Customer-adist_sales_person" , 
                    "Sales Invoice-delivery_status",
                    "Sales Invoice Item-total_value",
                    "Sales Invoice Item-discount_total",
                    "Stock Entry-adist_customer",
                    "Customer-tin",
                    "Customer-bin",
                    "Sales Invoice Item-adist_item",
                    "Sales Invoice-adist_item_group",
                    "Sales Order Item-discount_total",
                    "Sales Order Item-total_value",
                    "Sales Order-item_group",
                    "Purchase Order-item_group",
                    "Purchase Invoice-adist_item_group",
                    "Stock Entry-adist_sales_person",
                    "Delivery Note-adist_item_group",
                    "Stock Entry-adist_item_group",
                    "Purchase Receipt-adist_item_group",
                    "Payment Entry-adist_sales_person"
                    
                    
                ],
            ],
        ]
    },
 {"dt": "Property Setter",
  "filters": [
    [
        "name",
        "in",
        ["Sales Invoice-adist_item_group",
        "Sales Invoice Item-item_code-fetch_from",
        "Sales Invoice Item-main-field_order",
        "Supplier-main-quick_entry",
        "Customer-main-field_order",
        "Customer-main-quick_entry",
        "Item Price-main-quick_entry",
        "Item-main-quick_entry",
        "Sales Invoice-main-quick_entry,"
        "Stock Entry-main-field_order",
        "Stock Entry-section_break_jwgn-collapsible",
         ]
    ]
  ]
 }
]