# Copyright (c) 2026, Advance Distributions and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, nowdate


def execute(filters=None):
	filters = frappe._dict(filters or {})
	filters.from_date = getdate(filters.from_date or nowdate())
	filters.to_date = getdate(filters.to_date or nowdate())

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))

	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"label": _("Short Term Loan"),
			"fieldname": "short_term_loan",
			"fieldtype": "Link",
			"options": "Short Term Loan",
			"width": 200,
		},
		{
			"label": _("Opening Balance"),
			"fieldname": "opening_balance",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": _("Debit"),
			"fieldname": "debit",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": _("Credit"),
			"fieldname": "credit",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": _("Closing Balance"),
			"fieldname": "closing_balance",
			"fieldtype": "Currency",
			"width": 150,
		},
	]


def get_data(filters):
	conditions = build_conditions(filters)

	gl_entries = frappe.db.sql(
		f"""
		SELECT
			short_term_loan,
			posting_date,
			is_opening,
			debit,
			credit
		FROM `tabGL Entry`
		WHERE
			docstatus < 2
			AND is_cancelled = 0
			AND ifnull(short_term_loan, '') != ''
			AND posting_date <= %(to_date)s
			{conditions}
		ORDER BY posting_date
		""",
		filters,
		as_dict=True,
	)

	loan_data = {}
	for gle in gl_entries:
		loan = gle.short_term_loan
		if loan not in loan_data:
			loan_data[loan] = frappe._dict(
				{
					"short_term_loan": loan,
					"opening_balance": 0,
					"debit": 0,
					"credit": 0,
					"closing_balance": 0,
				}
			)

		if gle.posting_date < filters.from_date or gle.is_opening == "Yes":
			loan_data[loan].opening_balance += gle.debit - gle.credit
		else:
			loan_data[loan].debit += gle.debit
			loan_data[loan].credit += gle.credit

	data = []
	for loan, row in loan_data.items():
		row.closing_balance = row.opening_balance + row.debit - row.credit
		if row.opening_balance or row.debit or row.credit or row.closing_balance:
			data.append(row)

	return data


def build_conditions(filters):
	conditions = []

	if filters.get("company"):
		conditions.append("company = %(company)s")

	if filters.get("short_term_loan"):
		conditions.append("short_term_loan = %(short_term_loan)s")

	if filters.get("account"):
		conditions.append("account = %(account)s")

	if filters.get("cost_center"):
		conditions.append("cost_center = %(cost_center)s")

	if filters.get("against"):
		conditions.append("against = %(against)s")

	if filters.get("voucher_type"):
		conditions.append("voucher_type = %(voucher_type)s")

	if filters.get("voucher_no"):
		conditions.append("voucher_no = %(voucher_no)s")

	return " AND " + " AND ".join(conditions) if conditions else ""
