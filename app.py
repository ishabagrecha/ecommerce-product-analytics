import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# 1. PAGE SETUP
st.set_page_config(page_title="Product Analytics Dashboard", layout="wide")
st.title("📊 E-Commerce Product Analytics")

# 2. LOAD DATA
# We use @st.cache_data so the app doesn't reload the DB every time you click a button
@st.cache_data
def load_data():
    conn = sqlite3.connect('ecommerce.db')
    
    # Query 1: Funnel
    q_funnel = """
        SELECT event_type, COUNT(DISTINCT user_session) as sessions
        FROM events 
        WHERE event_type IN ('view', 'cart', 'purchase')
        GROUP BY 1
    """
    df_funnel = pd.read_sql(q_funnel, conn)
    
    # Query 2: Daily Trends
    q_dau = """
        SELECT strftime('%Y-%m-%d', event_time) as date, COUNT(DISTINCT user_id) as users
        FROM events GROUP BY 1 ORDER BY 1
    """
    df_dau = pd.read_sql(q_dau, conn)
    
    conn.close()
    return df_funnel, df_dau

# Load the data
try:
    df_funnel, df_dau = load_data()
    st.success("Data loaded successfully!")
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# 3. BUILD THE LAYOUT
col1, col2 = st.columns(2)

with col1:
    st.subheader("🛒 Conversion Funnel")
    # Sort data manually to ensure order: View -> Cart -> Purchase
    custom_order = {'view': 1, 'cart': 2, 'purchase': 3}
    df_funnel['order'] = df_funnel['event_type'].map(custom_order)
    df_funnel = df_funnel.sort_values('order')
    
    # Calculate Drop-off
    fig_funnel = px.bar(df_funnel, x='event_type', y='sessions', 
                        text='sessions', color='event_type',
                        title="User Sessions by Funnel Step")
    st.plotly_chart(fig_funnel, use_container_width=True)
    
    # Insights
    views = df_funnel[df_funnel['event_type']=='view']['sessions'].values[0]
    carts = df_funnel[df_funnel['event_type']=='cart']['sessions'].values[0]
    conversion_rate = round((carts / views) * 100, 2)
    st.metric(label="View-to-Cart Conversion", value=f"{conversion_rate}%")

with col2:
    st.subheader("📈 User Growth (DAU)")
    fig_dau = px.line(df_dau, x='date', y='users', title="Daily Active Users")
    st.plotly_chart(fig_dau, use_container_width=True)

st.markdown("---")
st.write(" **Business Recommendation:** The drop-off from View to Cart is high. Investigate the product details page UI.")