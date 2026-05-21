# 🌾 Agri-Vision: Smart Agriculture Predictive Analytics & Conversational AI Dashboard

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Gemini](https://img.shields.io/badge/Gemini%202.5%20Flash--Lite-AI-blueviolet?style=for-the-badge&logo=google-gemini&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Machine Learning](https://img.shields.io/badge/ML-RandomForest%20%7C%20XGBoost-FF6F00?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](https://opensource.org/licenses/MIT)

**Agri-Vision** is a next-generation, high-fidelity data-driven dashboard and advisory platform engineered to empower modern Indian farmers with state-of-the-art predictive analytics and interactive conversational AI. Combining four distinct Machine Learning models with the power of the **Gemini 2.5 Flash-Lite LLM**, Agri-Vision transforms raw soil chemistry, location, and seasonal parameters into highly actionable financial forecasts, agricultural suggestions, and automated government subsidy discoveries.

---

## 🚀 Key Features

### 1. 🧠 Multi-Model Predictive Machine Learning Pipeline
Instead of relying on a single generic model, Agri-Vision coordinates an ensemble of custom-trained ML models to deliver 360-degree forecasts:
*   **Top-3 Crop Recommendation Engine** (*Random Forest Classifier*): Evaluates Soil Chemistry ($N$, $P$, $K$, $pH$), automated weather readings, seasonal data, and rainfall to predict the top 3 most viable crops with exact confidence/probability percentages.
*   **Precision Yield Estimator** (*Random Forest Regressor*): Computes expected crop yield in quintals per hectare (Qtl/ha) under current parameters.
*   **Cultivation Cost Forecaster** (*Random Forest Regressor*): Projects the base cost of cultivation, augmented by a custom compound inflation model (`inflation.pkl`) specifically tailored for premium/fruit crops (e.g., Mango, Banana, Grapes, Apple, Papaya, Orange).
*   **Market Price Trend Forecaster** (*XGBoost Regressor*): Forecasts monthly market prices per quintal, dynamically adjusting for seasonal price factors and anomalies across a May–December harvesting timeline.

### 2. 📊 High-Fidelity Glassmorphism Dashboard
*   **Crop Comparison Engine**: A detailed side-by-side assessment of the top 3 predicted crops, outlining yield, total costs, projected revenues, and net profits.
*   **Interactive Financial Modeling**: Displays Best-Case, Average, and Worst-Case financial outcomes to prepare farmers for weather or market volatility.
*   **Chart.js Data Visualizations**: Custom, responsive dark-mode charts showing:
    *   *Monthly Revenue Trends* across the harvesting season.
    *   *Cultivation Cost Breakdown* (Seeds, fertilizers, manure, pesticide, irrigation, machinery, and misc costs).
    *   *State-Specific Historical Market Price Trends* pulled from genuine agricultural pricing databases.
*   **Automated District-wise Rainfall**: Integrates an annual rainfall database (`data/district_rainfall.csv`) covering Indian states and districts, automatically pre-filling moisture inputs or allowing granular manual overrides.
*   **Live Weather Integration**: Connects to the OpenWeatherMap API to retrieve current real-time temperature, humidity, and a 5-day predictive weather forecast.

### 3. 🛡️ State-Aware AI Agri-Bot Chatbot
*   **Context-Engineered Advisory**: Agri-Bot automatically ingests the live dashboard context (current Soil NPK, pH, district, temperature, predicted crops, estimated yield, and projected financial stats). The farmer can talk directly to it without repeating any parameters.
*   **Language-Agnostic Support**: Built-in support for both English and Hindi. The chatbot automatically responds in the language in which the farmer asks.
*   **Self-Throttling Rate Limiter**: Multi-threaded queue-based rate limiter capping API queries to a maximum of 14 requests per minute, preventing free-tier quota limits from interrupting service.
*   **Intelligent Offline Fallback**: In case of network interruptions or API limits, a smart keyword routing engine takes over offline to provide robust advice regarding fertilizers, soil amendments, price queries, and water management.

### 4. 📋 Dynamic Soil Health Diagnostics & Scheme Finder
*   **Soil Nutrient Action Report**: Instantly flags Soil deficiencies ($N$, $P$, or $K$ deficits, acidic/alkaline soils) and recommends precise chemical/organic treatments (e.g., Urea, DAP, MOP, Lime, Gypsum, Compost).
*   **Explainable AI (XAI)**: Demystifies model predictions by generating a natural language explanation of *why* the crop was recommended based on chemical benchmarks.
*   **Government Schemes Recommender**: Queries an extensive database (`data/government_schemes.json`) to isolate Central, State-specific, Crop-specific, and Condition-based (e.g., low-rainfall, poor soil) schemes (such as *PM-KISAN*, *PM Fasal Bima Yojana*, etc.) that the farmer qualifies for.
*   **One-Click PDF Export**: Uses `html2pdf.js` to compile the entire dashboard, predictions, financial breakdowns, and advisor insights into a beautifully structured, print-ready PDF Intelligence Report.

---

## 🛠️ Technology Stack

*   **Backend**: Python 3.9+, Flask Web Framework
*   **Frontend**: HTML5, Vanilla CSS3 (Custom Glassmorphism UI & Dark Mode), Javascript (ES6)
*   **Machine Learning**: Scikit-Learn (Random Forest Models), XGBoost (Price Regressor), NumPy, Pandas
*   **Generative AI**: Google Gemini 2.5 Flash-Lite LLM (`google-genai` SDK)
*   **APIs**: OpenWeatherMap API, Google Gemini Developer API
*   **Libraries**: Chart.js (Data Analytics), html2pdf.js (PDF Generation)

---

## 📂 Directory Structure

```directory
Agri_vision/
├── app.py                      # Flask main server application, routes, and chatbot logic
├── config.py                   # API Configuration (Gemini & OpenWeatherMap credentials)
├── train_model.py              # ML Pipeline Training script (generates models from CSVs)
├── crop_model.pkl              # Random Forest Classifier (Crop Recommendation)
├── yield_model.pkl             # Random Forest Regressor (Yield Forecast)
├── cost_model.pkl              # Random Forest Regressor (Cultivation Cost Prediction)
├── price_model.pkl             # XGBoost Regressor (Market Price Forecasting)
├── crop_encoding.pkl           # Crop category label encoding mappings
├── inflation.pkl               # Computed crop-specific inflation multipliers
├── data/
│   ├── district_rainfall.csv                  # Indian district-level average annual rainfall database
│   ├── final_cost_of_cultivation_with_fruits.csv  # Base cost datasets of agricultural inputs
│   ├── final_crop_recommendation.csv          # Core dataset containing soil chemistry parameters
│   ├── final_revenue.csv                      # Ministry pricing, state-wise crop market rate histories
│   └── government_schemes.json                # State, Central, and crop-specific agricultural schemes
├── static/
│   ├── css/
│   │   └── style.css           # Modern Dark-Mode and Glassmorphism styling rules
│   └── js/
│       └── translations.js     # Multi-lingual UI localization mapping engine
└── templates/
    ├── index.html              # Main landing and soil parameters input form page
    └── result.html             # Multi-tab analytics results page with charts and AI chat
```

---

## ⚙️ Installation & Setup

Follow these simple steps to set up and run Agri-Vision locally on your machine:

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/Agri-Vision.git
cd Agri-Vision
```

### 2. Configure Virtual Environment & Install Dependencies
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt
```
*(Note: If `requirements.txt` is missing, run: `pip install flask pandas numpy scikit-learn xgboost requests google-genai`)*

### 3. Add API Keys
Create or open the `config.py` file in the root folder and insert your OpenWeatherMap and Google Gemini API credentials:
```python
# config.py
weather_api_key = "YOUR_OPENWEATHERMAP_API_KEY"
gemini_api_key  = "YOUR_GEMINI_API_KEY"
```

### 4. Start the Application
```bash
python app.py
```
The application will launch in debug mode. Open your browser and navigate to:
```url
http://127.0.0.1:5000/
```

---

## 📈 Model Training Pipeline

Agri-Vision comes preloaded with pre-trained models. However, if you add new agricultural data to the `data/` directory or wish to retrain the models from scratch:

1. Ensure your updated `.csv` files are saved in the `data/` folder following the original schemas.
2. Execute the training script:
```bash
python train_model.py
```
This script will:
*   Automatically parse and clean crop recommendation, cost, and historical revenue tables.
*   Compute and dump crop-specific inflation indices (`inflation.pkl`).
*   Train three Random Forest models (`crop_model.pkl`, `yield_model.pkl`, `cost_model.pkl`).
*   Train the XGBoost regressor for monthly market price forecasting (`price_model.pkl`).
*   Verify model files and save category mapping files (`crop_encoding.pkl`).

---

## 📄 License & Acknowledgements

*   **License**: Distributed under the MIT License. See `LICENSE` for details.
*   **Data Sources**: Datasets compile raw records sourced from the Indian Ministry of Agriculture and district meteorological offices.
*   **LLM Provider**: Special thanks to **Google Gemini** for powering the smart Agri-Bot conversational companion!
