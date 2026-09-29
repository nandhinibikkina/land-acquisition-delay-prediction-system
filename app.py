import os
import sys
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

from config import Config
from services.data_service import (
    initialize_and_seed_database, process_and_add_new_case,
    format_case_detail, get_priority_queue
)
from utils.database import (
    get_all_cases, get_case_by_id, get_high_risk_cases,
    search_and_filter_cases, get_dashboard_stats,
    get_district_analytics, get_bottleneck_analysis
)
from services.prediction_service import get_full_case_prediction, run_scenario_comparison

app = Flask(__name__)
app.config.from_object(Config)

# Initialize and seed database on startup
initialize_and_seed_database()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash("Please log in to access the system.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            session['username'] = username
            flash("Successfully authenticated as Officer (Admin).", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password. Please use admin / admin123.", "error")
            
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    stats = get_dashboard_stats()
    priority_queue = get_priority_queue()[:8]
    district_analytics = get_district_analytics()
    bottlenecks = get_bottleneck_analysis()
    
    return render_template(
        'dashboard.html',
        stats=stats,
        priority_queue=priority_queue,
        district_analytics=district_analytics,
        bottlenecks=bottlenecks
    )

@app.route('/cases')
@login_required
def view_cases():
    query = request.args.get('q', '')
    district = request.args.get('district', 'All')
    village = request.args.get('village', 'All')
    stage = request.args.get('stage', 'All')
    risk = request.args.get('risk', 'All')
    status = request.args.get('status', 'All')
    sort_by = request.args.get('sort', 'highest_pending')
    
    raw_cases = search_and_filter_cases(
        query=query,
        district=district,
        stage=stage,
        risk=risk,
        sort_by=sort_by,
        village=village,
        status=status
    )
    
    cases = [format_case_detail(c) for c in raw_cases]
    
    districts = ['East Godavari', 'West Godavari', 'Visakhapatnam', 'Krishna', 'Guntur', 'Kurnool', 'Chittoor', 'Nellore']
    stages = [
        'Land Identification', 'Owner Verification', 'Document Verification',
        'Land Valuation', 'Compensation', 'Legal/Approval', 'Acquisition Completion'
    ]
    
    return render_template(
        'cases.html',
        cases=cases,
        query=query,
        selected_district=district,
        selected_village=village,
        selected_stage=stage,
        selected_risk=risk,
        selected_status=status,
        selected_sort=sort_by,
        districts=districts,
        stages=stages
    )

@app.route('/cases/add', methods=['GET', 'POST'])
@login_required
def add_case_page():
    if request.method == 'POST':
        try:
            case_dict, pred = process_and_add_new_case(request.form)
            flash(f"Case {case_dict['case_id']} registered successfully! ML predicted remaining days: {pred['predicted_remaining_days']} days ({pred['risk_level']} Risk).", "success")
            return redirect(url_for('case_details', case_id=case_dict['case_id']))
        except Exception as e:
            flash(f"Error registering case: {str(e)}", "error")
            
    return render_template('add_case.html')

@app.route('/cases/<case_id>')
@login_required
def case_details(case_id):
    raw_case = get_case_by_id(case_id)
    if not raw_case:
        flash(f"Case ID '{case_id}' not found.", "error")
        return redirect(url_for('view_cases'))
        
    case = format_case_detail(raw_case)
    
    # Model Evaluation Metrics metadata for transparency section
    model_metrics = {
        'regressor_name': 'RandomForestRegressor',
        'regressor_mae': 16.74,
        'regressor_r2': 0.9072,
        'classifier_name': 'RandomForestClassifier',
        'classifier_accuracy': 94.17
    }
    
    return render_template('case_details.html', case=case, model_metrics=model_metrics)

@app.route('/cases/<case_id>/scenario', methods=['POST'])
@login_required
def single_case_scenario(case_id):
    raw_case = get_case_by_id(case_id)
    if not raw_case:
        flash(f"Case ID '{case_id}' not found.", "error")
        return redirect(url_for('view_cases'))
        
    original_case = format_case_detail(raw_case)
    
    # Form modified values
    modified_data = dict(original_case)
    modified_data['documents_complete'] = request.form.get('documents_complete', original_case['documents_complete'])
    modified_data['owner_verified'] = request.form.get('owner_verified', original_case['owner_verified'])
    modified_data['compensation_status'] = request.form.get('compensation_status', original_case['compensation_status'])
    modified_data['legal_dispute'] = request.form.get('legal_dispute', original_case['legal_dispute'])
    modified_data['approval_status'] = request.form.get('approval_status', original_case['approval_status'])
    modified_data['days_pending'] = int(request.form.get('days_pending', original_case['days_pending']))
    
    scenario_res = run_scenario_comparison(original_case, modified_data)
    
    model_metrics = {
        'regressor_name': 'RandomForestRegressor',
        'regressor_mae': 16.74,
        'regressor_r2': 0.9072,
        'classifier_name': 'RandomForestClassifier',
        'classifier_accuracy': 94.17
    }
    
    return render_template('case_details.html', case=original_case, scenario_res=scenario_res, model_metrics=model_metrics)

@app.route('/cases/<case_id>/report')
@login_required
def case_report(case_id):
    raw_case = get_case_by_id(case_id)
    if not raw_case:
        flash(f"Case ID '{case_id}' not found.", "error")
        return redirect(url_for('view_cases'))
        
    case = format_case_detail(raw_case)
    return render_template('report.html', case=case)

@app.route('/alerts')
@login_required
def alerts():
    risk_filter = request.args.get('risk', 'All')
    query = request.args.get('q', '')
    
    raw_cases = search_and_filter_cases(query=query, risk=risk_filter if risk_filter != 'All' else None)
    if risk_filter == 'All':
        raw_cases = [c for c in raw_cases if c['risk_level'] in ['HIGH', 'MEDIUM']]
        
    alert_cases = [format_case_detail(c) for c in raw_cases]
    return render_template('alerts.html', alert_cases=alert_cases, selected_risk=risk_filter, query=query)

@app.route('/prediction', methods=['GET', 'POST'])
@login_required
def prediction_simulator():
    scenario_comparison = None
    input_data = None
    
    if request.method == 'POST':
        input_data = {
            'district': request.form.get('district', 'East Godavari'),
            'land_type': request.form.get('land_type', 'Agricultural'),
            'acquisition_purpose': request.form.get('acquisition_purpose', 'Highway Expansion'),
            'current_stage': request.form.get('current_stage', 'Compensation'),
            'land_area': float(request.form.get('land_area', 10.0)),
            'days_pending': int(request.form.get('days_pending', 45)),
            'documents_complete': request.form.get('documents_complete', 'No'),
            'owner_verified': request.form.get('owner_verified', 'Yes'),
            'compensation_status': request.form.get('compensation_status', 'Pending'),
            'legal_dispute': request.form.get('legal_dispute', 'No'),
            'approval_status': request.form.get('approval_status', 'Pending')
        }
        
        # Build hypothetical improved scenario
        simulated_data = dict(input_data)
        simulated_data['documents_complete'] = request.form.get('sim_documents_complete', input_data['documents_complete'])
        simulated_data['compensation_status'] = request.form.get('sim_compensation_status', input_data['compensation_status'])
        simulated_data['legal_dispute'] = request.form.get('sim_legal_dispute', input_data['legal_dispute'])
        simulated_data['approval_status'] = request.form.get('sim_approval_status', input_data['approval_status'])
        
        scenario_comparison = run_scenario_comparison(input_data, simulated_data)
        
    return render_template('prediction.html', scenario_comparison=scenario_comparison, input_data=input_data)

@app.route('/analytics')
@login_required
def analytics():
    stats = get_dashboard_stats()
    district_analytics = get_district_analytics()
    bottlenecks = get_bottleneck_analysis()
    return render_template(
        'analytics.html',
        stats=stats,
        district_analytics=district_analytics,
        bottlenecks=bottlenecks
    )

@app.route('/api/stats')
@login_required
def api_stats():
    stats = get_dashboard_stats()
    return jsonify(stats)

if __name__ == '__main__':
    print("Starting Land Acquisition Delay Prediction Platform server on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
