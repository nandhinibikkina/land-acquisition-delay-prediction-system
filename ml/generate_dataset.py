import os
import sys

# Ensure root directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
import datetime
from config import Config

def generate_synthetic_data(num_samples=1200, seed=42):
    np.random.seed(seed)
    
    districts = ['East Godavari', 'West Godavari', 'Visakhapatnam', 'Krishna', 'Guntur', 'Kurnool', 'Chittoor', 'Nellore']
    villages = ['Kakinada Rural', 'Rajahmundry', 'Anakapalle', 'Vijayawada North', 'Tenali', 'Nandyal', 'Tirupati Rural', 'Gudur', 'Bhimavaram', 'Eluru']
    land_types = ['Agricultural', 'Commercial', 'Residential', 'Barren']
    purposes = ['Highway Expansion', 'Railway Corridor', 'Industrial Park', 'Irrigation Project', 'Urban Infrastructure', 'Solar Power Plant']
    stages = [
        'Land Identification',
        'Owner Verification',
        'Document Verification',
        'Land Valuation',
        'Compensation',
        'Legal/Approval',
        'Acquisition Completion'
    ]
    
    # Base remaining days for each stage
    stage_base_days = {
        'Land Identification': 130,
        'Owner Verification': 105,
        'Document Verification': 85,
        'Land Valuation': 65,
        'Compensation': 45,
        'Legal/Approval': 35,
        'Acquisition Completion': 10
    }
    
    cases = []
    
    start_date = datetime.date(2024, 1, 1)
    
    for i in range(1, num_samples + 1):
        case_id = f"LA-{1000 + i}"
        district = np.random.choice(districts)
        village = np.random.choice(villages)
        land_area = round(float(np.random.uniform(0.5, 120.0)), 2)
        land_type = np.random.choice(land_types, p=[0.55, 0.15, 0.15, 0.15])
        acquisition_purpose = np.random.choice(purposes)
        current_stage = np.random.choice(stages)
        
        # Days pending based on stage
        days_pending = int(np.random.randint(10, 220))
        
        # Application date calculated backwards
        app_date = start_date - datetime.timedelta(days=days_pending)
        application_date = app_date.strftime('%Y-%m-%d')
        
        # Probabilities influenced by status
        docs_complete = np.random.choice(['Yes', 'No'], p=[0.7, 0.3])
        owner_verified = np.random.choice(['Yes', 'No'], p=[0.75, 0.25])
        
        if current_stage in ['Compensation', 'Legal/Approval', 'Acquisition Completion']:
            comp_status = np.random.choice(['Completed', 'In Progress', 'Pending', 'Disputed'], p=[0.45, 0.35, 0.15, 0.05])
        else:
            comp_status = np.random.choice(['Completed', 'In Progress', 'Pending', 'Disputed'], p=[0.1, 0.4, 0.4, 0.1])
            
        legal_dispute = np.random.choice(['Yes', 'No'], p=[0.18, 0.82])
        
        if current_stage == 'Acquisition Completion':
            approval_status = np.random.choice(['Approved', 'Under Review', 'Pending'], p=[0.8, 0.15, 0.05])
        else:
            approval_status = np.random.choice(['Approved', 'Under Review', 'Pending'], p=[0.4, 0.4, 0.2])
            
        # Calculate actual_remaining_days with logical domain factors
        base_days = stage_base_days[current_stage]
        
        delay_penalty = 0
        if docs_complete == 'No':
            delay_penalty += np.random.randint(25, 45)
        if owner_verified == 'No':
            delay_penalty += np.random.randint(20, 35)
        if comp_status in ['Pending', 'Disputed']:
            delay_penalty += np.random.randint(30, 60)
        if legal_dispute == 'Yes':
            delay_penalty += np.random.randint(65, 120)
        if approval_status in ['Pending', 'Under Review']:
            delay_penalty += np.random.randint(15, 35)
        if days_pending > 120:
            delay_penalty += np.random.randint(15, 30)
            
        # Noise
        noise = np.random.normal(0, 12)
        
        actual_remaining_days = max(5, int(round(base_days + delay_penalty + noise)))
        
        # Determine delayed binary classification target (1 if significantly delayed, 0 otherwise)
        # Logical rule with noise:
        total_time = days_pending + actual_remaining_days
        delay_threshold = stage_base_days[current_stage] + 90
        
        # Probabilistic assignment of 'delayed' based on total time & legal dispute
        delay_score = (
            (1 if docs_complete == 'No' else 0) * 1.5 +
            (1 if legal_dispute == 'Yes' else 0) * 3.0 +
            (1 if comp_status in ['Pending', 'Disputed'] else 0) * 1.5 +
            (1 if days_pending > 100 else 0) * 1.0 +
            (1 if actual_remaining_days > 70 else 0) * 1.5
        )
        
        # Threshold with random variation
        is_delayed = 1 if (delay_score >= 3.0 or legal_dispute == 'Yes' or (total_time > 200 and np.random.rand() > 0.15)) else 0
        
        cases.append({
            'case_id': case_id,
            'district': district,
            'village': village,
            'land_area': land_area,
            'land_type': land_type,
            'acquisition_purpose': acquisition_purpose,
            'current_stage': current_stage,
            'application_date': application_date,
            'days_pending': days_pending,
            'documents_complete': docs_complete,
            'owner_verified': owner_verified,
            'compensation_status': comp_status,
            'legal_dispute': legal_dispute,
            'approval_status': approval_status,
            'actual_remaining_days': actual_remaining_days,
            'delayed': is_delayed
        })
        
    df = pd.DataFrame(cases)
    return df

def main():
    os.makedirs(os.path.dirname(Config.HISTORICAL_DATA_PATH), exist_ok=True)
    
    print("Generating synthetic land acquisition historical dataset...")
    df = generate_synthetic_data(num_samples=1200, seed=42)
    df.to_csv(Config.HISTORICAL_DATA_PATH, index=False)
    print(f"Saved {len(df)} historical cases to {Config.HISTORICAL_DATA_PATH}")
    
    # Save a clean sample set of 100 cases
    sample_df = df.head(100).copy()
    sample_df.to_csv(Config.SAMPLE_DATA_PATH, index=False)
    print(f"Saved {len(sample_df)} sample cases to {Config.SAMPLE_DATA_PATH}")

if __name__ == '__main__':
    main()
