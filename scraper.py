import asyncio
import aiohttp
from bs4 import BeautifulSoup
import numpy as np
import psycopg2 # Swapped from sqlite3 to psycopg2
import os
import time

# Safely read database coordinates from environment variables (fallback to localhost for local testing)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "pricing_analytics")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASSWORD", "supersecretpassword")

def init_db():
    # Establish connection to the PostgreSQL server container
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    cursor = conn.cursor()
    # Create enterprise-ready relational table schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_prices (
            id SERIAL PRIMARY KEY,
            product_name TEXT,
            demand_score REAL,
            competitor_price REAL,
            day_of_week VARCHAR(10),
            price REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

async def fetch_page_data(session, url, page_number):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        async with session.get(url, headers=headers, timeout=10) as response:
            if response.status != 200: return []
            
            html = await response.text(encoding='utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            products = soup.find_all('article', class_='product_pod')
            
            page_records = []
            for index, item in enumerate(products):
                title = item.h3.a['title']
                raw_price = item.find('p', class_='price_color').text
                clean_price = float(raw_price.replace('£', '').replace('$', '').replace('Â', '').strip())
                
                np.random.seed(index + page_number)
                demand_score = np.round(np.random.uniform(2.0, 9.5), 1)
                competitor_margin = np.random.uniform(-10.0, 15.0)
                competitor_price = np.round(clean_price + competitor_margin, 2)
                day_of_week = np.random.choice(['Weekday', 'Weekend'], p=[0.7, 0.3])
                
                page_records.append((title, demand_score, competitor_price, day_of_week, clean_price))
            return page_records
    except Exception as e:
        print(f"Error scraping page {page_number}: {e}")
        return []

async def scrape_all_targets():
    init_db()
    base_url = "https://books.toscrape.com/catalogue/page-{}.html"
    urls_to_scrape = [base_url.format(page) for page in range(1, 5)]
    
    start_time = time.time()
    print("Step 1: Spawning parallel async loops pointing to production PostgreSQL...")
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_page_data(session, url, i) for i, url in enumerate(urls_to_scrape, start=1)]
        all_results = await asyncio.gather(*tasks)
        
    final_records = [record for page_list in all_results for record in page_list]
    
    if final_records:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cursor = conn.cursor()
        # Using PostgreSQL specific batch placeholder syntax (%s instead of ?)
        cursor.executemany('''
            INSERT INTO product_prices (product_name, demand_score, competitor_price, day_of_week, price)
            VALUES (%s, %s, %s, %s, %s)
        ''', final_records)
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"📁 Success: Logged {len(final_records)} records asynchronously into PostgreSQL container!")
        return True
    return False

def scrape_live_marketplace():
    return asyncio.run(scrape_all_targets())

if __name__ == "__main__":
    scrape_live_marketplace()