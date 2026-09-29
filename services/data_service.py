import os
import sys
import json
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config
from utils.database import (
    init_db, get_all_cases, get_case_by_id, add_case,
    get_high_risk_cases, search_and_filter_cases, get_dashboard_stats,
    get_db_connection, get_district_analytics, get_bottleneck_analysis
)
from services.prediction_service import get_full_case_prediction
from services.risk_analysis import analyze_risk_factors

def initialize_and_seed_database():
    """Initializes SQLite tables and seeds sample data if empty."""
    init_db()
    
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) FROM land_acquisition_cases').fetchone()[0]
    conn.close()
    
    if count == 0 and os.path.exists(Config.SAMPLE_DATA_PATH):
        print("Seeding database with sample cases...")
        df = pd.read_csv(Config.SAMPLE_DATA_PATH)
        
        for idx, row in df.iterrows():
            case_dict = row.to_dict()
            pred = get_full_case_prediction(case_dict)
            
            case_data = {
                'case_id': str(case_dict['case_id']),
                'district': str(case_dict['district']),
                'village': str(case_dict['village']),
                'land_area': float(case_dict['land_area']),
                'land_type': str(case_dict['land_type']),
                'acquisition_purpose': str(case_dict['acquisition_purpose']),
                'current_stage': str(case_dict['current_stage']),
                'application_date': str(case_dict['application_date']),
                'days_pending': int(case_dict['days_pending']),
                'documents_complete': str(case_dict['documents_complete']),
                'owner_verified': str(case_dict['owner_verified']),
                'compensation_status': str(case_dict['compensation_status']),
                'legal_dispute': str(case_dict['legal_dispute']),
                'approval_status': str(case_dict['approval_status']),
                'predicted_remaining_days': pred['predicted_remaining_days'],
                'risk_level': pred['risk_level'],
                'risk_probability': pred['risk_probability'],
                'risk_factors': pred['risk_factors'],
                'status': 'Active'
            }
            
            try:
                add_case(case_data)
            except Exception as e:
                print(f"Error seeding case {case_dict.get('case_id')}: {e}")
                
        print(f"Database seeded with {len(df)} sample cases.")

def process_and_add_new_case(form_data):
    """Processes form submission, runs ML prediction & risk analysis, and stores in SQLite."""
    case_id = form_data.get('case_id', '').strip()
    if not case_id:
        raise ValueError("Case ID is required.")
        
    case_dict = {
        'case_id': case_id,
        'district': form_data.get('district', 'East Godavari'),
        'village': form_data.get('village', 'Kakinada Rural'),
        'land_area': float(form_data.get('land_area', 1.0)),
        'land_type': form_data.get('land_type', 'Agricultural'),
        'acquisition_purpose': form_data.get('acquisition_purpose', 'Highway Expansion'),
        'current_stage': form_data.get('current_stage', 'Land Identification'),
        'application_date': form_data.get('application_date', '2024-01-01'),
        'days_pending': int(form_data.get('days_pending', 0)),
        'documents_complete': form_data.get('documents_complete', 'No'),
        'owner_verified': form_data.get('owner_verified', 'No'),
        'compensation_status': form_data.get('compensation_status', 'Pending'),
        'legal_dispute': form_data.get('legal_dispute', 'No'),
        'approval_status': form_data.get('approval_status', 'Pending')
    }
    
    pred = get_full_case_prediction(case_dict)
    
    case_dict['predicted_remaining_days'] = pred['predicted_remaining_days']
    case_dict['risk_level'] = pred['risk_level']
    case_dict['risk_probability'] = pred['risk_probability']
    case_dict['risk_factors'] = pred['risk_factors']
    case_dict['status'] = 'Active'
    
    add_case(case_dict)
    return case_dict, pred

def get_case_health_summary(case):
    """Calculates 5-dimension health indicators for case decision support."""
    docs = str(case.get('documents_complete', '')).lower()
    owner = str(case.get('owner_verified', '')).lower()
    comp = str(case.get('compensation_status', ''))
    legal = str(case.get('legal_dispute', '')).lower()
    approval = str(case.get('approval_status', ''))
    
    health = {
        'documentation': {'label': 'Documentation', 'status': 'Completed' if docs in ['yes', 'true'] else 'Pending', 'badge': 'success' if docs in ['yes', 'true'] else 'danger'},
        'owner_verification': {'label': 'Owner Verification', 'status': 'Verified' if owner in ['yes', 'true'] else 'Pending Audit', 'badge': 'success' if owner in ['yes', 'true'] else 'warning'},
        'compensation': {'label': 'Compensation', 'status': comp, 'badge': 'success' if comp == 'Completed' else ('danger' if comp == 'Disputed' else 'warning')},
        'legal_status': {'label': 'Legal Status', 'status': 'Attention Required' if legal in ['yes', 'true'] else 'Clear', 'badge': 'danger' if legal in ['yes', 'true'] else 'success'},
        'approval': {'label': 'Statutory Approval', 'status': approval, 'badge': 'success' if approval == 'Approved' else 'warning'}
    }
    return health

def format_case_detail(case):
    """Helper to parse JSON risk_factors string and format health, explainable indicators, and follow-ups."""
    if not case:
        return None
        
    case_obj = dict(case)
    
    if isinstance(case_obj.get('risk_factors'), str):
        try:
            case_obj['risk_factors_list'] = json.loads(case_obj['risk_factors'])
        except Exception:
            case_obj['risk_factors_list'] = [f.strip() for f in case_obj['risk_factors'].split(',') if f.strip()]
    elif isinstance(case_obj.get('risk_factors'), list):
        case_obj['risk_factors_list'] = case_obj['risk_factors']
    else:
        case_obj['risk_factors_list'] = []
        
    analysis = analyze_risk_factors(case_obj)
    case_obj['explainable_indicators'] = analysis['explainable_indicators']
    case_obj['suggested_actions'] = analysis['suggested_actions']
    case_obj['health_summary'] = get_case_health_summary(case_obj)
    
    if not case_obj['risk_factors_list']:
        case_obj['risk_factors_list'] = analysis['risk_indicators']
        
    return case_obj

def get_priority_queue():
    """
    Ranks cases into P1 (Critical), P2 (High), P3 (Medium), P4 (Low) priority review tiers
    based on risk level, risk probability %, and pending duration.
    """
    all_cases = get_all_cases()
    scored_cases = []
    
    for raw in all_cases:
        case = format_case_detail(raw)
        
        # Calculate composite priority score
        risk_weight = 50.0 if case['risk_level'] == 'HIGH' else (30.0 if case['risk_level'] == 'MEDIUM' else 10.0)
        prob_score = (case.get('risk_probability', 0) or 0) * 0.35
        pending_score = min(30.0, (case.get('days_pending', 0) / 180.0) * 30.0)
        
        composite_score = risk_weight + prob_score + pending_score
        
        if composite_score >= 75.0 or case['risk_level'] == 'HIGH':
            priority_rank = 'P1'
            priority_badge = 'danger'
            recommended_review = 'Immediate Collectorate intervention & legal review required.'
        elif composite_score >= 50.0 or case['risk_level'] == 'MEDIUM':
            priority_rank = 'P2'
            priority_badge = 'warning'
            recommended_review = 'Priority Tahsildar audit & compensation award follow-up.'
        elif composite_score >= 35.0:
            priority_rank = 'P3'
            priority_badge = 'info'
            recommended_review = 'Routine document verification & revenue audit.'
        else:
            priority_rank = 'P4'
            priority_badge = 'secondary'
            recommended_review = 'Standard workflow monitoring.'
            
        case['priority_rank'] = priority_rank
        case['priority_badge'] = priority_badge
        case['priority_score'] = round(composite_score, 1)
        case['recommended_review'] = recommended_review
        scored_cases.append(case)
        
    scored_cases.sort(key=lambda x: x['priority_score'], reverse=True)
    return scored_cases
