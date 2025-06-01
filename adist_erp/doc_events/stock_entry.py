import frappe


def create_material_receipt(doc, method):
    if not doc.stock_entry_type=="Material Issue":
        return
    
    replacement_settings= frappe.get_doc("Warranty Replacement Settings")
    if bool(replacement_settings.auto_create_bad_stock_return)== False:
        return
    good_warehouse=replacement_settings.good_stock_issue_warehouse
    bad_warehouse=replacement_settings.bad_stock_receipt_warehouse
    converted_items_array=[]
    for item in doc.items:
        converted_items={
          "item_code":item.item_code,
          "qty":item.qty,
          "t_warehouse":bad_warehouse,
          "actual_qty":item.actual_qty,
          "amount":item.amount,
          "basic_amount":item.basic_amount,
          "basic_rate":item.basic_rate     
      }
        converted_items_array.append(converted_items)
    
    new_material_receipt_doc=frappe.get_doc(
        {
            'doctype':'Stock Entry',
            "stock_entry_type":"Material Receipt",
            "items":converted_items_array,
            "adist_sales_person":doc.adist_sales_person,
            "adist_customer":doc.adist_customer,
            
            
        }
    )
    new_material_receipt_doc.insert()
    new_material_receipt_doc.submit()
    