import frappe
from hrms.payroll.doctype.payroll_entry.payroll_entry import PayrollEntry as PayrollEntryBase
import erpnext
from frappe.utils import flt
from frappe import _
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions

class PayrollEntry(PayrollEntryBase):
    def get_account(self, component_dict=None, process_payroll_accounting_entry_based_on_employee=False):
        account_dict = {}
        
        for key, amount in component_dict.items():
            if process_payroll_accounting_entry_based_on_employee and len(key) == 3:
                component, cost_center, employee = key
                account = self.get_salary_component_account(component)
                accounting_key = (account, cost_center, employee)
            else:
                if len(key) == 3:
                    component, cost_center, _ = key
                else:
                    component, cost_center = key
                account = self.get_salary_component_account(component)
                accounting_key = (account, cost_center)

            account_dict[accounting_key] = account_dict.get(accounting_key, 0) + amount
        
        return account_dict

    def make_accrual_jv_entry(self):
        self.check_permission("write")
        process_payroll_accounting_entry_based_on_employee = frappe.db.get_single_value(
            "Payroll Settings", "process_payroll_accounting_entry_based_on_employee"
        )
        self.employee_based_payroll_payable_entries = {}
        self._advance_deduction_entries = []

        earnings = (
            self.get_salary_component_total(
                component_type="earnings",
                process_payroll_accounting_entry_based_on_employee=process_payroll_accounting_entry_based_on_employee,  # Use setting for tracking
            )
            or {}
        )
        deductions = (
            self.get_salary_component_total(
                component_type="deductions",
                process_payroll_accounting_entry_based_on_employee=process_payroll_accounting_entry_based_on_employee,
            )
            or {}
        )

        payroll_payable_account = self.payroll_payable_account
        jv_name = ""
        precision = frappe.get_precision("Journal Entry Account", "debit_in_account_currency")

        if earnings or deductions:
            journal_entry = frappe.new_doc("Journal Entry")
            journal_entry.voucher_type = "Journal Entry"
            journal_entry.user_remark = _("Accrual Journal Entry for salaries from {0} to {1}").format(
                self.start_date, self.end_date
            )
            journal_entry.company = self.company
            journal_entry.posting_date = self.posting_date
            accounting_dimensions = get_accounting_dimensions() or []

            accounts = []
            currencies = []
            payable_amount = 0
            multi_currency = 0
            company_currency = erpnext.get_company_currency(self.company)

            # Earnings (aggregated by account and cost center)
            for acc_cc, amount in earnings.items():
                account, cost_center = acc_cc
                payable_amount = self.get_accounting_entries_and_payable_amount(
                    account,
                    cost_center or self.cost_center,
                    amount,
                    currencies,
                    company_currency,
                    payable_amount,
                    accounting_dimensions,
                    precision,
                    entry_type="debit",
                    accounts=accounts,
                )

            # Deductions
            for acc_cc, amount in deductions.items():
                if process_payroll_accounting_entry_based_on_employee and len(acc_cc) == 3:
                    account, cost_center, employee = acc_cc
                    payable_amount = self.get_accounting_entries_and_payable_amount(
                        account,
                        cost_center or self.cost_center,
                        amount,
                        currencies,
                        company_currency,
                        payable_amount,
                        accounting_dimensions,
                        precision,
                        entry_type="credit",
                        accounts=accounts,
                        party=employee,
                    )
                else:
                    account, cost_center = acc_cc
                    payable_amount = self.get_accounting_entries_and_payable_amount(
                        account,
                        cost_center or self.cost_center,
                        amount,
                        currencies,
                        company_currency,
                        payable_amount,
                        accounting_dimensions,
                        precision,
                        entry_type="credit",
                        accounts=accounts,
                    )

            payable_amount = self.set_accounting_entries_for_advance_deductions(
                accounts,
                currencies,
                company_currency,
                accounting_dimensions,
                precision,
                payable_amount,
            )

            # Payable entries
            if process_payroll_accounting_entry_based_on_employee:
                for employee, employee_details in self.employee_based_payroll_payable_entries.items():
                    net_pay = flt(employee_details.get("earnings", 0)) - flt(employee_details.get("deductions", 0))
                    if net_pay:
                        payable_amount = self.get_accounting_entries_and_payable_amount(
                            payroll_payable_account,
                            self.cost_center,
                            net_pay,
                            currencies,
                            company_currency,
                            payable_amount,
                            accounting_dimensions,
                            precision,
                            entry_type="payable",
                            party=employee,
                            accounts=accounts,
                        )
            else:
                if payable_amount:
                    payable_amount = self.get_accounting_entries_and_payable_amount(
                        payroll_payable_account,
                        self.cost_center,
                        payable_amount,
                        currencies,
                        company_currency,
                        0,
                        accounting_dimensions,
                        precision,
                        entry_type="payable",
                        accounts=accounts,
                    )

            journal_entry.set("accounts", accounts)
            
            if len(currencies) > 1:
                multi_currency = 1
            journal_entry.multi_currency = multi_currency
            journal_entry.title = payroll_payable_account
            journal_entry.save()

            try:
                journal_entry.submit()
                jv_name = journal_entry.name
                self.update_salary_slip_status(jv_name=jv_name)
            except Exception as e:
                if type(e) in (str, list, tuple):
                    frappe.msgprint(e)
                raise

        return jv_name

    def get_salary_component_total(
        self,
        component_type=None,
        process_payroll_accounting_entry_based_on_employee=False,
    ):
        salary_components = self.get_salary_components(component_type)
        if salary_components:
            component_dict = {}

            for item in salary_components:
                if not self.should_add_component_to_accrual_jv(component_type, item):
                    continue

                employee_cost_centers = self.get_payroll_cost_centers_for_employee(
                    item.employee, item.salary_structure
                )
                employee_advance = self.get_advance_deduction(component_type, item)

                for cost_center, percentage in employee_cost_centers.items():
                    amount_against_cost_center = flt(item.amount) * percentage / 100

                    if employee_advance:
                        self.add_advance_deduction_entry(
                            item, amount_against_cost_center, cost_center, employee_advance
                        )
                    else:
                        # For earnings, aggregate by component and cost center in component_dict
                        if component_type == "earnings":
                            key = (item.salary_component, cost_center)
                        else:
                            # For deductions, respect employee-based setting
                            key = (item.salary_component, cost_center, item.employee) if process_payroll_accounting_entry_based_on_employee else (item.salary_component, cost_center)
                        component_dict[key] = component_dict.get(key, 0) + amount_against_cost_center

                    # Always track earnings and deductions per employee for payable entries
                    if process_payroll_accounting_entry_based_on_employee:
                        self.set_employee_based_payroll_payable_entries(
                            component_type, item.employee, amount_against_cost_center
                        )

            account_details = self.get_account(
                component_dict=component_dict,
                process_payroll_accounting_entry_based_on_employee=process_payroll_accounting_entry_based_on_employee
            )

            return account_details