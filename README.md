# Land Acquisition Delay Prediction & Early Warning System (LADIS)

> **SIH Problem Statement:** SIH26017 – Predictive Analytics System for Early Detection of Land Acquisition Delays

---

## ⚠️ Prototype Notice
> **Important:** This decision-support system is a hackathon prototype developed for Smart India Hackathon (SIH26017). This demonstration uses synthetic/simulated land-acquisition dataset generated for algorithmic training and validation. It is **not connected** to live government databases or real-time revenue systems.

---

## 📌 Problem Statement & Background
Land acquisition is a critical prerequisite for infrastructure projects in India, including highways, railways, industrial corridors, and irrigation networks. However, land acquisition cases frequently suffer from severe timeline overruns caused by legal disputes, missing title deeds, delayed compensation disbursal, pending statutory approvals, and unverified owner titles.

These delay bottlenecks result in escalating infrastructure project costs and delayed public utility benefits. Existing manual monitoring tools react to delays only after deadlines have expired.

## 💡 Proposed Solution
The **Land Acquisition Delay Prediction & Early Warning System (LADIS)** provides land acquisition officers and revenue departments with a proactive AI-driven decision-support tool. By analyzing historical case parameters and workflow stage metrics using Random Forest Machine Learning algorithms, LADIS:
1. **Predicts Estimated Remaining Days** required for complete acquisition clearance.
2. **Classifies Delay Risk Level** into `LOW`, `MEDIUM`, and `HIGH` risk categories.
3. **Calculates Risk Probability Percentage**.
4. **Pinpoints Potential Contributing Risk Indicators** (e.g., missing documents, compensation disputes, litigation stay orders).
5. **Generates Actionable Officer Follow-up Recommendations**.
6. **Issues Early Warning Alerts** for high-risk cases before statutory deadlines lapse.

---

## 🔄 Acquisition Workflow Stages
The system models the standard 7-stage Indian land acquisition lifecycle:
1. **Land Identification** (Khasra/Survey plot identification)
2. **Owner Verification** (Genealogy & title register audit)
3. **Document Verification** (Revenue certificates & NOC verification)
4. **Land Valuation** (Market value & compensation assessment)
5. **Compensation** (Section 19 award & treasury transfer)
6. **Legal/Approval** (Statutory clearance & dispute resolution)
7. **Acquisition Completion** (Final possession & title transfer)

---

## 🛠️ Technology Stack

| Layer | Technology / Libraries |
| :--- | :--- |
| **Backend Framework** | Python 3.14, Flask |
| **Machine Learning** | Scikit-Learn, Pandas, NumPy, Joblib |
| **Database** | SQLite3 |
| **Frontend UI** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5 |
| **Data Visualization** | Chart.js 4.4 |
| **Icons & Styling** | FontAwesome 6, Custom Modern SIH Theme |

---

## 🧠 Machine Learning Approach

The system employs two distinct, complementary Random Forest models trained on preprocessed historical land acquisition features:

### 1. Regression Model (`RandomForestRegressor`)
* **Target:** `actual_remaining_days`
* **Output:** Estimated Remaining Days to completion.
* **Pipeline:** Categorical features OneHotEncoded, numerical features standardized via `ColumnTransformer`.
* **Performance:** R² Score ~ 0.907, MAE ~ 16.7 days.

### 2. Classification Model (`RandomForestClassifier`)
* **Target:** `delayed` (Binary delay status)
* **Output:** Predicted Delay Risk Probability & Risk Level (`LOW` <35%, `MEDIUM` 35-65%, `HIGH` >65%).
* **Performance:** Classification Accuracy ~ 94.2%.

---

## 📁 Project Structure

```
land-acquisition-delay-system/
├── app.py                      # Flask Application Main Server & Routes
├── config.py                   # Global Configuration & Path Settings
├── requirements.txt            # Python Package Dependencies
├── README.md                   # Comprehensive Project Documentation
│
├── data/
│   ├── historical_cases.csv    # 1,200 Synthetic Historical Cases for ML Training
│   └── sample_cases.csv        # 100 Sample Cases for Initial DB Seeding
│
├── database/
│   └── database.db             # SQLite Production Database File
│
├── ml/
│   ├── generate_dataset.py     # Domain-Logical Synthetic Dataset Generator
│   ├── train_models.py         # Model Training & Scikit-Learn Pipeline Persistence
│   ├── predict.py              # Real-Time ML Inference & Scoring Function
│   └── models/
│       ├── delay_regressor.pkl  # Trained Random Forest Regressor Model
│       └── risk_classifier.pkl # Trained Random Forest Classifier Model
│
├── services/
│   ├── data_service.py         # Business Logic & Database Access Layer
│   ├── prediction_service.py   # Integrated Prediction & Decision Support Service
│   └── risk_analysis.py       # Rule-Based Contributing Risk Indicator Engine
│
├── templates/
│   ├── base.html               # Master Layout with Navigation & Prototype Footer
│   ├── login.html              # Officer Authentication View
│   ├── dashboard.html          # Executive Analytics Dashboard with Chart.js
│   ├── cases.html              # Filterable Case Directory with Search & Sort
│   ├── add_case.html           # New Case Registration Form with Instant ML Scoring
│   ├── case_details.html       # 7-Stage Visual Progress Tracker & Decision Card
│   ├── prediction.html         # Interactive What-If Scenario Simulator
│   └── alerts.html             # High-Risk Early Warning Alerts Page
│
├── static/
│   ├── css/
│   │   └── style.css           # Custom SIH Modern Government Portal Theme
│   ├── js/
│   │   ├── dashboard.js        # Chart.js Initialization Scripts
│   │   └── prediction.js       # Dynamic Simulation Interaction Helper
│   └── images/
│
└── utils/
    └── database.py             # SQLite Helpers & CRUD Functions
```

---

## 🚀 Installation & How to Run

### 1. Prerequisites
Ensure Python 3.9+ is installed on your system.

### 2. Install Dependencies
Open terminal/powershell inside the project directory and run:
```bash
pip install -r requirements.txt
```

### 3. Generate Dataset (Optional - Pre-generated)
```bash
python ml/generate_dataset.py
```

### 4. Train ML Models (Optional - Pre-trained)
```bash
python ml/train_models.py
```

### 5. Launch Application Server
```bash
python app.py
```

### 6. Access in Web Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔑 Prototype Demo Credentials

| Role | Username | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Land Acquisition Officer** | `admin` | `admin123` | Executive Dashboard, Add Case, Alerts, Simulator |

---

## ⚡ Core Features Walkthrough

1. **Executive Dashboard (`/dashboard`):**
   * Real-time KPI summaries: Total Cases, Low Risk, Medium Risk, High Risk, Avg Pending Days.
   * 4 Interactive Chart.js Visualizations (Risk Level Distribution, Stage Breakdown, District Case Distribution, Avg Pending Days Bottleneck Trend).
   * High Risk Cases Quick Action Table.

2. **Acquisition Cases Directory (`/cases`):**
   * Multi-attribute filtering (District, Stage, Risk Level).
   * Keyword search across Case ID, Village, and Project Purpose.
   * Sorting by Days Pending, Risk Probability, or Estimated Remaining Days.

3. **Register New Case (`/cases/add`):**
   * Multi-section statutory input form.
   * Automatic execution of ML models and rule engine upon submission.
   * Instant database storage and redirect to detailed decision card.

4. **Case Details & Visual Progress Tracker (`/cases/<case_id>`):**
   * 7-Stage visual workflow timeline highlighting current active stage.
   * Predictive decision card detailing Estimated Remaining Days, Delay Risk Level, and Risk Probability.
   * Identified Contributing Risk Indicators and suggested officer follow-up actions.

5. **Early Warning Alerts (`/alerts`):**
   * Dedicated alert feed isolating HIGH-risk acquisition cases.
   * Actionable recommendations to prevent statutory deadline lapse.

6. **What-If Delay Simulator (`/prediction`):**
   * Interactive calculator allowing revenue officers to test custom parameter combinations without altering production DB records.

---

## 🛡️ Limitations
* **Synthetic Data Scope:** Uses simulated dataset reflecting standard Indian land acquisition patterns due to restricted access to confidential government land records.
* **Non-Automated External Actions:** The system operates purely as a decision-support system; it does not issue automated legal orders or directly disburse treasury payments.

---

## 🔮 Future Scope
* **GIS / GeoJSON Integration:** Interactive satellite map overlay highlighting acquired plots and disputed survey numbers.
* **Document OCR Analysis:** Automated scanning of scanned title deeds using AI OCR to flag missing stamps or title defects automatically.
* **Bilingual Support:** Multi-language interface support (Telugu, Hindi, Tamil, Marathi) for district field officers.
