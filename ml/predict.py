import os
import sys

# Ensure root directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
import joblib
from config import Config

_regressor_model = None
_classifier_model = None

def load_models():
    global _regressor_model, _classifier_model
    if _regressor_model is None:
        if os.path.exists(Config.REGRESSOR_MODEL_PATH):
            _regressor_model = joblib.load(Config.REGRESSOR_MODEL_PATH)
        else:
            raise FileNotFoundError(f"Regressor model file not found at {Config.REGRESSOR_MODEL_PATH}")
            
    if _classifier_model is None:
        if os.path.exists(Config.CLASSIFIER_MODEL_PATH):
            _classifier_model = joblib.load(Config.CLASSIFIER_MODEL_PATH)
        else:
            raise FileNotFoundError(f"Classifier model file not found at {Config.CLASSIFIER_MODEL_PATH}")
            
    return _regressor_model, _classifier_model

def predict_case(case_dict):
    regressor, classifier = load_models()
    
    expected_cols = [
        'district', 'land_type', 'acquisition_purpose', 'current_stage',
        'documents_complete', 'owner_verified', 'compensation_status',
        'legal_dispute', 'approval_status', 'land_area', 'days_pending'
    ]
    
    input_data = {
        'district': str(case_dict.get('district', 'East Godavari')),
        'land_type': str(case_dict.get('land_type', 'Agricultural')),
        'acquisition_purpose': str(case_dict.get('acquisition_purpose', 'Highway Expansion')),
        'current_stage': str(case_dict.get('current_stage', 'Land Identification')),
        'documents_complete': str(case_dict.get('documents_complete', 'No')),
        'owner_verified': str(case_dict.get('owner_verified', 'No')),
        'compensation_status': str(case_dict.get('compensation_status', 'Pending')),
        'legal_dispute': str(case_dict.get('legal_dispute', 'No')),
        'approval_status': str(case_dict.get('approval_status', 'Pending')),
        'land_area': float(case_dict.get('land_area', 1.0)),
        'days_pending': int(case_dict.get('days_pending', 0))
    }
    
    df_input = pd.DataFrame([input_data])[expected_cols]
    
    # 1. Regressor Prediction
    predicted_days_raw = regressor.predict(df_input)[0]
    predicted_remaining_days = int(max(1, round(predicted_days_raw)))
    
    # 2. Classifier Prediction
    prob_classes = classifier.predict_proba(df_input)[0]
    # Classifier target '1' represents delayed
    delay_prob = float(prob_classes[1]) if len(prob_classes) > 1 else float(prob_classes[0])
    risk_probability_pct = round(delay_prob * 100, 1)
    
    # Rule-assisted risk classification adjustment
    if risk_probability_pct >= 65.0 or input_data['legal_dispute'] == 'Yes' or predicted_remaining_days > 85:
        risk_level = 'HIGH'
    elif risk_probability_pct >= 35.0 or predicted_remaining_days > 45 or input_data['documents_complete'] == 'No':
        risk_level = 'MEDIUM'
    else:
        risk_level = 'LOW'
        
    return {
        'predicted_remaining_days': predicted_remaining_days,
        'risk_level': risk_level,
        'risk_probability': risk_probability_pct
    }

if __name__ == '__main__':
    sample_input = {
        'district': 'East Godavari',
        'land_area': 12.5,
        'land_type': 'Agricultural',
        'acquisition_purpose': 'Highway Expansion',
        'current_stage': 'Compensation',
        'days_pending': 45,
        'documents_complete': 'Yes',
        'owner_verified': 'Yes',
        'compensation_status': 'Pending',
        'legal_dispute': 'No',
        'approval_status': 'Pending'
    }
    
    res = predict_case(sample_input)
    print("Sample Case Prediction Test:")
    print("Input:", sample_input)
    print("Output:", res)
