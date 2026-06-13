from flask import Flask, render_template, request
import joblib
import pandas as pd

app = Flask(__name__)
model = joblib.load('merchant_model.pkl')
tiers = {0: 'High Risk', 1: 'Low Risk', 2: 'Medium Risk'}

category_map = {'electronics':0, 'food':1, 'hardware':2, 'kirana':3, 'pharmacy':4, 'salon':5, 'textile':6}
city_map     = {'amritsar':0, 'bathinda':1, 'chandigarh':2, 'jalandhar':3, 'ludhiana':4, 'patiala':5}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    avg_monthly_revenue  = float(request.form['avg_monthly_revenue'])
    avg_monthly_txns     = float(request.form['avg_monthly_txns'])
    avg_refund_rate      = float(request.form['avg_refund_rate'])
    avg_failure_rate     = float(request.form['avg_failure_rate'])
    avg_mom_growth       = float(request.form['avg_mom_growth'])
    worst_mom_growth     = float(request.form['worst_mom_growth'])
    negative_months      = int(request.form['negative_months'])
    total_months         = int(request.form['total_months'])
    business_age_days    = int(request.form['business_age_days'])
    monthly_rent         = float(request.form['monthly_rent'])
    category             = request.form['category'].lower()
    city                 = request.form['city'].lower()

    category_enc = category_map.get(category, 3)
    city_enc     = city_map.get(city, 3)
    avg_ticket_size     = avg_monthly_revenue / avg_monthly_txns if avg_monthly_txns > 0 else 0
    pct_negative_months = (negative_months / total_months * 100) if total_months > 0 else 0

    input_data = pd.DataFrame([{
        'avg_monthly_revenue':    avg_monthly_revenue,
        'avg_monthly_txns':       avg_monthly_txns,
        'avg_refund_rate':        avg_refund_rate,
        'avg_failure_rate':       avg_failure_rate,
        'avg_ticket_size':        avg_ticket_size,
        'avg_mom_growth':         avg_mom_growth,
        'worst_mom_growth':       worst_mom_growth,
        'negative_growth_months': negative_months,
        'pct_negative_months':    pct_negative_months,
        'business_age_days':      business_age_days,
        'monthly_rent':           monthly_rent,
        'category_enc':           category_enc,
        'city_enc':               city_enc
    }])

    prediction  = model.predict(input_data)[0]
    risk_tier   = tiers[prediction]

    if risk_tier == 'Low Risk':
        recommendation = 'Eligible for loan. Low default probability.'
        color = 'green'
    elif risk_tier == 'Medium Risk':
        recommendation = 'Review required. Moderate default risk.'
        color = 'orange'
    else:
        recommendation = 'High default risk. Loan not recommended.'
        color = 'red'

    return render_template('result.html',
                           risk_tier=risk_tier,
                           recommendation=recommendation,
                           color=color,
                           revenue=avg_monthly_revenue,
                           txns=avg_monthly_txns,
                           refund=avg_refund_rate,
                           failure=avg_failure_rate,
                           category=category,
                           city=city)

if __name__ == '__main__':
    app.run(debug=True)