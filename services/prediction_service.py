import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.predict import predict_case
from services.risk_analysis import analyze_risk_factors

def get_full_case_prediction(case_data):
    """
    Combines ML predictions (regressor & classifier) with explainable risk analysis
    to return a complete decision support prediction package.
    """
    # 1. ML predictions
    ml_res = predict_case(case_data)
    
    # 2. Risk Indicators & Actions
    risk_res = analyze_risk_factors(case_data)
    
    return {
        'predicted_remaining_days': ml_res['predicted_remaining_days'],
        'risk_level': ml_res['risk_level'],
        'risk_probability': ml_res['risk_probability'],
        'explainable_indicators': risk_res['explainable_indicators'],
        'risk_factors': risk_res['risk_indicators'],
        'suggested_actions': risk_res['suggested_actions']
    }

def run_scenario_comparison(original_case_data, modified_scenario_data):
    """
    Executes real ML model predictions on both the current case parameters
    and simulated modified parameters, returning a side-by-side comparative analysis.
    """
    current_prediction = get_full_case_prediction(original_case_data)
    simulated_prediction = get_full_case_prediction(modified_scenario_data)
    
    days_saved = current_prediction['predicted_remaining_days'] - simulated_prediction['predicted_remaining_days']
    risk_prob_reduction = round(current_prediction['risk_probability'] - simulated_prediction['risk_probability'], 1)
    
    return {
        'current': current_prediction,
        'simulated': simulated_prediction,
        'days_saved': max(0, days_saved),
        'risk_prob_reduction': max(0.0, risk_prob_reduction),
        'disclaimer': "Scenario results are prototype simulations based on the trained model and should not be interpreted as guaranteed real-world outcomes."
    }
