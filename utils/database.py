import sqlite3
import os
import json
from config import Config

def get_db_connection():
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS land_acquisition_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT UNIQUE NOT NULL,
            district TEXT NOT NULL,
            village TEXT NOT NULL,
            land_area REAL NOT NULL,
            land_type TEXT NOT NULL,
            acquisition_purpose TEXT NOT NULL,
            current_stage TEXT NOT NULL,
            application_date TEXT NOT NULL,
            days_pending INTEGER NOT NULL,
            documents_complete TEXT NOT NULL,
            owner_verified TEXT NOT NULL,
            compensation_status TEXT NOT NULL,
            legal_dispute TEXT NOT NULL,
            approval_status TEXT NOT NULL,
            predicted_remaining_days INTEGER,
            risk_level TEXT,
            risk_probability REAL,
            risk_factors TEXT,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_all_cases():
    conn = get_db_connection()
    cases = conn.execute('SELECT * FROM land_acquisition_cases ORDER BY days_pending DESC').fetchall()
    conn.close()
    return [dict(case) for case in cases]

def get_case_by_id(case_id):
    conn = get_db_connection()
    case = conn.execute('SELECT * FROM land_acquisition_cases WHERE case_id = ?', (case_id,)).fetchone()
    conn.close()
    return dict(case) if case else None

def add_case(case_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    risk_factors_str = json.dumps(case_data.get('risk_factors', [])) if isinstance(case_data.get('risk_factors'), list) else case_data.get('risk_factors', '')
    
    cursor.execute('''
        INSERT INTO land_acquisition_cases (
            case_id, district, village, land_area, land_type, acquisition_purpose,
            current_stage, application_date, days_pending, documents_complete,
            owner_verified, compensation_status, legal_dispute, approval_status,
            predicted_remaining_days, risk_level, risk_probability, risk_factors, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        case_data['case_id'], case_data['district'], case_data['village'],
        float(case_data['land_area']), case_data['land_type'], case_data['acquisition_purpose'],
        case_data['current_stage'], case_data['application_date'], int(case_data['days_pending']),
        case_data['documents_complete'], case_data['owner_verified'], case_data['compensation_status'],
        case_data['legal_dispute'], case_data['approval_status'],
        case_data.get('predicted_remaining_days'), case_data.get('risk_level'),
        case_data.get('risk_probability'), risk_factors_str,
        case_data.get('status', 'Active')
    ))
    
    conn.commit()
    conn.close()

def update_case_prediction(case_id, predicted_remaining_days, risk_level, risk_probability, risk_factors):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    risk_factors_str = json.dumps(risk_factors) if isinstance(risk_factors, list) else risk_factors
    
    cursor.execute('''
        UPDATE land_acquisition_cases
        SET predicted_remaining_days = ?,
            risk_level = ?,
            risk_probability = ?,
            risk_factors = ?
        WHERE case_id = ?
    ''', (predicted_remaining_days, risk_level, risk_probability, risk_factors_str, case_id))
    
    conn.commit()
    conn.close()

def get_high_risk_cases():
    conn = get_db_connection()
    cases = conn.execute("SELECT * FROM land_acquisition_cases WHERE risk_level = 'HIGH' ORDER BY days_pending DESC").fetchall()
    conn.close()
    return [dict(case) for case in cases]

def search_and_filter_cases(query=None, district=None, stage=None, risk=None, sort_by='days_pending', sort_order='desc', village=None, status=None):
    conn = get_db_connection()
    sql = 'SELECT * FROM land_acquisition_cases WHERE 1=1'
    params = []
    
    if query:
        sql += ' AND (case_id LIKE ? OR district LIKE ? OR village LIKE ? OR acquisition_purpose LIKE ?)'
        wildcard = f'%{query}%'
        params.extend([wildcard, wildcard, wildcard, wildcard])
        
    if district and district != 'All':
        sql += ' AND district = ?'
        params.append(district)
        
    if village and village != 'All':
        sql += ' AND village = ?'
        params.append(village)
        
    if stage and stage != 'All':
        sql += ' AND current_stage = ?'
        params.append(stage)
        
    if risk and risk != 'All':
        sql += ' AND risk_level = ?'
        params.append(risk)

    if status and status != 'All':
        sql += ' AND status = ?'
        params.append(status)
        
    if sort_by == 'newest':
        sql += ' ORDER BY created_at DESC, id DESC'
    elif sort_by == 'oldest':
        sql += ' ORDER BY created_at ASC, id ASC'
    elif sort_by == 'highest_pending':
        sql += ' ORDER BY days_pending DESC'
    elif sort_by == 'highest_risk':
        sql += ' ORDER BY risk_probability DESC'
    elif sort_by == 'lowest_risk':
        sql += ' ORDER BY risk_probability ASC'
    elif sort_by == 'predicted_remaining_days':
        sql += ' ORDER BY predicted_remaining_days DESC'
    else:
        order = 'DESC' if str(sort_order).lower() == 'desc' else 'ASC'
        sql += f' ORDER BY days_pending {order}'
        
    cases = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(case) for case in cases]

def get_district_analytics():
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT 
            district,
            COUNT(*) as total_cases,
            SUM(CASE WHEN risk_level = 'HIGH' THEN 1 ELSE 0 END) as high_risk,
            SUM(CASE WHEN risk_level = 'MEDIUM' THEN 1 ELSE 0 END) as medium_risk,
            SUM(CASE WHEN risk_level = 'LOW' THEN 1 ELSE 0 END) as low_risk,
            AVG(days_pending) as avg_pending,
            AVG(predicted_remaining_days) as avg_est_remaining
        FROM land_acquisition_cases
        GROUP BY district
        ORDER BY total_cases DESC
    ''').fetchall()
    conn.close()
    
    district_list = []
    for r in rows:
        district_list.append({
            'district': r['district'],
            'total_cases': r['total_cases'],
            'high_risk': r['high_risk'] or 0,
            'medium_risk': r['medium_risk'] or 0,
            'low_risk': r['low_risk'] or 0,
            'avg_pending': round(r['avg_pending'] or 0, 1),
            'avg_est_remaining': round(r['avg_est_remaining'] or 0, 1)
        })
    return district_list

def get_bottleneck_analysis():
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT 
            current_stage,
            COUNT(*) as total_cases,
            AVG(days_pending) as avg_pending,
            AVG(predicted_remaining_days) as avg_est_remaining,
            SUM(CASE WHEN risk_level = 'HIGH' THEN 1 ELSE 0 END) as high_risk_count
        FROM land_acquisition_cases
        GROUP BY current_stage
        ORDER BY avg_pending DESC
    ''').fetchall()
    conn.close()
    
    bottlenecks = []
    for r in rows:
        avg_p = round(r['avg_pending'] or 0, 1)
        if avg_p > 75:
            severity = 'High Bottleneck'
        elif avg_p > 45:
            severity = 'Moderate Delay'
        else:
            severity = 'Normal Pace'
            
        bottlenecks.append({
            'stage': r['current_stage'],
            'total_cases': r['total_cases'],
            'avg_pending': avg_p,
            'avg_est_remaining': round(r['avg_est_remaining'] or 0, 1),
            'high_risk_count': r['high_risk_count'] or 0,
            'severity': severity
        })
    return bottlenecks

def get_dashboard_stats():
    conn = get_db_connection()
    
    total_cases = conn.execute('SELECT COUNT(*) FROM land_acquisition_cases').fetchone()[0]
    low_risk = conn.execute("SELECT COUNT(*) FROM land_acquisition_cases WHERE risk_level = 'LOW'").fetchone()[0]
    medium_risk = conn.execute("SELECT COUNT(*) FROM land_acquisition_cases WHERE risk_level = 'MEDIUM'").fetchone()[0]
    high_risk = conn.execute("SELECT COUNT(*) FROM land_acquisition_cases WHERE risk_level = 'HIGH'").fetchone()[0]
    avg_pending = conn.execute('SELECT AVG(days_pending) FROM land_acquisition_cases').fetchone()[0] or 0
    
    stage_counts = conn.execute('SELECT current_stage, COUNT(*) as count FROM land_acquisition_cases GROUP BY current_stage').fetchall()
    district_counts = conn.execute('SELECT district, COUNT(*) as count FROM land_acquisition_cases GROUP BY district').fetchall()
    avg_pending_by_stage = conn.execute('SELECT current_stage, AVG(days_pending) as avg_days FROM land_acquisition_cases GROUP BY current_stage').fetchall()
    status_counts = conn.execute('SELECT status, COUNT(*) as count FROM land_acquisition_cases GROUP BY status').fetchall()
    
    conn.close()
    
    return {
        'total_cases': total_cases,
        'low_risk': low_risk,
        'medium_risk': medium_risk,
        'high_risk': high_risk,
        'avg_pending_days': round(avg_pending, 1),
        'risk_distribution': {
            'LOW': low_risk,
            'MEDIUM': medium_risk,
            'HIGH': high_risk
        },
        'cases_by_stage': {r['current_stage']: r['count'] for r in stage_counts},
        'cases_by_district': {r['district']: r['count'] for r in district_counts},
        'avg_pending_by_stage': {r['current_stage']: round(r['avg_days'], 1) for r in avg_pending_by_stage},
        'cases_by_status': {r['status']: r['count'] for r in status_counts}
    }

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
