import random
import pandas as pd
import numpy as np
from faker import Faker
import mysql.connector
from datetime import datetime, timedelta

fake = Faker('en_IN')
random.seed(42)
np.random.seed(42)

# DB connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",         # change if needed
    password="Harshita@123",        # add your MySQL password
    database="upi_merchant_health"
)
cursor = conn.cursor()

# config
CATEGORIES = ['kirana', 'textile', 'pharmacy', 'electronics', 'food', 'hardware', 'salon']
CITIES     = ['Jalandhar', 'Ludhiana', 'Amritsar', 'Chandigarh', 'Patiala', 'Bathinda']
BANKS      = ['SBI', 'HDFC', 'ICICI', 'Punjab National Bank', 'Axis', 'Kotak', 'Paytm Payments Bank']

NUM_MERCHANTS = 500
START_DATE    = datetime(2024, 1, 1)
END_DATE      = datetime(2025, 6, 30)

FESTIVAL_DATES = [
    datetime(2024, 1, 14),
    datetime(2024, 3, 25),
    datetime(2024, 10, 31),
    datetime(2024, 11, 15),
    datetime(2025, 1, 13),
    datetime(2025, 3, 14),
]

def is_festival(date):
    return any(abs((date - f).days) <= 2 for f in FESTIVAL_DATES)

def is_weekend(date):
    return date.weekday() >= 5

# merchants
print("Inserting merchants...")
merchants = []
for i in range(1, NUM_MERCHANTS + 1):
    merchant_id  = f"M{i:04d}"
    category     = random.choice(CATEGORIES)
    city         = random.choice(CITIES)
    reg_date     = START_DATE - timedelta(days=random.randint(30, 730))
    monthly_rent = random.choice([None, random.randint(3000, 25000)])
    merchants.append((merchant_id, fake.company(), category, city, reg_date.date(), monthly_rent, 1))

cursor.executemany("""
    INSERT INTO merchants (merchant_id, merchant_name, category, city, registration_date, monthly_rent, is_active)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
""", merchants)
conn.commit()
print("500 merchants done.")

# health profiles for merchants
HEALTHY    = random.sample(range(1, NUM_MERCHANTS+1), 300)
DECLINING  = random.sample([x for x in range(1, NUM_MERCHANTS+1) if x not in HEALTHY], 120)
STRUGGLING = [x for x in range(1, NUM_MERCHANTS+1) if x not in HEALTHY and x not in DECLINING]

def get_base_txns(merchant_num, date):
    if merchant_num in HEALTHY:
        base = random.randint(8, 25)
        days_in = (date - START_DATE).days
        base = int(base * (1 + 0.0003 * days_in))
    elif merchant_num in DECLINING:
        base = random.randint(5, 20)
        days_in = (date - START_DATE).days
        base = max(1, int(base * (1 - 0.0004 * days_in)))
    else:
        base = random.randint(1, 8)
    if is_festival(date):
        base = int(base * random.uniform(1.8, 3.0))
    if is_weekend(date):
        base = int(base * random.uniform(1.1, 1.4))
    return max(1, base)

def get_amount(category):
    ranges = {
        'kirana':      (50,  800),
        'textile':     (200, 5000),
        'pharmacy':    (80,  1500),
        'electronics': (500, 15000),
        'food':        (60,  600),
        'hardware':    (100, 3000),
        'salon':       (100, 1000),
    }
    lo, hi = ranges[category]
    return round(random.uniform(lo, hi), 2)

# transactions
print("Inserting transactions, this may take a few minutes...")
batch       = []
batch_size  = 5000
txn_counter = 1
current     = START_DATE

while current <= END_DATE:
    for i, (merchant_id, _, category, *_rest) in enumerate(merchants):
        merchant_num = i + 1
        num_txns     = get_base_txns(merchant_num, current)

        for _ in range(num_txns):
            if merchant_num in STRUGGLING:
                status = random.choices(['success','failed','refunded'], weights=[75,15,10])[0]
            elif merchant_num in DECLINING:
                status = random.choices(['success','failed','refunded'], weights=[85,9,6])[0]
            else:
                status = random.choices(['success','failed','refunded'], weights=[93,4,3])[0]

            txn_time = current + timedelta(
                hours=random.randint(8, 22),
                minutes=random.randint(0, 59)
            )
            batch.append((
                f"T{txn_counter:08d}",
                merchant_id,
                get_amount(category),
                txn_time,
                status,
                random.choice(BANKS)
            ))
            txn_counter += 1

            if len(batch) >= batch_size:
                cursor.executemany("""
                    INSERT INTO transactions
                    (transaction_id, merchant_id, amount, transaction_date, status, payer_bank)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, batch)
                conn.commit()
                print(f"  {txn_counter-1:,} transactions inserted so far...")
                batch = []

    current += timedelta(days=1)

if batch:
    cursor.executemany("""
        INSERT INTO transactions
        (transaction_id, merchant_id, amount, transaction_date, status, payer_bank)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, batch)
    conn.commit()

print(f"Inserted {txn_counter-1:,} transactions.")

# daily summaries
print("Building daily summaries...")
cursor.execute("""
    INSERT INTO daily_summaries
        (merchant_id, summary_date, total_revenue, transaction_count, refund_count, failed_count, avg_ticket_size)
    SELECT
        merchant_id,
        DATE(transaction_date)                                         AS summary_date,
        SUM(CASE WHEN status = 'success' THEN amount ELSE 0 END)      AS total_revenue,
        COUNT(*)                                                        AS transaction_count,
        SUM(CASE WHEN status = 'refunded' THEN 1 ELSE 0 END)          AS refund_count,
        SUM(CASE WHEN status = 'failed'   THEN 1 ELSE 0 END)          AS failed_count,
        AVG(CASE WHEN status = 'success' THEN amount ELSE NULL END)    AS avg_ticket_size
    FROM transactions
    GROUP BY merchant_id, DATE(transaction_date)
""")
conn.commit()
print("Daily summaries done.")

cursor.close()
conn.close()
print("All done.")