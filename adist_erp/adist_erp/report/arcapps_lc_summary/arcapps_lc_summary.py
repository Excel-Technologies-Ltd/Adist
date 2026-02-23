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
			"label": _("LC"),
			"fieldname": "lc",
			"fieldtype": "Link",
			"options": "LC",
			"width": 180,
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
			gle.lc,
			gle.posting_date,
			gle.is_opening,
			gle.debit,
			gle.credit
		FROM `tabGL Entry` gle
		WHERE
			gle.docstatus < 2
			AND gle.is_cancelled = 0
			AND ifnull(gle.lc, '') != ''
			AND gle.posting_date <= %(to_date)s
			{conditions}
		ORDER BY gle.posting_date
		""",
		filters,
		as_dict=True,
	)

	lc_data = {}
	for gle in gl_entries:
		lc = gle.lc
		if lc not in lc_data:
			lc_data[lc] = frappe._dict(
				{
					"lc": lc,
					"opening_balance": 0,
					"debit": 0,
					"credit": 0,
					"closing_balance": 0,
				}
			)

		if gle.posting_date < filters.from_date or gle.is_opening == "Yes":
			lc_data[lc].opening_balance += gle.debit - gle.credit
		else:
			lc_data[lc].debit += gle.debit
			lc_data[lc].credit += gle.credit

	data = []
	for lc, row in lc_data.items():
		row.closing_balance = row.opening_balance + row.debit - row.credit
		if row.opening_balance or row.debit or row.credit or row.closing_balance:
			data.append(row)

	return data


def build_conditions(filters):
	conditions = []

	if filters.get("company"):
		conditions.append("gle.company = %(company)s")

	if filters.get("lc"):
		conditions.append("gle.lc = %(lc)s")

	if filters.get("account"):
		conditions.append("gle.account = %(account)s")

	if filters.get("cost_center"):
		conditions.append("gle.cost_center = %(cost_center)s")

	return " AND " + " AND ".join(conditions) if conditions else ""
