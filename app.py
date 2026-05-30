import streamlit as st
import pandas as pd
import requests
import os
import joblib
import xgboost as xgb
import plotly.express as px
from train import execute_ml_pipeline

st.set_page_config(page_title="Enterprise Dynamic Pricing Dashboard", layout="wide")
st.title("📊 Real-Time Dynamic Pricing Engine (Enterprise REST Architecture)")

SUPABASE_URL = "https://bmsrfnjpaqxmegxwbhum.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJtc3JmbmpwYXF4bWVneHdiaHVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODAxNTgzMTgsImV4cCI6MjA5NTczNDMxOH0.o742QJe6ivSsUvARoolRJqcapPPItF8PIOdw8y5ZPPI"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

try:
    response = requests.get(f"{SUPABASE_URL}/rest/v1/product_prices?select=*&order=timestamp.desc", headers=headers)
    df_history = pd.DataFrame(response.json())
except Exception:
    df_history = pd.DataFrame()

if df_history.empty:
    with st.spinner("🚀 Booting system application pipeline..."):
        execute_ml_pipeline()
    st.rerun()

col_inputs, col_charts = st.columns([1, 2])

with col_inputs:
    st.header("⚡ Simulation Engine")
    demand = st.slider("Market Demand Index", 1.0, 10.0, 5.5)
    comp_price = st.number_input("Competitor Price Benchmark ($)", value=45.0)
    day_type = st.selectbox("Day Variance Categorization", ["Weekday", "Weekend"])
    
    if os.path.exists('models/preprocessor.pkl') and os.path.exists('models/pricing_xgb_model.json'):
        preprocessor = joblib.load('models/preprocessor.pkl')
        model = xgb.XGBRegressor()
        model.load_model('models/pricing_xgb_model.json')
        
        input_data = pd.DataFrame([{'demand_score': demand, 'competitor_price': comp_price, 'day_of_week': day_type}])
        pred = model.predict(preprocessor.transform(input_data))[0]
        
        st.metric(label="Calculated Target Optimization Price", value=f"${pred:,.2f}")

with col_charts:
    st.header("📈 Live Cloud Database Stream")
    if not df_history.empty:
        fig = px.scatter(df_history, x='competitor_price', y='price', color='demand_score',
                         title="Internal Valuation vs Competitor Benchmarks")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_history.head(15))