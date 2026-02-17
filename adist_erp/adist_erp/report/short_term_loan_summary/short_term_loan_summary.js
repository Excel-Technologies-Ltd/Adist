// Copyright (c) 2026, Advance Distributions and contributors
// For license information, please see license.txt

frappe.query_reports["Short Term Loan Summary"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			reqd: 1,
			width: "60px",
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
			width: "60px",
		},
		{
			fieldname: "short_term_loan",
			label: __("Short Term Loan"),
			fieldtype: "Link",
			options: "Short Term Loan",
		},
		{
			fieldname: "account",
			label: __("Account"),
			fieldtype: "Link",
			options: "Account",
			get_query: function () {
				var company = frappe.query_report.get_filter_value("company");
				return {
					filters: {
						company: company,
					},
				};
			},
		},
		{
			fieldname: "cost_center",
			label: __("Cost Center"),
			fieldtype: "Link",
			options: "Cost Center",
			get_query: function () {
				var company = frappe.query_report.get_filter_value("company");
				return {
					filters: {
						company: company,
					},
				};
			},
		},
		{
			fieldname: "against",
			label: __("Against"),
			fieldtype: "Data",
		},
		{
			fieldname: "voucher_type",
			label: __("Voucher Type"),
			fieldtype: "Link",
			options: "DocType",
		},
		{
			fieldname: "voucher_no",
			label: __("Voucher No"),
			fieldtype: "Dynamic Link",
			options: "voucher_type",
		},
	],
};
