# import send_sms

import frappe
def sales_invoice_on_submit(doc,method):
    sales_order_id=""
    for item in doc.items:
        if item.sales_order:
            sales_order_id=item.sales_order
            break
    if sales_order_id:
        sales_order=frappe.get_doc("Sales Order",sales_order_id)
        if sales_order.custom_status != "Completed":
            sales_order.custom_status="Completed" 
            sales_order.save(ignore_permissions=True)
            print(sales_order)
    else:
        print("Sales Order not found")
        