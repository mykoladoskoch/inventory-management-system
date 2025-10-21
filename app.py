"""
Small Business Inventory Management System
A Flask web application for managing inventory, orders, and sales predictions.
"""
import json
import os
from flask import Flask, flash, render_template, request, redirect, url_for
import pandas as pd
import sqlite3
import traceback
from contextlib import contextmanager
from config import Config
from model import main

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

# Database path from configuration
DB_PATH = app.config['DATABASE_PATH']

@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Ensures proper connection handling and automatic cleanup.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        yield conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

@app.route('/')
def index():
    """
    Display the main inventory dashboard with products and orders.
    Shows color-coded stock levels and provides search/sort functionality.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Fetch product data
        cursor.execute("SELECT * FROM products")
        product_data = cursor.fetchall()

        # Process product data
        if product_data:
            product_df = pd.DataFrame(product_data, columns=['product_id', 'name', 'price', 'stock_level'])

            # Add a style column for stock level based on conditions
            def get_row_style(stock_level):
                if stock_level <= 0:
                    return "table-danger"  # Red for negative stock
                elif stock_level < 100:
                    return "table-warning"  # Yellow for stock < 100
                return "table-success"  # green if stock is sufficient

            product_df['row_style'] = product_df['stock_level'].apply(get_row_style)
            product_table = product_df.to_dict(orient='records')  # Convert to list of dicts
        else:
            product_table = []  # Empty list if no products

        # Fetch order data
        cursor.execute("SELECT * FROM orders")
        order_data = cursor.fetchall()

        # Process order data
        if order_data:
            order_df = pd.DataFrame(order_data, columns=['order_id', 'product_id', 'quantity', 'order_date', 'customer_name', 'customer_address'])
            order_table = order_df.to_dict(orient='records')  # Convert to list of dicts
        else:
            order_table = []  # Empty list if no orders

        # Pass the processed data to the template
        return render_template('index.html', product_table=product_table, order_table=order_table)



@app.route('/orders')
def orders_page():
    """
    Display the orders management page.
    Shows all orders with their line items and status.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

        cursor.execute("SELECT order_id, order_date, customer_email, total_amount, status, line_items FROM orders")
        order_data = cursor.fetchall()

        order_table = []
        for row in order_data:
            try:
                # Parse the line_items into a Python object
                line_items = json.loads(row[5])
            except json.JSONDecodeError:
                line_items = []

            # Escape the JSON string for HTML
            escaped_line_items = json.dumps(line_items).replace("'", "&#39;").replace('"', '&quot;')

            order_table.append({
                'order_id': row[0],
                'order_date': row[1],
                'customer_email': row[2],
                'total_amount': row[3],
                'status': row[4],
                'line_items': escaped_line_items  # Escape JSON string
            })

            return render_template('orders.html', order_table=order_table)

    except Exception as e:
        print(f"Error in orders_page route: {e}")
        return f"An error occurred: {e}", 500




@app.route('/upload_inventory', methods=['POST'])
def upload_inventory():
    """
    Handle CSV file upload for product inventory.
    Validates and imports product data into the database.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        if 'file' not in request.files:
            return "No file selected!", 400

        file = request.files['file']
        if file.filename.strip() == '':
            return "No file selected!", 400

        # Detect file type based on extension
        file_extension = os.path.splitext(file.filename)[1].lower()

        if file_extension == '.csv':
            try:
                # Read the CSV file into a DataFrame
                data = pd.read_csv(file)
            except Exception as e:
                return f"Error reading CSV file: {str(e)}", 500
        else:
            return "Unsupported file format! Please upload a CSV file.", 400

        # Edit names in the DataFrame
        data.columns = data.columns.str.strip().str.lower()

        # Ensure the required columns exist
        required_columns = {'productid', 'productname', 'price', 'stock'}
        if not required_columns.issubset(data.columns):
            print("Detected columns:", data.columns.tolist())  # Debugging
            return f"File must contain the following columns: {', '.join(required_columns)}", 400

        # Insert data into the database
        cursor.execute("DELETE FROM products")

        # Insert new data into the table
        for _, row in data.iterrows():
            cursor.execute('''
                INSERT INTO products (product_id, name, price, stock_level)
                VALUES (?, ?, ?, ?)
            ''', (row['productid'], row['productname'], row['price'], row['stock']))

        conn.commit()
        flash("Inventory uploaded successfully!", "success")
        return redirect(url_for('index'))

@app.route('/upload_orders', methods=['POST'])
def upload_orders():
    """
    Handle CSV file upload for orders.
    Validates JSON format and imports order data.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        if 'file' not in request.files:
            return "No file selected!", 400

        file = request.files['file']
        if file.filename.strip() == '':
            return "No file selected!", 400

        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension != '.csv':
            return "Unsupported file format! Please upload a CSV file.", 400

        try:
            data = pd.read_csv(file)
        except Exception as e:
            return f"Error reading CSV file: {str(e)}", 500

        required_columns = {'order_id', 'order_date', 'customer_email', 'total_amount', 'status', 'line_items'}
        if not required_columns.issubset(data.columns.str.lower()):
            return f"File must contain the following columns: {', '.join(required_columns)}", 400

        for _, row in data.iterrows():
            # Validate row data
            if not all([row['order_id'], row['order_date'], row['customer_email'], row['total_amount'], row['status'], row['line_items']]):
                flash(f"Missing required fields in order ID {row['order_id']}. Skipping.", "danger")
                continue

            try:
                json.loads(row['line_items'])  # Validate JSON
            except json.JSONDecodeError:
                flash(f"Invalid JSON in line_items for order ID {row['order_id']}. Skipping.", "danger")
                continue

            # Check for duplicate order_id
            cursor.execute("SELECT 1 FROM orders WHERE order_id = ?", (row['order_id'],))
            if cursor.fetchone():
                flash(f"Order ID {row['order_id']} already exists. Skipping.", "warning")
                continue

            # Insert the order
            try:
                cursor.execute('''
                    INSERT INTO orders (order_id, order_date, customer_email, total_amount, status, line_items)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (row['order_id'], row['order_date'], row['customer_email'],
                      row['total_amount'], row['status'], row['line_items']))
            except sqlite3.IntegrityError as e:
                flash(f"Integrity error for order ID {row['order_id']}: {e}", "danger")
                continue
            except Exception as e:
                flash(f"Error inserting order ID {row['order_id']}: {e}", "danger")
                continue

        conn.commit()
        flash("Orders uploaded successfully!", "success")
        return redirect(url_for('orders_page'))


@app.route('/process_orders', methods=['POST'])
def process_orders():
    """
    Process pending orders by deducting stock levels.
    Marks orders as completed after processing.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM orders WHERE status != 'completed'")
        orders = cursor.fetchall()

        for order in orders:
            order_id, order_date, customer_email, total_amount, status, line_items = order
            try:
                items = json.loads(line_items)  # Safe JSON parsing
            except json.JSONDecodeError:
                flash(f"Invalid JSON in order {order_id}. Skipping.", "danger")
                continue

            for item in items:
                product_id = item['product_id']
                quantity = item['quantity']

                # Deduct stock (even if stock goes negative)
                cursor.execute('''
                    UPDATE products
                    SET stock_level = stock_level - ?
                    WHERE product_id = ?
                ''', (quantity, product_id))

                # If the product does not exist, add it to the products table
                cursor.execute('SELECT stock_level FROM products WHERE product_id = ?', (product_id,))
                if cursor.fetchone() is None:
                    cursor.execute('''
                        INSERT INTO products (product_id, name, price, stock_level)
                        VALUES (?, ?, ?, ?)
                    ''', (product_id, item['name'], item['price'], -quantity))

            # Mark the order as completed
            cursor.execute('''
                UPDATE orders
                SET status = 'completed'
                WHERE order_id = ?
            ''', (order_id,))

        conn.commit()
        flash("Orders processed successfully!", "success")
        return redirect(url_for('orders_page'))


    

@app.route('/clear_orders', methods=['POST'])
def clear_orders():
    """Clear all orders from the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders")
        conn.commit()
        flash("Orders have been cleared successfully!", "success")
        return redirect(url_for('orders_page'))

@app.route('/add_product', methods=['POST'])
def add_product():
    """Add a new product to the inventory."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get form data
        product_name = request.form.get('product_name')
        price = request.form.get('price')
        stock_level = request.form.get('stock_level')

        # Validate input
        if not all([product_name, price, stock_level]):
            flash("All fields are required!", "danger")
            return redirect(url_for('index'))

        try:
            price = float(price)
            stock_level = int(stock_level)
        except ValueError:
            flash("Invalid price or stock level format!", "danger")
            return redirect(url_for('index'))

        # Check if product already exists
        cursor.execute("SELECT * FROM products WHERE name = ?", (product_name,))
        existing_product = cursor.fetchone()

        if existing_product:
            flash(f"Product '{product_name}' already exists!", "warning")
            return redirect(url_for('index'))

        # Insert new product
        cursor.execute('''
            INSERT INTO products (name, price, stock_level)
            VALUES (?, ?, ?)
        ''', (product_name, price, stock_level))

        conn.commit()
        flash(f"Product '{product_name}' added successfully!", "success")
        return redirect(url_for('index'))

@app.route('/remove_product', methods=['POST'])
def remove_product():
    """Remove a product and its related orders from the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get product ID to remove
        product_id = request.form.get('product_id')

        # Validate input
        if not product_id:
            flash("Product ID is required!", "danger")
            return redirect(url_for('index'))

        try:
            product_id = int(product_id)
        except ValueError:
            flash("Invalid product ID format!", "danger")
            return redirect(url_for('index'))

        # Check if product exists
        cursor.execute("SELECT name FROM products WHERE product_id = ?", (product_id,))
        product = cursor.fetchone()

        if not product:
            flash(f"No product found with ID {product_id}!", "warning")
            return redirect(url_for('index'))

        # Remove the product
        cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
        
        cursor.execute("SELECT order_id, line_items FROM orders")
        orders = cursor.fetchall()
        
        for order_id, line_items in orders:
            try:
                # Safe JSON parsing
                items = json.loads(line_items)
                
                # Check if any item in the order matches the product
                if any(item.get('product_id') == product_id for item in items):
                    cursor.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
            except (json.JSONDecodeError, Exception) as e:
                print(f"Error processing order {order_id}: {e}")

        conn.commit()
        flash(f"Product '{product[0]}' and related orders removed successfully!", "success")
        return redirect(url_for('index'))

@app.route('/update_product', methods=['POST'])
def update_product():
    """Update an existing product's details."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get form data
        product_id = request.form.get('product_id')
        product_name = request.form.get('product_name')
        price = request.form.get('price')
        stock_level = request.form.get('stock_level')

        # Validate input
        if not all([product_id, product_name, price, stock_level]):
            flash("All fields are required!", "danger")
            return redirect(url_for('index'))

        try:
            product_id = int(product_id)
            price = float(price)
            stock_level = int(stock_level)
        except ValueError:
            flash("Invalid input format!", "danger")
            return redirect(url_for('index'))

        # Check if product exists
        cursor.execute("SELECT name FROM products WHERE product_id = ?", (product_id,))
        product = cursor.fetchone()

        if not product:
            flash(f"No product found with ID {product_id}!", "warning")
            return redirect(url_for('index'))

        # Update the product
        cursor.execute('''
            UPDATE products
            SET name = ?, price = ?, stock_level = ?
            WHERE product_id = ?
        ''', (product_name, price, stock_level, product_id))

        conn.commit()
        flash(f"Product '{product_name}' updated successfully!", "success")
        return redirect(url_for('index'))

@app.route('/update_order', methods=['POST'])
def update_order():
    """Update an existing order's details."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get form data
        order_id = request.form.get('order_id')
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')
        order_date = request.form.get('order_date')
        customer_name = request.form.get('customer_name')
        customer_address = request.form.get('customer_address')

        # Validate input
        if not all([order_id, product_id, quantity, order_date, customer_name, customer_address]):
            flash("All fields are required to update the order!", "danger")
            return redirect(url_for('orders_page'))

        try:
            order_id = int(order_id)
            product_id = int(product_id)
            quantity = int(quantity)
        except ValueError:
            flash("Invalid format for numeric fields!", "danger")
            return redirect(url_for('orders_page'))

        # Check if the order exists
        cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        existing_order = cursor.fetchone()

        if not existing_order:
            flash(f"No order found with ID {order_id}!", "warning")
            return redirect(url_for('orders_page'))

        # Update the order
        cursor.execute('''
            UPDATE orders
            SET product_id = ?, quantity = ?, order_date = ?, customer_name = ?, customer_address = ?
            WHERE order_id = ?
        ''', (product_id, quantity, order_date, customer_name, customer_address, order_id))

        conn.commit()
        flash(f"Order ID {order_id} updated successfully!", "success")
        return redirect(url_for('orders_page'))

@app.route('/remove_order', methods=['POST'])
def remove_order():
    """Remove an order from the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get the order ID from the form
        order_id = request.form.get('order_id')

        # Validate input
        if not order_id:
            flash("Order ID is required!", "danger")
            return redirect(url_for('orders_page'))

        try:
            order_id = int(order_id)
        except ValueError:
            flash("Invalid Order ID format!", "danger")
            return redirect(url_for('orders_page'))

        # Check if the order exists
        cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        existing_order = cursor.fetchone()

        if not existing_order:
            flash(f"No order found with ID {order_id}!", "warning")
            return redirect(url_for('orders_page'))

        # Remove the order
        cursor.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
        conn.commit()

        flash(f"Order ID {order_id} removed successfully!", "success")
        return redirect(url_for('orders_page'))

@app.route('/add_order', methods=['POST'])
def add_order():
    """Add a new order to the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get form data
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')
        order_date = request.form.get('order_date')
        customer_name = request.form.get('customer_name')
        customer_address = request.form.get('customer_address')

        # Validate input
        if not all([product_id, quantity, order_date, customer_name, customer_address]):
            flash("All fields are required to add an order!", "danger")
            return redirect(url_for('orders_page'))

        try:
            product_id = int(product_id)
            quantity = int(quantity)
        except ValueError:
            flash("Invalid format for numeric fields!", "danger")
            return redirect(url_for('orders_page'))

        # Check if the product exists
        cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
        existing_product = cursor.fetchone()

        if not existing_product:
            flash(f"No product found with ID {product_id}!", "warning")
            return redirect(url_for('orders_page'))

        # Insert the new order
        cursor.execute('''
            INSERT INTO orders (product_id, quantity, order_date, customer_name, customer_address)
            VALUES (?, ?, ?, ?, ?)
        ''', (product_id, quantity, order_date, customer_name, customer_address))

        conn.commit()
        flash("Order added successfully!", "success")
        return redirect(url_for('orders_page'))
            

@app.route('/sales_predictions', methods=['GET', 'POST'])
def sales_predictions():
    """
    Display sales predictions page.
    Accepts order file upload and generates stock predictions using ML.
    """
    if request.method == 'POST':
        if 'order_file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['order_file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        # Create temp directory if it doesn't exist
        os.makedirs('temp', exist_ok=True)
        
        # Save temporarily
        file_path = os.path.join('temp', file.filename)
        file.save(file_path)
        
        try:
            predictions = main(file_path)
            return render_template('sales_predictions.html', predictions=predictions)
        except Exception as e:
            # Print full traceback for debugging
            traceback.print_exc()
            flash(f'Prediction error: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template('sales_predictions.html')

if __name__ == "__main__":
    app.run(debug=True)
