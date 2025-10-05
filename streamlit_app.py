# streamlit_app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="Personalized Offer Dashboard", layout="wide")

# --------------------------
# 1️⃣ Load raw CSVs
# --------------------------
customers = pd.read_csv('data/customers.csv')
transactions = pd.read_csv('data/transactions.csv')
offers = pd.read_csv('data/offers.csv')
redemptions = pd.read_csv('data/redemptions.csv')

# --------------------------
# 2️⃣ Feature Engineering (RFM)
# --------------------------
transactions['timestamp'] = pd.to_datetime(transactions['timestamp'])
now = pd.to_datetime('2025-10-05')

rfm = transactions.groupby('customer_id').agg(
    recency=('timestamp', lambda x: (now - x.max()).days),
    frequency=('order_id','count'),
    monetary=('total_amount','sum')
).reset_index()

data = rfm.merge(customers, on='customer_id', how='left')

# Redemption rate
red_rate = redemptions.groupby('customer_id')['offer_id'].count() / transactions.groupby('customer_id')['order_id'].count()
data['redemption_rate'] = data['customer_id'].map(red_rate).fillna(0)

# --------------------------
# 3️⃣ Clustering
# --------------------------
X_scaled = StandardScaler().fit_transform(data[['recency','frequency','monetary']])
kmeans = KMeans(n_clusters=5, random_state=42).fit(X_scaled)
data['segment'] = kmeans.labels_

# --------------------------
# 4️⃣ Predictive Model
# --------------------------
target = (redemptions.groupby('customer_id')['offer_id'].count() > 0).astype(int)
data['target'] = data['customer_id'].map(target).fillna(0)

features = ['recency','frequency','monetary','redemption_rate']
X_train, X_val, y_train, y_val = train_test_split(data[features], data['target'], test_size=0.2, random_state=42)

clf = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
clf.fit(X_train, y_train)
data['pred_prob'] = clf.predict_proba(data[features])[:,1]

# --------------------------
# 5️⃣ ROI Simulation
# --------------------------
N = len(data)
uplift = 0.05  # 5% incremental conversion
AOV = 8.0
margin = 0.6
discount_cost = 1.5
fixed_costs = 2000

incremental_redemptions = N * uplift
incremental_revenue = incremental_redemptions * AOV
incremental_profit = incremental_revenue * margin
total_costs = incremental_redemptions * discount_cost + fixed_costs
net_profit = incremental_profit - total_costs
roi = net_profit / total_costs

# --------------------------
# 6️⃣ Streamlit UI
# --------------------------
st.title("Personalized Offer Dashboard")
st.write("Customer Segments and Offer Redemption Insights")

# Segment distribution
st.subheader("Customer Segment Distribution")
seg_counts = data['segment'].value_counts().sort_index()
st.bar_chart(seg_counts)

# Predicted redemption probability
st.subheader("Predicted Redemption Probability")
fig, ax = plt.subplots()
ax.hist(data['pred_prob'], bins=50, color='skyblue', edgecolor='black')
ax.set_xlabel("Predicted Redemption Probability")
ax.set_ylabel("Number of Customers")
st.pyplot(fig)

# ROI summary
st.subheader("ROI Simulation")
st.write(f"Net Profit: ${net_profit:,.2f}")
st.write(f"ROI: {roi*100:.2f}%")
