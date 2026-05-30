import pandas as pd
import requests
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import xgboost as xgb
import joblib
from scraper import scrape_live_marketplace
import streamlit as st

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    SUPABASE_URL = "https://bmsrfnjpaqxmegxwbhum.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJtc3JmbG5qcGFxeG1lZ3h3Ymh1bSIsInJvbGUiOiJhbm9uIiwiaWF0IjoxNzE2OTU2NDA0LCJleHAiOjIwMzI1MzI0MDR9.YOUR_ANON_KEY_FROM_DASHBOARD"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

def execute_ml_pipeline():
    print("Step 1: Invoking parallel scraper module...")
    if not scrape_live_marketplace():
        print("❌ Scraper routine returned empty dataset.")
        return

    print("Step 2: Fetching consolidated dataset via API...")
    response = requests.get(f"{SUPABASE_URL}/rest/v1/product_prices?select=*", headers=headers)
    
    if response.status_code != 200:
        print("❌ Cloud fetch failed.")
        return
        
    df = pd.DataFrame(response.json())
    if df.empty:
        print("❌ Database table verified empty.")
        return

    print(f"Processing {len(df)} rows for model fitting...")
    X = df[['demand_score', 'competitor_price', 'day_of_week']]
    y = df['price']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
    
    preprocessor = ColumnTransformer(transformers=[
        ('num', StandardScaler(), ['demand_score', 'competitor_price']),
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['day_of_week'])
    ])
    
    X_train_processed = preprocessor.fit_transform(X_train)
    
    print("Step 3: Training XGBoost Core Architecture...")
    model = xgb.XGBRegressor(n_estimators=150, learning_rate=0.06, max_depth=4, random_state=42)
    model.fit(X_train_processed, y_train)
    
    os.makedirs('models', exist_ok=True)
    joblib.dump(preprocessor, 'models/preprocessor.pkl')
    model.save_model('models/pricing_xgb_model.json')
    print("🎯 Model training complete! Production configurations saved.")

if __name__ == "__main__":
    execute_ml_pipeline()