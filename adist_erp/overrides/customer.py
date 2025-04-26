import frappe
from erpnext.selling.doctype.customer.customer import Customer
class newCustomer(Customer):
    def before_save(self):
        sales_team = self.sales_team
        if len(sales_team)>0:
            self.adist_sales_person = sales_team[0].sales_person
        if len(sales_team)==0:
            self.adist_sales_person = None
           
