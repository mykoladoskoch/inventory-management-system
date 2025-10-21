# Sample Data Files

This directory contains sample CSV files to help you get started with the Small Business Inventory Management System.

## Files

### sample_products.csv
Example product inventory data with 10 sample products including:
- Electronics (laptops, monitors, peripherals)
- Office supplies (chairs, lamps)
- Accessories (cables, headphones)

**Format:**
```csv
ProductID,ProductName,Price,Stock
1,Laptop Computer,899.99,50
```

**Columns:**
- `ProductID`: Unique identifier for the product (integer)
- `ProductName`: Name of the product (text)
- `Price`: Product price (decimal)
- `Stock`: Current stock level (integer)

### sample_orders.csv
Example order data with 10 sample orders demonstrating various scenarios.

**Format:**
```csv
order_id,order_date,customer_email,total_amount,status,line_items
1,2025-01-15,john.doe@example.com,924.98,pending,"[{""product_id"": 1, ""name"": ""Laptop Computer"", ""quantity"": 1, ""price"": 899.99}]"
```

**Columns:**
- `order_id`: Unique order identifier (integer)
- `order_date`: Date of order in YYYY-MM-DD format
- `customer_email`: Customer's email address
- `total_amount`: Total order amount (decimal)
- `status`: Order status (pending/completed)
- `line_items`: JSON array of ordered items

**Line Items Format:**
Each line item is a JSON object with:
- `product_id`: ID of the product
- `name`: Product name
- `quantity`: Quantity ordered
- `price`: Price per unit

## Usage

### Loading Sample Products

1. Navigate to the main application page
2. Click "Choose File" under "Manage Inventory"
3. Select `sample_products.csv`
4. Click "Upload Inventory"

### Loading Sample Orders

1. Navigate to the Orders page
2. Click "Choose File" under order upload section
3. Select `sample_orders.csv`
4. Click "Upload Orders"

### Testing Sales Predictions

1. Navigate to Sales Predictions page
2. Upload `sample_orders.csv`
3. View predicted stock needs based on order history

## Creating Your Own Data Files

### Product CSV Requirements
- Must include columns: `ProductID`, `ProductName`, `Price`, `Stock`
- Column names are case-insensitive but must match exactly
- ProductID must be unique
- Price and Stock must be numeric values

### Order CSV Requirements
- Must include columns: `order_id`, `order_date`, `customer_email`, `total_amount`, `status`, `line_items`
- `line_items` must be valid JSON format
- Use double quotes for JSON strings
- Escape quotes in CSV properly

### Example Line Items JSON
```json
[
  {
    "product_id": 1,
    "name": "Product Name",
    "quantity": 2,
    "price": 19.99
  }
]
```

## Tips

- Start with sample data to understand the system
- Modify sample files to match your business needs
- Keep backups of your data files
- Test with small datasets first
- Validate JSON format before uploading orders

## Troubleshooting

**Upload fails:**
- Check column names match exactly
- Verify CSV format is correct
- Ensure no special characters in data
- Validate JSON in line_items

**Data not appearing:**
- Refresh the page
- Check for error messages
- Verify file was uploaded successfully
- Check database was initialized

For more help, see the main [README.md](../README.md) or open an issue on GitHub.
