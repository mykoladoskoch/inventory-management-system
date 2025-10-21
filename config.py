"""
Configuration management for the Small Business Inventory Management System.
Loads environment variables and provides configuration settings.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class."""
    
    # Flask configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_ENV', 'production') == 'development'
    
    # Database configuration
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATABASE_PATH = os.getenv('DATABASE_PATH', os.path.join(BASE_DIR, 'data', 'inventory.db'))
    
    # Upload configuration
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploaded_files')
    TEMP_FOLDER = os.path.join(BASE_DIR, 'temp')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'csv'}
    
    # Model configuration
    MODEL_PATH = os.path.join(BASE_DIR, 'stock_prediction_model.pkl')
    SCALER_PATH = os.path.join(BASE_DIR, 'stock_scaler.pkl')
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration."""
        # Create necessary directories
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.TEMP_FOLDER, exist_ok=True)
        os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
