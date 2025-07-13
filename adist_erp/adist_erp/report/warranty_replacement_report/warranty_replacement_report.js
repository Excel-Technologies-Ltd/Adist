frappe.query_reports["Warranty Replacement Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1,
			"width": "80px"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "80px"
		},
		{
			"fieldname": "sales_person",
			"label": __("Sales Person"),
			"fieldtype": "Link",
			"options": "Sales Person",
			"width": "100px"
		}
	],
	
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		// Format sales person headers
		if (data && data.is_header) {
			if (column.fieldname === 'sales_person') {
				value = `<span style='font-weight: bold; color: #28a745; font-size: 14px;'>${value}</span>`;
			} else if (column.fieldname === 'total_qty') {
				value = ''; // Hide total_qty for headers
			}
		}
		
		// Format total rows
		if (data && data.is_total) {
			if (column.fieldname === 'item_name') {
				value = `<span style='font-weight: bold; color: #333;'>${value}</span>`;
			}
			if (column.fieldname === 'total_qty') {
				value = `<span style='font-weight: bold; color: #333;'>${value}</span>`;
			}
		}
		
		return value;
	}
};