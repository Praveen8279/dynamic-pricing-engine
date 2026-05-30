import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import xgboost as xgb
import joblib
import os
from scraper import scrape_live_marketplace

def execute_ml_pipeline():
    # 1. Run the scraper first to fetch fresh data
    success = scrape_live_marketplace()
    if not success:
        print("Pipeline stopped: Data collection failed.")
        return

    # 2. Ingest the newly scraped data
    print("Step 3: Loading data into machine learning pipeline...")
    df = pd.read_csv('data/raw_prices.csv')
    
    # Separate input features (X) and target output price (y)
    X = df[['demand_score', 'competitor_price', 'day_of_week']]
    y = df['price']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
    
    # 3. Data Preprocessing (Scaling numbers and encoding text labels)
    numeric_features = ['demand_score', 'competitor_price']
    categorical_features = ['day_of_week']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])
    
    X_train_processed = preprocessor.fit_transform(X_train)
    
    # 4. Model Training using XGBoost Regressor
    print("Step 4: Training XGBoost Machine Learning model...")
    model = xgb.XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=5, random_state=42)
    model.fit(X_train_processed, y_train)
    
    # 5. Save model artifacts so our UI can use them later
    os.makedirs('models', exist_ok=True)
    joblib.dump(preprocessor, 'models/preprocessor.pkl')
    model.save_model('models/pricing_xgb_model.json')
    print("🎯 Success: Production ML model saved in /models folder!")

if __name__ == "__main__":
    execute_ml_pipeline()