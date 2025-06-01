frappe.query_reports["Cheque in Hand"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": ("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_start(),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": ("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_end(),
            "reqd": 1
        },
        {
            "fieldname": "customer",
            "label": ("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
            "default": ""
        },
        {
            "fieldname": "sales_person",
            "label": ("Sales Person"),
            "fieldtype": "Link",
            "options": "Sales Person",
            "default": ""
        }
    ]
}