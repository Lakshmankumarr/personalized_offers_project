import pandas as pd
import numpy as np
from datetime import datetime, timedelta


np.random.seed(42)
n_customers = 100_000
customers = pd.DataFrame({
    'customer_id': range(1, n_customers+1),
    'signup_date': pd.to_datetime('2020-01-01') + pd.to_timedelta(np.random.randint(0, 365*5, n_customers), unit='d'),
    'loyalty_status': np.random.choice(['Silver','Gold','Platinum'], n_customers, p=[0.5,0.35,0.15]),
    'age': np.random.randint(18, 70, n_customers),
    'gender': np.random.choice(['M','F'], n_customers)
})


n_transactions = 500_000
transactions = pd.DataFrame({
    'order_id': range(1, n_transactions+1),
    'customer_id': np.random.choice(customers['customer_id'], n_transactions),
    'timestamp': pd.to_datetime('2025-01-01') + pd.to_timedelta(np.random.randint(0, 365, n_transactions), unit='d'),
    'total_amount': np.round(np.random.uniform(2.5, 15.0, n_transactions),2),
    'store_id': np.random.randint(1, 500, n_transactions)
})

# -------------------------
# 3️⃣ Generate Offers
# -------------------------
offers = pd.DataFrame({
    'offer_id': [1,2,3,4],
    'offer_type': ['10% Discount','20% Discount','BOGO','Free Add-on'],
    'discount_value': [0.1,0.2,0,0],  
    'cost_estimate': [1,2,2,1.5]
})

# -------------------------
# 4️⃣ Generate Redemptions (Vectorized)
# -------------------------
# Map loyalty to probability
loyalty_map = {'Silver':0.1, 'Gold':0.2, 'Platinum':0.3}
customer_loyalty = customers.set_index('customer_id')['loyalty_status']
transactions['loyalty'] = transactions['customer_id'].map(customer_loyalty)
transactions['redeem_prob'] = transactions['loyalty'].map(loyalty_map)

# Generate random numbers and select redemptions
transactions['rand'] = np.random.rand(len(transactions))
redemptions = transactions[transactions['rand'] < transactions['redeem_prob']].copy()

# Assign random offer to each redemption
redemptions['offer_id'] = np.random.choice(offers['offer_id'], len(redemptions))
redemptions = redemptions[['customer_id','order_id','offer_id','timestamp']]

# -------------------------
# 5️⃣ Save CSVs
# -------------------------
customers.to_csv('data/customers.csv', index=False)
transactions.to_csv('data/transactions.csv', index=False)
offers.to_csv('data/offers.csv', index=False)
redemptions.to_csv('data/redemptions.csv', index=False)

print("Synthetic dataset generated and saved in 'data/' folder.")
