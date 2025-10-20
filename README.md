# Small Business Inventory Management System

A Flask-based web application for managing inventory, processing orders, and predicting sales trends using machine learning.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

- **Inventory Management** - Track products with real-time stock level monitoring
- **Order Processing** - Upload and process customer orders with automatic stock deduction
- **Sales Predictions** - ML-powered forecasting using Random Forest algorithm
- **Bulk Import** - CSV file upload support for products and orders
- **Visual Alerts** - Color-coded stock indicators (red: out of stock, yellow: low, green: sufficient)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/small-business-system.git
cd small-business-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your secret key

# Initialize database
python data/init_db.py

# Run application
python app.py
```

Visit `http://localhost:5000` in your browser.

## Usage

### Product Management
Upload a CSV file with columns: `ProductID`, `ProductName`, `Price`, `Stock`

### Order Management
Upload a CSV file with columns: `order_id`, `order_date`, `customer_email`, `total_amount`, `status`, `line_items`

Line items must be in JSON format:
```json
[{"product_id": 1, "name": "Product", "quantity": 2, "price": 19.99}]
```

### Sales Predictions
Upload historical order data to receive AI-powered stock recommendations based on purchase patterns.

## Tech Stack

- **Backend:** Flask, SQLite
- **Frontend:** Bootstrap 5, jQuery
- **ML:** scikit-learn (Random Forest)
- **Data Processing:** pandas, numpy

## Project Structure

```
├── app.py              # Main Flask application
├── model.py            # ML prediction model
├── config.py           # Configuration management
├── data/
│   └── init_db.py      # Database initialization
├── templates/          # HTML templates
└── sample_data/        # Example CSV files
```

## Configuration

Create a `.env` file:

```env
FLASK_SECRET_KEY=your-secret-key-here
FLASK_ENV=development
DATABASE_PATH=data/inventory.db
```

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Author

Created and maintained by [Mykola]

## Acknowledgments

Built with Flask, Bootstrap, and scikit-learn.
