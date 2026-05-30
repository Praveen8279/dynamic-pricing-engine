import streamlit as st
import pandas as pd
import psycopg2
import os
import joblib
import xgboost as xgb
import plotly.express as px
# Add this right after your imports in app.py
from scraper import scrape_live_marketplace
from train import execute_ml_pipeline

# Cloud Auto-Initialize check
try:
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM product_prices LIMIT 1;")
    has_data = cursor.fetchone()
    conn.close()
except Exception:
    has_data = False

# If the database is completely empty (like it is right now), kickstart the engine automatically!
if not has_data:
    st.info("🚀 System initializing for the first time... Triggering live parallel data ingestion pipeline...")
    execute_ml_pipeline()
    st.rerun()

st.set_page_config(page_title="Enterprise Pricing System", layout="wide")
st.title("📊 Enterprise Real-Time Dynamic Pricing Engine")

# Environment variable configs for streaming analytics
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "pricing_analytics")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASSWORD", "supersecretpassword")

# Fetch background log metrics safely
try:
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    df_history = pd.read_sql_query("SELECT * FROM product_prices ORDER BY timestamp DESC", conn)
    conn.close()
except Exception as e:
    df_history = pd.DataFrame()

# Split the layout cleanly into simulation controls and operational data
col_inputs, col_charts = st.columns([1, 2])

with col_inputs:
    st.header("⚡ Simulation Tool")
    demand = st.slider("Demand Index", 1.0, 10.0, 5.0)
    comp_price = st.number_input("Competitor Index ($)", value=50.0)
    day_type = st.selectbox("Day Variance", ["Weekday", "Weekend"])
    
    # Inference engine execution
    if os.path.exists('models/preprocessor.pkl') and os.path.exists('models/pricing_xgb_model.json'):
        preprocessor = joblib.load('models/preprocessor.pkl')
        model = xgb.XGBRegressor()
        model.load_model('models/pricing_xgb_model.json')
        
        input_data = pd.DataFrame([{'demand_score': demand, 'competitor_price': comp_price, 'day_of_week': day_type}])
        pred = model.predict(preprocessor.transform(input_data))[0]
        
        st.metric(label="Target Selling Strategy Price", value=f"${pred:,.2f}")
    else:
        st.warning("Please run train.py first to build machine learning assets.")

with col_charts:
    st.header("📈 Historical Marketplace Operations Data")
    if not df_history.empty:
        fig = px.line(df_history, x='timestamp', y='price', title="Price Trajectory Trends (PostgreSQL Live Feed)")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_history.head(10))
    else:
        st.info("Database is currently empty. Running your pipeline will show live relational tables here.")