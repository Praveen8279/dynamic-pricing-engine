import streamlit as st
import pandas as pd
import requests
import os
import joblib
import xgboost as xgb
import plotly.express as px
from train import execute_ml_pipeline

# 1. Environment Secrets & Fallback Configuration
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    # Local fallback keys for machine execution
    SUPABASE_URL = "https://bmsrfnjpaqxmegxwbhum.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJtc3JmbG5qcGFxeG1lZ3h3Ymh1bSIsInJvbGUiOiJhbm9uIiwiaWF0IjoxNzE2OTU2NDA0LCJleHAiOjIwMzI1MzI0MDR9.YOUR_ANON_KEY_FROM_DASHBOARD"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

# 2. Page Configuration Setup
st.set_page_config(
    page_title="Enterprise Dynamic Pricing Dashboard", 
    layout="wide",
    page_icon="📊"
)

st.title("📊 Enterprise Real-Time Dynamic Pricing Engine")
st.markdown("---")

# 3. Data Fetching Routine from Cloud Database
@st.cache_data(ttl=60)
def fetch_historical_records():
    try:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/product_prices?select=*", headers=headers)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
    except Exception as e:
        st.error(f"Cloud DB Connection Error: {e}")
    return pd.DataFrame()

df_history = fetch_historical_records()

# 4. Check & Initialize Machine Learning Artifacts
model_dir = 'models'
preprocessor_path = os.path.join(model_dir, 'preprocessor.pkl')
model_path = os.path.join(model_dir, 'pricing_xgb_model.json')

if not (os.path.exists(preprocessor_path) and os.path.exists(model_path)):
    with st.spinner("🚀 Initializing system application pipeline and training core XGBoost model..."):
        execute_ml_pipeline()
    st.rerun()

# 5. Core Operational UI Layout Split
col_inputs, col_charts = st.columns([1, 2], gap="large")

with col_inputs:
    st.header("⚙️ Simulation Controls")
    st.write("Modify operational market indexes below to generate real-time predictive optimizations.")
    
    demand = st.slider("📈 Market Demand Index (Level 1-5)", min_value=1.0, max_value=5.0, value=3.0, step=0.5)
    comp_price = st.number_input("💵 Competitor Price Benchmark ($)", min_value=10.0, max_value=2000.0, value=150.0, step=10.0)
    day_type = st.selectbox("📅 Temporal Category Indicator", options=['Weekday', 'Weekend'])

    st.markdown("---")
    
    # 6. Real-Time Inference Execution Block
    if st.button("🎯 Calculate Optimized Strategy", type="primary"):
        try:
            # Load serialized scaling pipeline and model structure
            preprocessor = joblib.load(preprocessor_path)
            model = xgb.XGBRegressor()
            model.load_model(model_path)
            
            # Construct feature ingestion dataframe
            input_data = pd.DataFrame([{
                'demand_score': demand, 
                'competitor_price': comp_price, 
                'day_of_week': day_type
            }])
            
            # Run normalization and score prediction
            transformed_features = preprocessor.transform(input_data)
            predicted_price = model.predict(transformed_features)[0]
            
            st.success("Target Pricing Strategy Synthesized!")
            st.metric(
                label="Calculated Target Optimization Price", 
                value=f"${predicted_price:,.2f}"
            )
        except Exception as e:
            st.error(f"Inference Engine Runtime Exception: {e}")

with col_charts:
    st.header("📈 Live Cloud Database Stream")
    
    if not df_history.empty:
        # Build interactive Plotly Scatter Distribution
        fig = px.scatter(
            df_history, 
            x='competitor_price', 
            y='price', 
            color='demand_score',
            title="Internal App Valuation vs Competitor Benchmarks",
            labels={'competitor_price': 'Competitor Price ($)', 'price': 'Target Price ($)', 'demand_score': 'Demand Index'}
        )
        
        # Render responsive chart container using current Streamlit standards
        st.plotly_chart(fig, width='stretch')
        
        st.subheader("📋 Latest Operational Catalog Streams")
        st.dataframe(df_history.head(15), use_container_width=True)
    else:
        st.info("Cloud storage index currently empty. Fire the parallel scraper pipeline to seed data rows.")