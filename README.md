# Real-Time Dynamic Pricing Engine 📈

An end-to-end, production-grade Data Science pipeline that integrates live automated web scraping, machine learning regression modeling, and an interactive UI dashboard to calculate optimized retail prices on the fly.

Live Web Application: [https://dynamic-pricing-engine-p5u5f2mf5z6xtw5p33dvef.streamlit.app/]

---

## 🏗️ System Architecture

The application isolates processes into clean, modular layers to maintain industry-standard machine learning practices:

1. **Data Ingestion Layer (`scraper.py`)**: A live ETL script utilizing BeautifulSoup and Requests to extract real-world product data from active e-commerce web layers while handling runtime encoding transformations (`utf-8`).
2. **Feature & ML Pipeline (`train.py`)**: Ingests unstructured scraped data, targets high-cardinality values using OneHotEncoding, standardizes continuous elements using StandardScaler, and trains a high-performance XGBoost Regressor.
3. **User Interface Layer (`app.py`)**: A visual analytical dashboard built with Streamlit allowing stakeholders to fine-tune market parameters (demand, competitor indexing) and evaluate instant model predictions.
4. **Containerization (`Dockerfile`)**: Complete software configuration using Docker to freeze dependencies and guarantee platform-agnostic deployments.

---

## 🛠️ Tech Stack & Tooling

* **Core Language:** Python 3.10
* **Data Processing & Scrape Processing:** Pandas, NumPy, BeautifulSoup4, Requests
* **Machine Learning & Pipeline Serialization:** XGBoost, Scikit-Learn, Joblib
* **Interface & Version Control:** Streamlit, Docker, Git

---

## 🚀 Local Execution Guide

To clone and execute this project locally on your machine, launch your terminal window and execute the following steps:

### 1. Initialize and Install Software Packages
# Install all required data science frameworks
pip install -r requirements.txt

2. Trigger ETL Data Scraping & Model Training
# Pulls live data, saves raw_prices.csv, and exports trained model weights
python train.py

3. Run the Live Visual UI
# Launches the browser interface on localhost:8501
streamlit run app.py

🐋 Production Deployment with Docker
To isolate this ecosystem inside a container environment without conflicting with local machine libraries, use these commands:

# Build the application container image
docker build -t dynamic-pricing-engine .

# Initialize container mapping onto network port 8501
docker run -p 8501:8501 dynamic-pricing-engine

📊 Core Feature Implementations

Live Web Scraping: Bypasses character artifacts (Â) during response text extraction to guarantee clean numerical conversions.

Feature Engineering: Injecting field-specific economic variances (e.g., weekend premiums, surge multipliers) to train the model on real-world competitive supply-and-demand mechanics.

Low Inference Latency: Model architecture states are stored via serialized binary tree footprints (.json and .pkl) to enable sub-second prediction responses.

---

### 📤 How to save and send it to GitHub:

1. Open your **`README.md`** file in VS Code.
2. Paste everything you just copied into that file.
3. Press **`Ctrl + S`** (or `Cmd + S` on Mac) to save the file.
4. Open your bottom VS Code terminal, type these three final commands one by one, and press **Enter** after each:

git add README.md.
git commit -m "Docs: Complete final project release documentation".
git push origin main.
