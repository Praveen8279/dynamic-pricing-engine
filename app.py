import streamlit as st
import pandas as pd
import numpy as np
import joblib
import xgboost as xgb

st.set_page_config(page_title="AI Dynamic Pricing Engine", layout="centered")
st.title("📈 Real-Time Dynamic Pricing Engine")
st.write("Adjust variables to check how your live trained ML model responds.")

@st.cache_resource
def load_artifacts():
    preprocessor = joblib.load('models/preprocessor.pkl')
    model = xgb.XGBRegressor()
    model.load_model('models/pricing_xgb_model.json')
    return preprocessor, model

try:
    preprocessor, model = load_artifacts()
    
    st.sidebar.header("Market Input Parameters")
    demand = st.sidebar.slider("Demand Score (1 = Low, 10 = Surge)", 1.0, 10.0, 5.0, step=0.1)
    comp_price = st.sidebar.number_input("Competitor's Price ($)", min_value=10.0, max_value=1000.0, value=50.0, step=1.0)
    day_type = st.sidebar.selectbox("Day of the Week", ["Weekday", "Weekend"])
    
    input_df = pd.DataFrame([{
        'demand_score': demand,
        'competitor_price': comp_price,
        'day_of_week': day_type
    }])
    
    processed_input = preprocessor.transform(input_df)
    predicted_price = model.predict(processed_input)[0]
    
    st.markdown("### Market Analysis Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Current Demand", f"{demand}/10")
    col2.metric("Competitor Price", f"${comp_price:,.2f}")
    col3.metric("Day Status", day_type)
    
    st.markdown("---")
    st.subheader("Recommended Selling Price")
    st.success(f"💰 **Optimal Retail Price: ${predicted_price:,.2f}**")

except FileNotFoundError:
    st.error("Model files not found! Please run 'python train.py' in your terminal first.")