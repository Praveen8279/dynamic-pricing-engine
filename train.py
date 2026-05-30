import pandas as pd
import psycopg2
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import xgboost as xgb
import joblib
from scraper import scrape_live_marketplace

# Environment variable lookups for secure container networking
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "pricing_analytics")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASSWORD", "supersecretpassword")

def execute_ml_pipeline():
    # 1. Trigger our new asynchronous PostgreSQL scraper
    if not scrape_live_marketplace(): 
        print("Scraping engine pass failed.")
        return

    # 2. Ingest structured features directly using a PostgreSQL connection
    print("Step 3: Querying historical features from production PostgreSQL engine...")
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    
    # Read database tables into a Pandas DataFrame
    df = pd.read_sql_query("SELECT * FROM product_prices", conn)
    conn.close()
    
    if df.empty:
        print("No records found in database to train on.")
        return
    
    X = df[['demand_score', 'competitor_price', 'day_of_week']]
    y = df['price']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
    
    preprocessor = ColumnTransformer(transformers=[
        ('num', StandardScaler(), ['demand_score', 'competitor_price']),
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['day_of_week'])
    ])
    
    X_train_processed = preprocessor.fit_transform(X_train)
    
    print("Step 4: Training XGBoost optimization algorithms...")
    model = xgb.XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=5, random_state=42)
    model.fit(X_train_processed, y_train)
    
    os.makedirs('models', exist_ok=True)
    joblib.dump(preprocessor, 'models/preprocessor.pkl')
    model.save_model('models/pricing_xgb_model.json')
    print("🎯 Success: Enterprise ML Pipeline execution complete!")

if __name__ == "__main__":
    execute_ml_pipeline()