import frappe
from frappe import _

def execute(filters=None):
	if not filters:
		filters = {}
	
	columns = get_columns()
	data = get_data(filters)
	
	return columns, data

def get_columns():
	return [
		{
			"fieldname": "sales_person",
			"label": _("Sales Person"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "item_code",
			"label": _("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"width": 150
		},
		{
			"fieldname": "item_name",
			"label": _("Item Name"),
			"fieldtype": "Data",
			"width": 300
		},
		{
			"fieldname": "total_qty",
			"label": _("Total Quantity"),
			"fieldtype": "Float",
			"width": 120
		}
	]

def get_data(filters):
	conditions = get_conditions(filters)
	
	query = """
		SELECT 
			se.adist_sales_person as sales_person,
			sed.item_code, 
			sed.item_name, 
			SUM(sed.qty) AS total_qty
		FROM 
			`tabStock Entry` se
		JOIN 
			`tabStock Entry Detail` sed ON se.name = sed.parent
		WHERE 
			se.docstatus = 1
			AND se.stock_entry_type = 'Material Issue'
			{conditions}
		GROUP BY 
			se.adist_sales_person, sed.item_code, sed.item_name
		ORDER BY 
			se.adist_sales_person, sed.item_code
	""".format(conditions=conditions)
	
	raw_data = frappe.db.sql(query, filters, as_dict=True)
	
	if not raw_data:
		return []
	
	# Group data by sales person
	grouped_data = {}
	for row in raw_data:
		sales_person = row.get('sales_person') or _('No Sales Person')
		if sales_person not in grouped_data:
			grouped_data[sales_person] = []
		grouped_data[sales_person].append(row)
	
	# Format data for display
	formatted_data = []
	
	for sales_person, items in grouped_data.items():
		# Add sales person header
		formatted_data.append({
			'sales_person': sales_person,
			'item_code': '',
			'item_name': '',
			'total_qty': None,
			'indent': 0,
			'is_header': True
		})
		
		# Add items under sales person
		total_qty_for_person = 0
		for item in items:
			formatted_data.append({
				'sales_person': '',
				'item_code': item.get('item_code'),
				'item_name': item.get('item_name'),
				'total_qty': item.get('total_qty', 0),
				'indent': 1
			})
			total_qty_for_person += item.get('total_qty', 0)
		
		# Add total for sales person
		formatted_data.append({
			'sales_person': '',
			'item_code': '',
			'item_name': _('Total for {0}').format(sales_person),
			'total_qty': total_qty_for_person,
			'indent': 1,
			'is_total': True
		})
	
	return formatted_data

def get_conditions(filters):
	conditions = []
	
	if filters.get("from_date"):
		conditions.append("se.posting_date >= %(from_date)s")
	
	if filters.get("to_date"):
		conditions.append("se.posting_date <= %(to_date)s")
	
	if filters.get("sales_person"):
		conditions.append("se.adist_sales_person = %(sales_person)s")
	
	return " AND " + " AND ".join(conditions) if conditions else ""