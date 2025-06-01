# Copyright (c) 2025, sohan.dev@excelbd.com and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data

def get_columns():
    return [
        "Posting Date:Date:100",
        "ID:Link/Payment Entry:140",
        "Customer Code:Link/Customer:150",
        "Customer Name:Data:150",
        "Sales Person:Data:150",
        "Paid Amount:Currency:100",
        "Mode:Data:115",
        "Account:Data:150"
    ]

def get_data(filters):
    conditions = """
        pe.posting_date >= %(from_date)s AND 
        pe.posting_date <= %(to_date)s AND 
        pe.docstatus = 1
    """

    if filters.get("customer"):
        conditions += " AND pe.party = %(customer)s"

    if filters.get("sales_person"):
        conditions += " AND c.sales_person = %(sales_person)s"

    query = f"""
        SELECT
            pe.posting_date,
            pe.name,
            pe.party,
            pe.party_name,
            c.adist_sales_person,
            pe.paid_amount,
            pe.mode_of_payment,
            pe.paid_to
        FROM
            `tabPayment Entry` pe
        LEFT JOIN
            `tabCustomer` c ON c.name = pe.party
        WHERE
            {conditions}
        ORDER BY
            pe.posting_date DESC
    """

    return frappe.db.sql(query, filters, as_list=True)
