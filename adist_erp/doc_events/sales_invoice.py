# import send_sms
from frappe.core.doctype.sms_settings.sms_settings import send_sms
import frappe
def send_sales_invoice_sms(doc, method):
    if method== "on_submit":
        mobile_number = get_customer_mobile_number(doc.customer)
        if mobile_number:
            sms_message = f"Dear {doc.customer_name}, your sales invoice {doc.name} has been submitted"
            send_sms([mobile_number], sms_message,success_msg=False)
    if method == "on_cancel":
        mobile_number = get_customer_mobile_number(doc.customer)
        if mobile_number:
            sms_message = f"Dear {doc.customer_name}, your sales invoice {doc.name} has been cancelled"
            send_sms([mobile_number], sms_message,success_msg=False)
    # if method == "on_update_after_submit" and doc.delivery_status == "Delivery Completed":
    #     mobile_number = get_customer_mobile_number(doc.customer)
    #     if mobile_number:
    #         sms_message = f"Dear {doc.customer_name}, your sales invoice {doc.name} delivery status has been updated to Delivery Completed"
    #         send_sms([mobile_number], sms_message,success_msg=False)
def get_customer_mobile_number(customer_id):
    return frappe.db.get_value("Customer", customer_id, "mobile_no")