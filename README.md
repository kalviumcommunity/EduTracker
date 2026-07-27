# 🎓 EduTrack – Student Learning Behaviour Analytics & Early Risk Detection Dashboard

EduTrack is a **Business Intelligence (BI) Analytics Platform** built to help educational institutions analyze student learning behavior and identify at-risk students through interactive dashboards and data-driven insights.

The platform processes educational data such as course completion, quiz performance, study sessions, and engagement metrics to provide actionable recommendations that improve learning outcomes and course completion rates.

---

## 📖 Overview

Modern EdTech platforms collect large volumes of educational data, but much of it remains underutilized. EduTrack transforms this raw data into meaningful analytics, enabling instructors and academic teams to monitor student engagement, identify learning patterns, and take proactive interventions before students drop out.

---

## 🚀 Features

### 📊 Interactive Dashboard
- Institutional KPIs
- Course Completion Trends
- Student Engagement Analysis
- Course Performance Analytics
- At-Risk Student Overview

### 📈 Behaviour Analytics
- Student Engagement Score
- Study Hours Analysis
- Login Frequency Tracking
- Learning Consistency Metrics
- Drop-Off Detection

### 📚 Course Analytics
- Course Completion Rate
- Average Quiz Performance
- Student Progress Monitoring
- Completion Trends

### 📄 Reporting
- Dashboard Export
- Analytical Reports
- Chart Export
- KPI Reports

---

## 🎯 Project Objectives

- Analyze student learning behaviour
- Measure learner engagement
- Detect at-risk students early
- Identify behavioural patterns
- Build interactive dashboards
- Improve course completion rates
- Enable data-driven academic decisions

---

## ❗ Problem Statement

Educational institutions generate enormous amounts of learning data, but this information is rarely transformed into meaningful insights.

Current challenges include:

- Difficulty identifying at-risk students
- Limited visibility into learner engagement
- Student disengagement going unnoticed
- Decisions based on assumptions instead of analytics

EduTrack addresses these challenges by providing a centralized analytics platform for monitoring student performance and engagement.

---

## 👥 Target Users

### Primary Users
- 👨‍🏫 Instructors
- 📚 Course Managers

### Secondary Users
- Academic Teams
- Learning Success Teams
- Product Managers

---

## 📂 Data Sources

EduTrack integrates data from multiple educational sources:

- Student Information
- Course Details
- Quiz Performance Records
- Learning Session Activity Logs
- Course Completion Records

---

## 🔄 Workflow

```
Raw Educational Data
        │
        ▼
Data Cleaning & Validation
        │
        ▼
Feature Engineering
        │
        ▼
SQLite Database
        │
        ▼
SQL Analytics
        │
        ▼
KPI Calculation
        │
        ▼
Interactive Streamlit Dashboard
        │
        ▼
Behaviour Analytics
        │
        ▼
Business Insights & Reports
```

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Programming Language | Python |
| Data Processing | Pandas, NumPy |
| Database | SQLite |
| ORM | SQLAlchemy |
| Dashboard | Streamlit |
| Visualization | Plotly, Matplotlib, Seaborn |
| Version Control | Git, GitHub |
| Development Environment | Visual Studio Code |
| Testing | Pytest |

---

## 📊 Key Performance Indicators (KPIs)

The dashboard tracks:

- Course Completion Rate
- Student Drop-Off Rate
- Average Quiz Score
- Student Engagement Score
- Average Study Hours
- Daily Active Students (DAS)
- Number of At-Risk Students

---

## ⚙️ Functional Requirements

- Import CSV datasets
- Validate and clean data
- Store data in SQLite
- Execute SQL queries
- Calculate KPIs
- Detect at-risk students
- Display interactive Streamlit dashboards
- Generate analytical reports

---

## 🔒 Non-Functional Requirements

- Dashboard load time under **5 seconds**
- High reliability
- Responsive user interface
- Secure data storage
- Scalable architecture
- Cross-platform compatibility

---

## 📦 Project Scope

### ✅ In Scope

- Data Cleaning
- Feature Engineering
- SQLite Database
- SQL Analytics
- KPI Calculation
- Streamlit Dashboard
- Interactive Visualizations
- Report Generation

### ❌ Out of Scope

- User Authentication
- Mobile Application
- Real-Time Data Processing
- Machine Learning
- Cloud Deployment
- LMS Integration

---

## 💻 Setup & Installation

Follow these steps to set up the development environment locally:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kalviumcommunity/EduTracker.git
   cd EduTracker
   ```

2. **Create and activate a virtual environment:**
   - macOS/Linux: `python3 -m venv venv && source venv/bin/activate`
   - Windows: `python -m venv venv && venv\Scripts\activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Analytics & Data Pipelines:**
   ```bash
   python scripts/feature_engineering_pipeline.py
   python scripts/numpy_vectorization_pipeline.py
   python scripts/distribution_analysis_pipeline.py
   python scripts/correlation_analysis_pipeline.py
   python scripts/segmentation_groupby_pipeline.py
   python scripts/time_series_trends_pipeline.py
   ```

5. **Run the Streamlit Dashboard:**
   ```bash
   streamlit run app.py
   ```

---

## 📈 Expected Deliverables

- Cleaned Educational Dataset
- SQLite Database
- SQL Queries
- Interactive Dashboard
- KPI Calculation Module
- Behaviour Analytics Module
- Project Documentation
- User Guide

---

## 🌟 Future Enhancements

- Machine Learning-based Risk Prediction
- Predictive Analytics
- Real-Time Data Processing
- Mobile Dashboard
- Email Notifications
- Role-Based Access Control (RBAC)
- LMS Integration
- Cloud Deployment
- Forecasting Dashboards

---

## 📁 Project Structure

```
EduTrack/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── database/
│
├── notebooks/
│
├── dashboard/
│
├── output/
│   └── (Generated charts, figures, and analytical reports)
│
├── reports/
│
├── scripts/
│   ├── feature_engineering_pipeline.py
│   ├── numpy_vectorization_pipeline.py
│   ├── distribution_analysis_pipeline.py
│   ├── correlation_analysis_pipeline.py
│   ├── segmentation_groupby_pipeline.py
│   └── time_series_trends_pipeline.py
│
├── src/
│   ├── data_cleaning/
│   ├── feature_engineering/
│   ├── analytics/
│   ├── kpi/
│   └── visualization/
│
├── tests/
│
├── requirements.txt
├── README.md
└── app.py
```

---

## 👨‍💻 Team

**Team 03**

- Megha R.
- Rahul A. B.
- Kathram Vijaya Simha Reddy

---

## 📌 Version

**Version:** 1.0

**Sprint:** Sprint 1

---

## 📄 License

This project is developed for educational and academic purposes.

---

## ⭐ Conclusion

EduTrack transforms educational data into actionable insights through interactive dashboards, performance metrics, and early risk detection. By empowering instructors and academic teams with meaningful analytics, the platform supports proactive interventions, improves student engagement, reduces dropout rates, and promotes data-driven decision-making for better learning outcomes.

---

### ⭐ If you found this project useful, consider giving it a star on GitHub!