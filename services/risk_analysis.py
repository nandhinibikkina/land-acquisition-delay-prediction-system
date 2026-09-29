def analyze_risk_factors(case_data):
    """
    Analyzes case attributes to identify potential contributing risk indicators with detailed
    explainable descriptions, severity levels, and decision-support follow-up recommendations.
    """
    explainable_indicators = []
    risk_indicators_simple = []
    suggested_actions = []
    
    docs = str(case_data.get('documents_complete', '')).strip().lower()
    owner = str(case_data.get('owner_verified', '')).strip().lower()
    comp = str(case_data.get('compensation_status', '')).strip()
    legal = str(case_data.get('legal_dispute', '')).strip().lower()
    approval = str(case_data.get('approval_status', '')).strip()
    days_pending = int(case_data.get('days_pending', 0))
    stage = str(case_data.get('current_stage', '')).strip()
    
    # 1. Document Verification
    if docs in ['no', 'false', 'incomplete']:
        risk_indicators_simple.append("Documents incomplete")
        explainable_indicators.append({
            'indicator': 'Documents incomplete',
            'title': 'Missing Statutory Land Record Deeds',
            'description': 'Mandatory revenue survey maps, title deeds, or Non-Encumbrance Certificates (NEC) are incomplete, preventing statutory Section 11 notification.',
            'severity': 'High'
        })
        suggested_actions.append("Issue formal notice to land owners and coordinate with Tahsildar to supply missing survey plot certificates.")
        
    # 2. Owner Verification
    if owner in ['no', 'false', 'pending']:
        risk_indicators_simple.append("Owner verification pending")
        explainable_indicators.append({
            'indicator': 'Owner verification pending',
            'title': 'Unverified Title & Genealogy Audit',
            'description': 'Ownership title verification or legal heir genealogy audit is pending with local revenue authorities, creating risk of title challenges.',
            'severity': 'Medium'
        })
        suggested_actions.append("Schedule urgent field inquiry by Village Revenue Officer (VRO) to complete title register audit.")
        
    # 3. Compensation Status
    if comp in ['Pending', 'Disputed', 'In Progress']:
        if comp == 'Disputed':
            risk_indicators_simple.append("Compensation dispute present")
            explainable_indicators.append({
                'indicator': 'Compensation dispute present',
                'title': 'Disputed Land Valuation Award',
                'description': 'Landowners have filed objections regarding compensation valuation rate, risking formal escalation to LARA authority.',
                'severity': 'High'
            })
            suggested_actions.append("Refer valuation dispute to District Land Acquisition Rehabilitation Authority (LARA) for fast-track negotiation.")
        else:
            risk_indicators_simple.append("Compensation pending")
            explainable_indicators.append({
                'indicator': 'Compensation pending',
                'title': 'Pending Treasury Disbursal Award',
                'description': 'Compensation award calculation or treasury fund allocation is pending disbursal under Section 19.',
                'severity': 'Medium'
            })
            suggested_actions.append("Expedite compensation award sanction and coordinate with Treasury Officer for direct bank transfer.")
            
    # 4. Legal Dispute
    if legal in ['yes', 'true']:
        risk_indicators_simple.append("Legal dispute present")
        explainable_indicators.append({
            'indicator': 'Legal dispute present',
            'title': 'Active High Court Litigation / Stay Order',
            'description': 'An active writ petition or court stay order has been issued against possession, halting physical acquisition proceedings.',
            'severity': 'High'
        })
        suggested_actions.append("Submit urgent counter-affidavit via Government Standing Counsel to vacate court stay order.")
        
    # 5. Approval Status
    if approval in ['Pending', 'Under Review']:
        risk_indicators_simple.append("Approval pending")
        explainable_indicators.append({
            'indicator': 'Approval pending',
            'title': 'Pending Statutory Environmental/Forest Clearance',
            'description': 'Statutory clearance or competent authority sanction is under administrative review at the state department level.',
            'severity': 'Medium'
        })
        suggested_actions.append("Depute a nodal officer to follow up with the competent departmental approval committee.")
        
    # 6. Long Pending Duration
    if days_pending > 120:
        risk_indicators_simple.append("Long pending duration (>120 days)")
        explainable_indicators.append({
            'indicator': 'Long pending duration (>120 days)',
            'title': 'Critical Time Overrun (>120 Days)',
            'description': 'Case pending duration has exceeded the statutory benchmark threshold of 120 days without stage transition.',
            'severity': 'High'
        })
        suggested_actions.append("Flag case for priority review in District Collectorate monthly bottleneck clearing agenda.")
    elif days_pending > 60:
        risk_indicators_simple.append("Long pending duration (>60 days)")
        explainable_indicators.append({
            'indicator': 'Long pending duration (>60 days)',
            'title': 'Moderate Pending Duration (>60 Days)',
            'description': 'Case has been pending in the current workflow stage longer than the standard 60-day operational target.',
            'severity': 'Medium'
        })
        suggested_actions.append("Assign dedicated revenue inspector to monitor file progress daily.")

    if not suggested_actions:
        suggested_actions.append("Standard workflow proceeding normally. Schedule routine stage completion audit.")

    return {
        'explainable_indicators': explainable_indicators,
        'risk_indicators': risk_indicators_simple,
        'suggested_actions': suggested_actions
    }
