"""
Sales Prediction Model
Machine learning module for predicting stock needs based on historical order data.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import json

def prepare_data(orders_df):
    """
    Prepare order data for machine learning model.
    
    Args:
        orders_df: DataFrame containing order data with line_items column
        
    Returns:
        DataFrame with aggregated product sales statistics
    """
    # Parse line_items JSON safely
    orders_df['line_items'] = orders_df['line_items'].apply(json.loads)
    
    # Extract product details from line items
    product_data = []
    for _, order in orders_df.iterrows():
        for item in order['line_items']:
            product_data.append({
                'product_id': item['product_id'],
                'quantity': item['quantity']
            })
    
    # Convert to DataFrame
    product_df = pd.DataFrame(product_data)
    
    # Group orders by product, calculate total quantity
    product_sales = product_df.groupby('product_id')['quantity'].sum().reset_index()
    
    # Add features like average order size, sales frequency
    product_sales['avg_order_size'] = product_df.groupby('product_id')['quantity'].mean()
    product_sales['order_frequency'] = product_df.groupby('product_id').size()
    
    return product_sales

def train_stock_prediction_model(data):
    """
    Train a Random Forest model to predict stock needs.
    
    Args:
        data: DataFrame with product sales features
        
    Returns:
        Trained RandomForestRegressor model
    """
    X = data[['avg_order_size', 'order_frequency']]
    y = data['quantity']
    
    # Split and scale data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # Train Random Forest model
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X_train_scaled, y_train)
    
    # Save model and scaler
    joblib.dump(model, 'stock_prediction_model.pkl')
    joblib.dump(scaler, 'stock_scaler.pkl')
    
    return model

def predict_stock_needs(new_data):
    """
    Predict stock needs for products using trained model.
    
    Args:
        new_data: DataFrame with product features
        
    Returns:
        Dictionary mapping product IDs to prediction details
    """
    model = joblib.load('stock_prediction_model.pkl')
    scaler = joblib.load('stock_scaler.pkl')
    
    # Scale new data
    new_data_scaled = scaler.transform(new_data)
    
    # Predict stock needs with confidence
    predictions = model.predict(new_data_scaled)
    confidence = model.score(new_data_scaled, new_data['quantity'])
    
    # Create detailed predictions dictionary
    stock_predictions = {}
    for idx, (product_id, avg_quantity, pred_stock) in enumerate(zip(
        new_data.index, 
        new_data['avg_order_size'], 
        predictions
    )):
        stock_predictions[product_id] = {
            'avg_quantity': avg_quantity,
            'predicted_stock': pred_stock,
            'confidence': confidence
        }
    
    return stock_predictions

def main(orders_file):
    """
    Main function to generate sales predictions from order history.
    
    Args:
        orders_file: Path to CSV file containing order data
        
    Returns:
        Dictionary mapping product IDs to prediction details including:
        - total_quantity: Total quantity ordered historically
        - avg_quantity: Average quantity per order
        - predicted_stock: Recommended stock level (1.5x average)
    """
    try:
        orders_df = pd.read_csv(orders_file)
        
        # Parse line_items safely
        orders_df['line_items'] = orders_df['line_items'].apply(json.loads)
        
        # Extract product details
        product_data = []
        for _, order in orders_df.iterrows():
            for item in order['line_items']:
                product_data.append({
                    'product_id': item['product_id'],
                    'quantity': item['quantity']
                })
        
        # Convert to DataFrame
        product_df = pd.DataFrame(product_data)
        
        # Group and calculate statistics
        product_sales = product_df.groupby('product_id').agg({
            'quantity': ['sum', 'mean', 'count']
        }).reset_index()
        product_sales.columns = ['product_id', 'total_quantity', 'avg_quantity', 'order_frequency']
        
        # Predict stock needs
        predictions = {}
        for _, row in product_sales.iterrows():
            predictions[row['product_id']] = {
                'total_quantity': row['total_quantity'],
                'avg_quantity': row['avg_quantity'],
                'predicted_stock': int(row['avg_quantity'] * 1.5)  # 50% buffer over average
            }
        
        return predictions
    
    except Exception as e:
        print(f"Error in prediction: {e}")
        import traceback
        traceback.print_exc()
        return {}
