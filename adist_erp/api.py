import frappe


@frappe.whitelist()
def get_customer_outstanding_amount(customer_name):
    """
    Get the outstanding amount for a customer
    """
    outstanding_amount = frappe.db.sql("""
        SELECT 
            SUM(outstanding_amount) as outstanding_amount
        FROM 
            `tabSales Invoice`
        WHERE 
            customer = %s
    """, (customer_name), as_dict=1)
    return outstanding_amount


@frappe.whitelist()
def get_last_payment_info(customer_name):
    # Get the last payment date and amount for the customer
    last_payment = frappe.db.sql(
        """
        SELECT 
            posting_date,
            paid_amount
        FROM 
            `tabPayment Entry`
        WHERE 
            party_type = 'Customer' AND party = %s
        ORDER BY 
            modified DESC
        LIMIT 1
        """, 
        (customer_name,),
        as_dict=True
    )
    
    # Return the last payment date and amount, or None if no payment found
    if last_payment:
        return {
            'last_payment_date': last_payment[0].posting_date,
            'last_payment_amount': last_payment[0].paid_amount
        }
    else:
        return None

