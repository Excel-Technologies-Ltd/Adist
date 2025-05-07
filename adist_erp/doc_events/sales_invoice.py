# import send_sms
from frappe.core.doctype.sms_settings.sms_settings import send_sms

def send_sales_invoice_sms(doc, method):
    if method== "on_submit":
        if doc.contact_mobile:
            sms_message = f"Dear {doc.customer_name}, your sales invoice {doc.name} has been submitted"
            send_sms(doc.contact_mobile, sms_message)
    if method == "on_cancel":
        if doc.contact_mobile:
            sms_message = f"Dear {doc.customer_name}, your sales invoice {doc.name} has been cancelled"
            send_sms(doc.contact_mobile, sms_message)
    if method == "on_update" and doc.delivery_status == "Delivery Completed":
        if doc.contact_mobile:
            sms_message = f"Dear {doc.customer_name}, your sales invoice {doc.name} delivery status has been updated to Delivery Completed"
            send_sms(doc.contact_mobile, sms_message)
