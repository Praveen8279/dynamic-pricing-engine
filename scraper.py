import asyncio
import aiohttp
from bs4 import BeautifulSoup
import numpy as np
import requests
from datetime import datetime
import streamlit as st
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    SUPABASE_URL = "https://bmsrfnjpaqxmegxwbhum.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJtc3JmbmpwYXF4bWVneHdiaHVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODAxNTgzMTgsImV4cCI6MjA5NTczNDMxOH0.o742QJe6ivSsUvARoolRJqcapPPItF8PIOdw8y5ZPPI"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

async def fetch_page_data(session, url, page_number):
    client_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        async with session.get(url, headers=client_headers, timeout=10) as response:
            if response.status != 200: return []
            html = await response.text(encoding='utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            products = soup.find_all('article', class_='product_pod')
            
            page_records = []
            current_day = "Weekend" if datetime.now().weekday() >= 5 else "Weekday"
            
            for index, item in enumerate(products):
                title = item.h3.a['title']
                raw_price = item.find('p', class_='price_color').text
                clean_price = float(raw_price.replace('£', '').replace('$', '').replace('Â', '').strip())
                
                calculated_demand = round(min(9.8, max(1.5, 3.0 + (len(title) % 7))), 1)
                price_variance = -3.50 if index % 2 == 0 else 2.75
                competitor_price = round(max(1.00, clean_price + price_variance), 2)
                
                page_records.append({
                    "product_name": title,
                    "demand_score": calculated_demand,
                    "competitor_price": competitor_price,
                    "day_of_week": current_day,
                    "price": clean_price
                })
            return page_records
    except Exception:
        return []

async def scrape_all_targets():
    base_url = "https://books.toscrape.com/catalogue/page-{}.html"
    urls_to_scrape = [base_url.format(page) for page in range(1, 6)]
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_page_data(session, url, i) for i, url in enumerate(urls_to_scrape, start=1)]
        all_results = await asyncio.gather(*tasks)
        
    final_records = [record for page_list in all_results for record in page_list]
    
    if final_records:
        print(f" Collected {len(final_records)} live items across Levels 1-5.")
        response = requests.post(f"{SUPABASE_URL}/rest/v1/product_prices", headers=headers, json=final_records)
        if response.status_code in [200, 201]:
            return True
        else:
            print(f"API Error: {response.text}")
    return False

def scrape_live_marketplace():
    return asyncio.run(scrape_all_targets())

if __name__ == "__main__":
    print("🚀 Booting data ingestion engine...")
    if scrape_live_marketplace():
        print("✅ Success! Database updated.")