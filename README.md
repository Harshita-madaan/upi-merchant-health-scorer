# UPI Merchant Health Scorer

## Problem Statement
Small UPI merchants (kirana stores, textile shops, pharmacies) across Punjab have no formal credit history, making it impossible for NBFCs and banks to assess their creditworthiness. This project builds a data-driven merchant health scoring system using UPI transaction behavior as a proxy for credit risk.

## Solution
An end-to-end data science pipeline that:
- Ingests and stores 4.28M+ UPI transactions in a MySQL database
- Engineers features using SQL window functions and CTEs
- Predicts merchant risk tier (Low / Medium / High) using XGBoost
- Explains predictions using SHAP values
- Visualizes insights through a live Tableau dashboard
- Serves predictions via a modern Flask web application

## Live Demo
- Dashboard: [View on Tableau Public](https://public.tableau.com/app/profile/harshita.madaan/viz/UPIMerchantHealthScorer/Dashboard1?publish=yes)
- Web App: Run locally via python app.py

## Tech Stack
| Layer | Tools |
|---|---|
| Database | MySQL |
| Data Generation | Python, Faker, NumPy |
| SQL Analytics | Window Functions, CTEs, Views |
| ML Pipeline | XGBoost, Scikit-learn, SHAP |
| Web App | Flask, HTML, CSS |
| Visualization | Tableau Public |
| Version Control | Git, GitHub |

## Key Results
- 4,280,000+ transactions across 500 merchants over 18 months
- XGBoost model achieving 100% accuracy on synthetic data
- Top features: transaction frequency, MoM growth, failure rate
- Modern dark-theme web UI for instant risk assessment

## Project Structure
upi_merchant_health/
├── app.py                      # Flask web application
├── predict_merchant.py         # CLI risk predictor
├── generate_data.py            # Synthetic data generation
├── merchant_model.pkl          # Trained XGBoost model
├── sql_analytics.sql           # SQL feature engineering
├── merchant_health_ml.ipynb    # ML pipeline notebook
├── templates/
│   ├── index.html              # Input form
│   └── result.html             # Risk result page
├── eda_charts.png              # EDA visualizations
├── shap_feature_importance.png # SHAP explainability
└── confusion_matrix.png        # Model evaluation

## How to Run
1. Set up MySQL and create database upi_merchant_health
2. Run python generate_data.py to populate the database
3. Run SQL queries in sql_analytics.sql
4. Open and run merchant_health_ml.ipynb
5. Start web app: python app.py
6. Open http://127.0.0.1:5000 in your browser
