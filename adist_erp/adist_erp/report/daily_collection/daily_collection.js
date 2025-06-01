frappe.query_reports["Daily Collection"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": ("From Date"),
            "fieldtype": "Date",
            "default": get_today(),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": ("To Date"),
            "fieldtype": "Date",
            "default": get_today(),
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
    ],
    
    
   
}