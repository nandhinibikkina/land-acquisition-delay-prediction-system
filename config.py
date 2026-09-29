import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sih-land-acquisition-secret-key-2026'
    
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'database.db')
    
    REGRESSOR_MODEL_PATH = os.path.join(BASE_DIR, 'ml', 'models', 'delay_regressor.pkl')
    CLASSIFIER_MODEL_PATH = os.path.join(BASE_DIR, 'ml', 'models', 'risk_classifier.pkl')
    
    HISTORICAL_DATA_PATH = os.path.join(BASE_DIR, 'data', 'historical_cases.csv')
    SAMPLE_DATA_PATH = os.path.join(BASE_DIR, 'data', 'sample_cases.csv')
    
    # Prototype Auth Credentials
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'
