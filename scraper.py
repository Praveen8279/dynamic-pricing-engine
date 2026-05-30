import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os

def scrape_live_marketplace():
    print("Step 1: Initializing live web scraping...")
    
    url = "https://books.toscrape.com/catalogue/page-1.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8' # Forces correct character parsing
        
        if response.status_code != 200:
            print(f"Connection failed. Error code: {response.status_code}")
            return False
            
        soup = BeautifulSoup(response.text, 'html.parser')
        products = soup.find_all('article', class_='product_pod')
        
        scraped_data = []
        print(f"Step 2: Found {len(products)} live products. Extracting features...")
        
        for index, item in enumerate(products):
            title = item.h3.a['title']
            raw_price = item.find('p', class_='price_color').text
            
            # Clean data: removes currency symbols AND encoding artifacts like 'Â'
            clean_price = float(raw_price.replace('£', '').replace('$', '').replace('Â', '').strip())
            
            np.random.seed(index)
            demand_score = np.round(np.random.uniform(2.0, 9.5), 1)
            competitor_margin = np.random.uniform(-10.0, 15.0)
            competitor_price = np.round(clean_price + competitor_margin, 2)
            day_of_week = np.random.choice(['Weekday', 'Weekend'], p=[0.7, 0.3])
            
            scraped_data.append({
                'product_name': title,
                'demand_score': demand_score,
                'competitor_price': competitor_price,
                'day_of_week': day_of_week,
                'price': clean_price
            })
            
        df = pd.DataFrame(scraped_data)
        os.makedirs('data', exist_ok=True)
        df.to_csv('data/raw_prices.csv', index=False)
        print("📁 Success: Live data saved to data/raw_prices.csv!")
        return True
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    scrape_live_marketplace()