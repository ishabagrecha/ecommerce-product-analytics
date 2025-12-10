import sqlite3
import pandas as pd
import plotly.express as px

# Connect to the database
conn = sqlite3.connect('ecommerce.db')

print("--- 📊 STARTING PRODUCT ANALYSIS ---")

# ==========================================
# ANALYSIS 1: The Conversion Funnel
# Question: How many people view -> add to cart -> purchase?
# ==========================================
print("\n1️⃣ Calculating Conversion Funnel...")

funnel_query = """
SELECT 
    event_type,
    COUNT(DISTINCT user_session) as sessions
FROM events
WHERE event_type IN ('view', 'cart', 'purchase')
GROUP BY 1
ORDER BY 2 DESC;
"""

df_funnel = pd.read_sql(funnel_query, conn)

# Calculate specific drop-off rates
# (We use "sessions" instead of users because a user can have multiple buying journeys)
initial_views = df_funnel[df_funnel['event_type'] == 'view']['sessions'].values[0]
cart_adds = df_funnel[df_funnel['event_type'] == 'cart']['sessions'].values[0]
purchases = df_funnel[df_funnel['event_type'] == 'purchase']['sessions'].values[0]

print(df_funnel)
print(f"\n📉 View to Cart Rate: {round((cart_adds / initial_views) * 100, 2)}%")
print(f"📉 Cart to Purchase Rate: {round((purchases / cart_adds) * 100, 2)}%")


# ==========================================
# ANALYSIS 2: Daily Active Users (DAU)
# Question: Are we growing or losing users over time?
# ==========================================
print("\n2️⃣ Calculating Daily Active Users (DAU)...")

dau_query = """
SELECT 
    strftime('%Y-%m-%d', event_time) as date,
    COUNT(DISTINCT user_id) as active_users
FROM events
GROUP BY 1
ORDER BY 1;
"""

df_dau = pd.read_sql(dau_query, conn)

# Quick peek at the data
print(df_dau.head())
print(f"✅ Extracted {len(df_dau)} days of data.")

# ==========================================
# VISUALIZATION PREVIEW (Optional)
# This opens a quick interactive chart in your browser
# ==========================================
print("\n🚀 Generating Quick Chart...")
fig = px.line(df_dau, x='date', y='active_users', title='Daily Active Users (DAU) Trend')
fig.write_html("dau_chart.html")

conn.close()