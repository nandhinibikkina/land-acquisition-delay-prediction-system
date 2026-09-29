import os
import sys

# Ensure root directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score, classification_report

from config import Config

def train():
    print("Loading historical dataset...")
    if not os.path.exists(Config.HISTORICAL_DATA_PATH):
        raise FileNotFoundError(f"Historical data file not found at {Config.HISTORICAL_DATA_PATH}. Run generate_dataset.py first.")
        
    df = pd.read_csv(Config.HISTORICAL_DATA_PATH)
    
    categorical_features = [
        'district', 'land_type', 'acquisition_purpose', 'current_stage',
        'documents_complete', 'owner_verified', 'compensation_status',
        'legal_dispute', 'approval_status'
    ]
    
    numerical_features = ['land_area', 'days_pending']
    
    X = df[categorical_features + numerical_features]
    y_reg = df['actual_remaining_days']
    y_cls = df['delayed']
    
    # Preprocessor pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features),
            ('num', StandardScaler(), numerical_features)
        ]
    )
    
    # Train/Test Split
    X_train, X_test, y_reg_train, y_reg_test, y_cls_train, y_cls_test = train_test_split(
        X, y_reg, y_cls, test_size=0.2, random_state=42
    )
    
    # MODEL 1: RandomForestRegressor
    print("\n--- Training Model 1: RandomForestRegressor (Estimated Remaining Days) ---")
    regressor_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42))
    ])
    
    regressor_pipeline.fit(X_train, y_reg_train)
    y_reg_pred = regressor_pipeline.predict(X_test)
    
    mae = mean_absolute_error(y_reg_test, y_reg_pred)
    r2 = r2_score(y_reg_test, y_reg_pred)
    
    print(f"Regression Performance:")
    print(f"Mean Absolute Error (MAE): {mae:.2f} days")
    print(f"R² Score: {r2:.4f}")
    
    # MODEL 2: RandomForestClassifier
    print("\n--- Training Model 2: RandomForestClassifier (Predicted Delay Risk) ---")
    classifier_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42))
    ])
    
    classifier_pipeline.fit(X_train, y_cls_train)
    y_cls_pred = classifier_pipeline.predict(X_test)
    
    acc = accuracy_score(y_cls_test, y_cls_pred)
    report = classification_report(y_cls_test, y_cls_pred)
    
    print(f"Classification Performance:")
    print(f"Accuracy: {acc * 100:.2f}%")
    print("Classification Report:\n", report)
    
    # Save models
    os.makedirs(os.path.dirname(Config.REGRESSOR_MODEL_PATH), exist_ok=True)
    
    joblib.dump(regressor_pipeline, Config.REGRESSOR_MODEL_PATH)
    print(f"Saved regressor model to {Config.REGRESSOR_MODEL_PATH}")
    
    joblib.dump(classifier_pipeline, Config.CLASSIFIER_MODEL_PATH)
    print(f"Saved classifier model to {Config.CLASSIFIER_MODEL_PATH}")

if __name__ == '__main__':
    train()
