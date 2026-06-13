import joblib
import pandas as pd
import numpy as np

# load model
model = joblib.load('merchant_model.pkl')
tiers = {0: 'High Risk', 1: 'Low Risk', 2: 'Medium Risk'}

print("================================")
print("  UPI Merchant Risk Predictor")
print("================================\n")

avg_monthly_revenue  = float(input("Avg Monthly Revenue (INR): "))
avg_monthly_txns     = float(input("Avg Monthly Transactions: "))
avg_refund_rate      = float(input("Avg Refund Rate % (e.g. 3.5): "))
avg_failure_rate     = float(input("Avg Failure Rate % (e.g. 5.0): "))
avg_mom_growth       = float(input("Avg Month-on-Month Growth % (e.g. 2.5): "))
worst_mom_growth     = float(input("Worst Month Growth % (e.g. -15.0): "))
negative_months      = int(input("Number of Negative Growth Months (e.g. 3): "))
total_months         = int(input("Total Months in Business (e.g. 18): "))
business_age_days    = int(input("Business Age in Days (e.g. 730): "))
monthly_rent         = float(input("Monthly Rent INR (0 if unknown): "))
category             = input("Category (kirana/textile/pharmacy/electronics/food/hardware/salon): ").strip().lower()
city                 = input("City (Jalandhar/Ludhiana/Amritsar/Chandigarh/Patiala/Bathinda): ").strip()

# encode category and city
category_map = {'electronics':0, 'food':1, 'hardware':2, 'kirana':3, 'pharmacy':4, 'salon':5, 'textile':6}
city_map     = {'amritsar':0, 'bathinda':1, 'chandigarh':2, 'jalandhar':3, 'ludhiana':4, 'patiala':5}

category_enc = category_map.get(category, 3)
city_enc     = city_map.get(city.lower(), 3)

avg_ticket_size     = avg_monthly_revenue / avg_monthly_txns if avg_monthly_txns > 0 else 0
pct_negative_months = (negative_months / total_months * 100) if total_months > 0 else 0

input_data = pd.DataFrame([{
    'avg_monthly_revenue':  avg_monthly_revenue,
    'avg_monthly_txns':     avg_monthly_txns,
    'avg_refund_rate':      avg_refund_rate,
    'avg_failure_rate':     avg_failure_rate,
    'avg_ticket_size':      avg_ticket_size,
    'avg_mom_growth':       avg_mom_growth,
    'worst_mom_growth':     worst_mom_growth,
    'negative_growth_months': negative_months,
    'pct_negative_months':  pct_negative_months,
    'business_age_days':    business_age_days,
    'monthly_rent':         monthly_rent,
    'category_enc':         category_enc,
    'city_enc':             city_enc
}])

prediction = model.predict(input_data)[0]

print("\n================================")
print(f"  Risk Tier: {tiers[prediction]}")
print("================================")

if tiers[prediction] == 'Low Risk':
    print("Recommendation: Eligible for loan. Low default probability.")
elif tiers[prediction] == 'Medium Risk':
    print("Recommendation: Review required. Moderate default risk.")
else:
    print("Recommendation: High default risk. Loan not recommended.")
print("================================\n")