

import frappe
from frappe.core.doctype.sms_settings.sms_settings import send_sms
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice

class NewSalesInvoice(SalesInvoice):
    def on_update_after_submit(self):
        get_customer_mobile_number=frappe.db.get_value('Customer', self.customer, 'mobile_no')
        if get_customer_mobile_number and self.delivery_status == "Delivery Completed":
            sms_message = f"Dear {self.customer_name}, your sales invoice {self.name} has been delivered"
            send_sms([get_customer_mobile_number], sms_message,success_msg=False)


