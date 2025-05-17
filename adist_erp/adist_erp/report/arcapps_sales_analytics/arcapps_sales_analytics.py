import frappe
from frappe import _, scrub
from frappe.utils import add_days, add_to_date, flt, getdate

from erpnext.accounts.utils import get_fiscal_year


def execute(filters=None):
	return Analytics(filters).run()


class Analytics:
	def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})
		self.date_field = (
			"transaction_date"
			if self.filters.doc_type in ["Sales Order", "Purchase Order"]
			else "posting_date"
		)
		# Handle Payment Entry specifically
		if self.filters.doc_type == "Payment Entry":
			self.date_field = "posting_date"
		self.months = [
			"Jan",
			"Feb",
			"Mar",
			"Apr",
			"May",
			"Jun",
			"Jul",
			"Aug",
			"Sep",
			"Oct",
			"Nov",
			"Dec",
		]
		self.get_period_date_ranges()

	def run(self):
		self.get_columns()
		self.get_data()
		

		# Skipping total row for tree-view reports
		skip_total_row = 0

		if self.filters.tree_type in ["Supplier Group", "Item Group", "Customer Group", "Territory"]:
			skip_total_row = 1

		return self.columns, self.data, None, None, None, skip_total_row

	def get_columns(self):
		self.columns = [
			{
				"label": _(self.filters.tree_type),
				"options": self.filters.tree_type if self.filters.tree_type != "Order Type" else "",
				"fieldname": "entity",
				"fieldtype": "Link" if self.filters.tree_type != "Order Type" else "Data",
				"width": 140 if self.filters.tree_type != "Order Type" else 200,
			}
		]
		if self.filters.tree_type in ["Customer", "Supplier", "Item"]:
			self.columns.append(
				{
					"label": _(self.filters.tree_type + " Name"),
					"fieldname": "entity_name",
					"fieldtype": "Data",
					"width": 140,
				}
			)

		# Add Sales Person column if tree_type is Customer (always show it for Customer view)
		if self.filters.tree_type == "Customer":
			self.columns.append(
				{
					"label": _("Sales Person"),
					"fieldname": "sales_person",
					"fieldtype": "Data",
					"width": 140,
				}
			)

		if self.filters.tree_type == "Item":
			self.columns.append(
				{
					"label": _("UOM"),
					"fieldname": "stock_uom",
					"fieldtype": "Link",
					"options": "UOM",
					"width": 100,
				}
			)

		for end_date in self.periodic_daterange:
			period = self.get_period(end_date)
			self.columns.append(
				{"label": _(period), "fieldname": scrub(period), "fieldtype": "Float", "width": 120}
			)

		self.columns.append({"label": _("Total"), "fieldname": "total", "fieldtype": "Float", "width": 120})

	def get_data(self):
		if self.filters.tree_type in ["Customer", "Supplier"]:
			self.get_sales_transactions_based_on_customers_or_suppliers()
			self.get_rows()

		elif self.filters.tree_type == "Item":
			self.get_sales_transactions_based_on_items()
			self.get_rows()

		elif self.filters.tree_type in ["Customer Group", "Supplier Group", "Territory"]:
			self.get_sales_transactions_based_on_customer_or_territory_group()
			self.get_rows_by_group()

		elif self.filters.tree_type == "Item Group":
			self.get_sales_transactions_based_on_item_group()
			self.get_rows_by_group()

		elif self.filters.tree_type == "Order Type":
			if self.filters.doc_type != "Sales Order" and self.filters.doc_type != "Sales Invoice":
				self.data = []
				return
			self.get_sales_transactions_based_on_order_type()
			self.get_rows_by_group()

		elif self.filters.tree_type == "Project":
			self.get_sales_transactions_based_on_project()
			self.get_rows()
		elif self.filters.tree_type == "Sales Person":
			self.get_sales_transactions_based_on_sales_person()
			self.get_rows()


	def get_sales_transactions_based_on_order_type(self):
		if self.filters["value_quantity"] == "Value":
			value_field = "base_net_total"
		else:
			value_field = "total_qty"

		if self.filters.doc_type == "Payment Entry":
			# Payment entries don't have order type
			self.entries = []
			return

		self.entries = frappe.db.sql(
			""" select s.order_type as entity, s.{value_field} as value_field, s.{date_field}
			from `tab{doctype}` s where s.docstatus = 1 and s.company = %s and s.{date_field} between %s and %s
			and ifnull(s.order_type, '') != '' order by s.order_type
		""".format(date_field=self.date_field, value_field=value_field, doctype=self.filters.doc_type),
			(self.filters.company, self.filters.from_date, self.filters.to_date),
			as_dict=1,
		)

		self.get_teams()

	def get_sales_transactions_based_on_customers_or_suppliers(self):
		if self.filters["value_quantity"] == "Value":
			if self.filters.doc_type == "Payment Entry":
				value_field = "paid_amount as value_field"
			else:
				value_field = "base_net_total as value_field"
		else:
			if self.filters.doc_type == "Payment Entry":
				value_field = "paid_amount as value_field"  # Use paid_amount as quantity doesn't make sense for payments
			else:
				value_field = "total_qty as value_field"

		if self.filters.tree_type == "Customer":
			if self.filters.doc_type == "Payment Entry":
				entity = "party as entity"
				entity_name = "party_name as entity_name"
				
				# Add sales person field for Payment Entry when Customer is selected
				# Always fetch sales person for Customer view
				sales_person_field = """COALESCE((SELECT adist_sales_person FROM tabCustomer 
				                     WHERE name = `tabPayment Entry`.party), '') as sales_person"""
				additional_filter = "and payment_type='Receive' and party_type='Customer'"
				filter_params = (self.filters.company, self.filters.from_date, self.filters.to_date)
			else:
				entity = "customer as entity"
				entity_name = "customer_name as entity_name"
				
				# Add sales person field for other doctypes when Customer is selected
				# Always fetch sales person for Customer view
				sales_person_field = """COALESCE((SELECT adist_sales_person FROM tabCustomer 
				                     WHERE name = `tab{0}`.customer), '') as sales_person""".format(self.filters.doc_type)
				additional_filter = ""
				filter_params = (self.filters.company, self.filters.from_date, self.filters.to_date)
		else:  # Supplier
			if self.filters.doc_type == "Payment Entry":
				entity = "party as entity"
				entity_name = "party_name as entity_name"
				sales_person_field = "'' as sales_person"  # Suppliers don't have sales persons
				additional_filter = "and payment_type='Pay' and party_type='Supplier'"
				filter_params = (self.filters.company, self.filters.from_date, self.filters.to_date)
			else:
				entity = "supplier as entity"
				entity_name = "supplier_name as entity_name"
				sales_person_field = "'' as sales_person"  # Suppliers don't have sales persons
				additional_filter = ""
				filter_params = (self.filters.company, self.filters.from_date, self.filters.to_date)

		if self.filters.doc_type == "Payment Entry":
			self.entries = frappe.db.sql(
				f"""
				select {entity}, {entity_name}, {sales_person_field}, {value_field}, {self.date_field}
				from `tab{self.filters.doc_type}`
				where docstatus = 1 and company = %s
				{additional_filter}
				and {self.date_field} between %s and %s
				""",
				filter_params,
				as_dict=1,
			)
		else:
			query = f"""
				select {entity}, {entity_name}, {sales_person_field}, {value_field}, {self.date_field}
				from `tab{self.filters.doc_type}`
				where docstatus = 1 and company = %s
				{additional_filter}
				and {self.date_field} between %s and %s
			"""
			self.entries = frappe.db.sql(query, filter_params, as_dict=1)

		self.entity_names = {}
		self.sales_persons = {}
		for d in self.entries:
			self.entity_names.setdefault(d.entity, d.entity_name)
			if hasattr(d, 'sales_person'):
				self.sales_persons.setdefault(d.entity, d.sales_person)

	def get_sales_transactions_based_on_items(self):
		if self.filters["value_quantity"] == "Value":
			value_field = "base_net_amount"
		else:
			value_field = "stock_qty"

		if self.filters.doc_type == "Payment Entry":
			# Payment entries don't have item details directly
			self.entries = []
			return

		self.entries = frappe.db.sql(
			"""
			select i.item_code as entity, i.item_name as entity_name, i.stock_uom, i.{value_field} as value_field, s.{date_field}
			from `tab{doctype} Item` i , `tab{doctype}` s
			where s.name = i.parent and i.docstatus = 1 and s.company = %s
			and s.{date_field} between %s and %s
		""".format(date_field=self.date_field, value_field=value_field, doctype=self.filters.doc_type),
			(self.filters.company, self.filters.from_date, self.filters.to_date),
			as_dict=1,
		)

		self.entity_names = {}
		for d in self.entries:
			self.entity_names.setdefault(d.entity, d.entity_name)

	def get_sales_transactions_based_on_customer_or_territory_group(self):
		if self.filters["value_quantity"] == "Value":
			if self.filters.doc_type == "Payment Entry":
				value_field = "paid_amount as value_field"
			else:
				value_field = "base_net_total as value_field"
		else:
			if self.filters.doc_type == "Payment Entry":
				value_field = "paid_amount as value_field"
			else:
				value_field = "total_qty as value_field"
				
		additional_filter = ""
		filter_params = (self.filters.company, self.filters.from_date, self.filters.to_date)
		
		if self.filters.tree_type == "Customer Group":
			if self.filters.doc_type == "Payment Entry":
				entity_field = "COALESCE((SELECT customer_group FROM tabCustomer WHERE name = `tabPayment Entry`.party), '') as entity"
				
				if self.filters.sales_person:
					additional_filter = """and payment_type='Receive' and party_type='Customer'
					                         and exists (select 1 from tabCustomer 
					                         where name = `tabPayment Entry`.party 
					                         and adist_sales_person = %s)"""
					filter_params = (self.filters.company, self.filters.sales_person, self.filters.from_date, self.filters.to_date)
				else:
					additional_filter = "and payment_type='Receive' and party_type='Customer'"
			else:
				entity_field = "customer_group as entity"
				
				if self.filters.sales_person:
					additional_filter = """and exists (select 1 from tabCustomer 
					                      where name = `tab{0}`.customer 
					                      and adist_sales_person = %s)""".format(self.filters.doc_type)
					filter_params = (self.filters.company, self.filters.sales_person, self.filters.from_date, self.filters.to_date)
		elif self.filters.tree_type == "Supplier Group":
			if self.filters.doc_type == "Payment Entry":
				entity_field = "COALESCE((SELECT supplier_group FROM tabSupplier WHERE name = `tabPayment Entry`.party), '') as entity"
				additional_filter = "and payment_type='Pay' and party_type='Supplier'"
			else:
				entity_field = "supplier as entity"
				self.get_supplier_parent_child_map()
		else:  # Territory
			if self.filters.doc_type == "Payment Entry":
				entity_field = "COALESCE((SELECT territory FROM tabCustomer WHERE name = `tabPayment Entry`.party), '') as entity"
				
				if self.filters.sales_person:
					additional_filter = """and payment_type='Receive' and party_type='Customer'
					                         and exists (select 1 from tabCustomer 
					                         where name = `tabPayment Entry`.party 
					                         and adist_sales_person = %s)"""
					filter_params = (self.filters.company, self.filters.sales_person, self.filters.from_date, self.filters.to_date)
				else:
					additional_filter = "and payment_type='Receive' and party_type='Customer'"
			else:
				entity_field = "territory as entity"
				
				if self.filters.sales_person:
					additional_filter = """and exists (select 1 from tabCustomer
					                      where name = `tab{0}`.customer
					                      and adist_sales_person = %s)""".format(self.filters.doc_type)
					filter_params = (self.filters.company, self.filters.sales_person, self.filters.from_date, self.filters.to_date)

		if self.filters.doc_type == "Payment Entry":
			self.entries = frappe.db.sql(
				f"""
				select {entity_field}, {value_field}, {self.date_field}
				from `tab{self.filters.doc_type}`
				where docstatus = 1 and company = %s
				{additional_filter}
				and {self.date_field} between %s and %s
				""",
				filter_params,
				as_dict=1,
			)
		else:
			query = f"""
				select {entity_field}, {value_field}, {self.date_field}
				from `tab{self.filters.doc_type}`
				where docstatus = 1 and company = %s
				{additional_filter}
				and {self.date_field} between %s and %s
			"""
			self.entries = frappe.db.sql(query, filter_params, as_dict=1)
			
		self.get_groups()

	def get_sales_transactions_based_on_item_group(self):
		if self.filters["value_quantity"] == "Value":
			value_field = "base_net_amount"
		else:
			value_field = "qty"

		if self.filters.doc_type == "Payment Entry":
			# Payment entries don't have item details directly
			self.entries = []
			return

		if self.filters.sales_person and self.filters.tree_type == "Item Group":
			# For Item Group with Sales Person filter, join with Sales Invoice to get customer info
			self.entries = frappe.db.sql(
				f"""
				select i.item_group as entity, i.{value_field} as value_field, s.{self.date_field}
				from `tab{self.filters.doc_type} Item` i 
				join `tab{self.filters.doc_type}` s on s.name = i.parent
				join tabCustomer c on c.name = s.customer
				where i.docstatus = 1 and s.company = %s
				and c.adist_sales_person = %s
				and s.{self.date_field} between %s and %s
				""",
				(self.filters.company, self.filters.sales_person, self.filters.from_date, self.filters.to_date),
				as_dict=1,
			)
		else:
			self.entries = frappe.db.sql(
				f"""
				select i.item_group as entity, i.{value_field} as value_field, s.{self.date_field}
				from `tab{self.filters.doc_type} Item` i , `tab{self.filters.doc_type}` s
				where s.name = i.parent and i.docstatus = 1 and s.company = %s
				and s.{self.date_field} between %s and %s
				""",
				(self.filters.company, self.filters.from_date, self.filters.to_date),
				as_dict=1,
			)

		self.get_groups()

	def get_sales_transactions_based_on_project(self):
		if self.filters["value_quantity"] == "Value":
			if self.filters.doc_type == "Payment Entry":
				value_field = "paid_amount as value_field"
			else:
				value_field = "base_net_total as value_field"
		else:
			if self.filters.doc_type == "Payment Entry":
				value_field = "paid_amount as value_field"
			else:
				value_field = "total_qty as value_field"

		entity = "project as entity"
		additional_filter = ""
		filter_params = (self.filters.company, self.filters.from_date, self.filters.to_date)

		if self.filters.sales_person and self.filters.doc_type != "Payment Entry":
			# Add sales person filter for project view
			additional_filter = """and exists (select 1 from tabCustomer
			                      where name = `tab{0}`.customer
			                      and adist_sales_person = %s)""".format(self.filters.doc_type)
			filter_params = (self.filters.company, self.filters.sales_person, self.filters.from_date, self.filters.to_date)
		elif self.filters.sales_person and self.filters.doc_type == "Payment Entry":
			additional_filter = """and payment_type='Receive' and party_type='Customer'
			                     and exists (select 1 from tabCustomer 
			                     where name = `tabPayment Entry`.party 
			                     and adist_sales_person = %s)"""
			filter_params = (self.filters.company, self.filters.sales_person, self.filters.from_date, self.filters.to_date)
		elif self.filters.doc_type == "Payment Entry":
			additional_filter = "and ifnull(project, '') != ''"

		if self.filters.doc_type == "Payment Entry":
			self.entries = frappe.db.sql(
				f"""
				select {entity}, {value_field}, {self.date_field}
				from `tab{self.filters.doc_type}`
				where docstatus = 1 and company = %s
				{additional_filter}
				and {self.date_field} between %s and %s
				""",
				filter_params,
				as_dict=1,
			)
		else:
			query = f"""
				select {entity}, {value_field}, {self.date_field}
				from `tab{self.filters.doc_type}`
				where docstatus = 1 and company = %s
				{additional_filter}
				and ifnull(project, '') != ''
				and {self.date_field} between %s and %s
			"""
			self.entries = frappe.db.sql(query, filter_params, as_dict=1)
	def get_sales_transactions_based_on_sales_person(self):
		if self.filters["value_quantity"] == "Value":
			if self.filters.doc_type == "Payment Entry":
				value_field = "paid_amount as value_field"
			else:
				value_field = "base_net_total as value_field"
		else:
			if self.filters.doc_type == "Payment Entry":
				value_field = "paid_amount as value_field"  # Quantity doesn't make sense
			else:
				value_field = "total_qty as value_field"

		additional_filter = ""
		filter_params = (self.filters.company, self.filters.from_date, self.filters.to_date)

		if self.filters.doc_type == "Payment Entry":
			# Payment Entry sales person logic
			additional_filter = """
				and payment_type='Receive' and party_type='Customer'
				and exists (
					select 1 from tabCustomer 
					where name = `tabPayment Entry`.party 
					and ifnull(adist_sales_person, '') != ''
				)
			"""
		else:
			# Other doctypes sales person logic
			additional_filter = """
				and exists (
					select 1 from tabCustomer 
					where name = `tab{0}`.customer 
					and ifnull(adist_sales_person, '') != ''
				)
			""".format(self.filters.doc_type)

		# Now fetch: group by sales person
		if self.filters.doc_type == "Payment Entry":
			self.entries = frappe.db.sql(
				f"""
				select 
					(select adist_sales_person from tabCustomer where name = `tabPayment Entry`.party) as entity,
					{value_field},
					{self.date_field}
				from `tab{self.filters.doc_type}`
				where docstatus = 1 and company = %s
				{additional_filter}
				and {self.date_field} between %s and %s
				""",
				filter_params,
				as_dict=1,
			)
		else:
			self.entries = frappe.db.sql(
				f"""
				select 
					(select adist_sales_person from tabCustomer where name = `tab{self.filters.doc_type}`.customer) as entity,
					{value_field},
					{self.date_field}
				from `tab{self.filters.doc_type}`
				where docstatus = 1 and company = %s
				{additional_filter}
				and {self.date_field} between %s and %s
				""",
				filter_params,
				as_dict=1,
			)

		# Prepare entity name dictionary
		self.entity_names = {}
		for d in self.entries:
			self.entity_names.setdefault(d.entity, d.entity)  # Sales Person is its own name


	def get_rows(self):
		self.data = []
		self.get_periodic_data()

		for entity, period_data in self.entity_periodic_data.items():
			row = {
				"entity": entity,
				"entity_name": self.entity_names.get(entity) if hasattr(self, "entity_names") else None,
			}
			
			# Always add sales person to row if available for Customer view
			if self.filters.tree_type == "Customer" and hasattr(self, "sales_persons"):
				row["sales_person"] = self.sales_persons.get(entity, "")
				
			total = 0
			for end_date in self.periodic_daterange:
				period = self.get_period(end_date)
				amount = flt(period_data.get(period, 0.0))
				row[scrub(period)] = amount
				total += amount

			row["total"] = total

			if self.filters.tree_type == "Item":
				row["stock_uom"] = period_data.get("stock_uom")

			self.data.append(row)

	def get_rows_by_group(self):
		self.get_periodic_data()
		out = []

		for d in reversed(self.group_entries):
			# Don't include empty entries for Payment Entry
			if self.filters.doc_type == "Payment Entry" and not self.entity_periodic_data.get(d.name):
				continue
				
			row = {"entity": d.name, "indent": self.depth_map.get(d.name)}
			total = 0
			for end_date in self.periodic_daterange:
				period = self.get_period(end_date)
				amount = flt(self.entity_periodic_data.get(d.name, {}).get(period, 0.0))
				row[scrub(period)] = amount
				if d.parent and (self.filters.tree_type != "Order Type" or d.parent == "Order Types"):
					self.entity_periodic_data.setdefault(d.parent, frappe._dict()).setdefault(period, 0.0)
					self.entity_periodic_data[d.parent][period] += amount
				total += amount

			row["total"] = total
			out = [row, *out]

		self.data = out

	def get_periodic_data(self):
		self.entity_periodic_data = frappe._dict()

		for d in self.entries:
			if self.filters.tree_type == "Supplier Group":
				d.entity = self.parent_child_map.get(d.entity) if d.entity else None
				
			# Skip empty entities (especially for Payment Entry with group reports)
			if not d.entity:
				continue
				
			period = self.get_period(d.get(self.date_field))
			self.entity_periodic_data.setdefault(d.entity, frappe._dict()).setdefault(period, 0.0)
			self.entity_periodic_data[d.entity][period] += flt(d.value_field)

			if self.filters.tree_type == "Item":
				self.entity_periodic_data[d.entity]["stock_uom"] = d.stock_uom

	def get_period(self, posting_date):
		if self.filters.range == "Weekly":
			period = _("Week {0} {1}").format(str(posting_date.isocalendar()[1]), str(posting_date.year))
		elif self.filters.range == "Monthly":
			period = _(str(self.months[posting_date.month - 1])) + " " + str(posting_date.year)
		elif self.filters.range == "Quarterly":
			period = _("Quarter {0} {1}").format(
				str(((posting_date.month - 1) // 3) + 1), str(posting_date.year)
			)
		else:
			year = get_fiscal_year(posting_date, company=self.filters.company)
			period = str(year[0])
		return period

	def get_period_date_ranges(self):
		from dateutil.relativedelta import MO, relativedelta

		from_date, to_date = getdate(self.filters.from_date), getdate(self.filters.to_date)

		increment = {"Monthly": 1, "Quarterly": 3, "Half-Yearly": 6, "Yearly": 12}.get(self.filters.range, 1)

		if self.filters.range in ["Monthly", "Quarterly"]:
			from_date = from_date.replace(day=1)
		elif self.filters.range == "Yearly":
			from_date = get_fiscal_year(from_date)[1]
		else:
			from_date = from_date + relativedelta(from_date, weekday=MO(-1))

		self.periodic_daterange = []
		for _dummy in range(1, 53):
			if self.filters.range == "Weekly":
				period_end_date = add_days(from_date, 6)
			else:
				period_end_date = add_to_date(from_date, months=increment, days=-1)

			if period_end_date > to_date:
				period_end_date = to_date

			self.periodic_daterange.append(period_end_date)

			from_date = add_days(period_end_date, 1)
			if period_end_date == to_date:
				break

	def get_groups(self):
		if self.filters.tree_type == "Territory":
			parent = "parent_territory"
		if self.filters.tree_type == "Customer Group":
			parent = "parent_customer_group"
		if self.filters.tree_type == "Item Group":
			parent = "parent_item_group"
		if self.filters.tree_type == "Supplier Group":
			parent = "parent_supplier_group"

		self.depth_map = frappe._dict()

		self.group_entries = frappe.db.sql(
			f"""select name, lft, rgt , {parent} as parent
			from `tab{self.filters.tree_type}` order by lft""",
			as_dict=1,
		)

		for d in self.group_entries:
			if d.parent:
				self.depth_map.setdefault(d.name, self.depth_map.get(d.parent) + 1)
			else:
				self.depth_map.setdefault(d.name, 0)

	def get_teams(self):
		self.depth_map = frappe._dict()

		self.group_entries = frappe.db.sql(
			f""" select * from (select "Order Types" as name, 0 as lft,
			2 as rgt, '' as parent union select distinct order_type as name, 1 as lft, 1 as rgt, "Order Types" as parent
			from `tab{self.filters.doc_type}` where ifnull(order_type, '') != '') as b order by lft, name
		""",
			as_dict=1,
		)

		for d in self.group_entries:
			if d.parent:
				self.depth_map.setdefault(d.name, self.depth_map.get(d.parent) + 1)
			else:
				self.depth_map.setdefault(d.name, 0)

	def get_supplier_parent_child_map(self):
		self.parent_child_map = frappe._dict(
			frappe.db.sql(""" select name, supplier_group from `tabSupplier`""")
		)