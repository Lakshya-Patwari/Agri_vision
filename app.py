from flask import Flask, render_template, request, jsonify
import json
import pandas as pd
import pickle
import requests
import config
from datetime import datetime
import math
import numpy as np
import time
import threading
from collections import deque
from google import genai
from google.genai import types

app = Flask(__name__)

# --------------------------------
# GEMINI SETUP (once at startup)
# --------------------------------
GEMINI_SYSTEM_PROMPT = (
    "You are Agri-Bot, an expert Indian agricultural consultant and agronomist embedded inside the "
    "Agri-Vision AI dashboard. Give concise, practical, and warm advice to Indian farmers about:\n"
    "- Crop selection, soil health, and fertilizers\n"
    "- Market prices and revenue forecasts\n"
    "- Pest management and irrigation\n"
    "- Government schemes (PM-KISAN, Fasal Bima Yojana, etc.)\n"
    "- Climate and seasonal impact on farming\n\n"
    "Rules:\n"
    "- Respond in 2-4 short paragraphs. Be concise and actionable.\n"
    "- Use Indian context: rupees (\u20b9), quintals, hectares, kharif/rabi seasons.\n"
    "- If the user writes in Hindi, respond in Hindi.\n"
    "- Never make up data. If unsure, suggest consulting a local KVK (Krishi Vigyan Kendra).\n"
)

try:
    _genai_client = genai.Client(api_key=config.gemini_api_key)
except Exception as _e:
    print(f"[Agri-Bot] Gemini client init warning: {_e}")
    _genai_client = None

GEMINI_MODEL = "gemini-2.5-flash-lite"

# Simple rate limiter: max 14 calls per 60s window (free tier limit is 15/min)
_rate_lock       = threading.Lock()
_call_timestamps = deque()   # timestamps of recent Gemini calls

def _gemini_rate_wait():
    """Block until it's safe to make another Gemini call without hitting quota."""
    with _rate_lock:
        now = time.time()
        # Remove entries older than 60s
        while _call_timestamps and now - _call_timestamps[0] > 60:
            _call_timestamps.popleft()
        if len(_call_timestamps) >= 14:
            wait_for = 60 - (now - _call_timestamps[0]) + 0.5
            if wait_for > 0:
                time.sleep(wait_for)
            # Clean up again after sleeping
            now2 = time.time()
            while _call_timestamps and now2 - _call_timestamps[0] > 60:
                _call_timestamps.popleft()
        _call_timestamps.append(time.time())


# -------------------------------
# LOAD MODELS & DATA
# -------------------------------
crop_model = pickle.load(open("crop_model.pkl", "rb"))
yield_model = pickle.load(open("yield_model.pkl", "rb"))
cost_model = pickle.load(open("cost_model.pkl", "rb"))
price_model = pickle.load(open("price_model.pkl", "rb"))
crop_encoding = pickle.load(open("crop_encoding.pkl", "rb"))
inflation_rates = pickle.load(open("inflation.pkl", "rb"))

# Load State-Specific Revenue Data
try:
    revenue_df = pd.read_csv("data/final_revenue.csv")
    revenue_df['Commodity'] = revenue_df['Commodity'].str.strip().str.lower()
    revenue_df['Month_Name'] = revenue_df['Month'].str.split('-').str[0]
    state_prices = revenue_df.groupby(['State', 'Commodity', 'Month_Name'])['Modal Price 01-01-2024 to 10-04-2026'].mean().to_dict()
    
    # Create historical prices mapping for charts
    historical_prices = {}
    for _, row in revenue_df.iterrows():
        s, c, m, p = row['State'], row['Commodity'], row['Month'], row['Modal Price 01-01-2024 to 10-04-2026']
        key = (s, c)
        if key not in historical_prices:
            historical_prices[key] = {}
        historical_prices[key][m] = p

except Exception as e:
    print(f"Could not load state pricing data: {e}")
    state_prices = {}
    historical_prices = {}

# Load District-wise Rainfall Data
try:
    rainfall_df = pd.read_csv("data/district_rainfall.csv")
    # Clean up state names to match our frontend dropdown
    state_map = {
        "ORISSA": "Odisha",
        "CHATISGARH": "Chattisgarh",
        "UTTARANCHAL": "Uttarakhand",
        "HIMACHAL": "Himachal Pradesh",
        "DELHI": "NCT of Delhi",
        "ANDAMAN AND NICOBAR": "Andaman and Nicobar",
        "PONDICHERRY": "Pondicherry"
    }
    rainfall_df['STATE_UT_NAME'] = rainfall_df['STATE_UT_NAME'].apply(lambda x: state_map.get(x, x.title()))
    rainfall_df['DISTRICT'] = rainfall_df['DISTRICT'].str.title()
    
    # Create mapping: {State: {District: Rainfall}}
    district_rainfall = {}
    districts_by_state = {} # For frontend dropdown
    for _, row in rainfall_df.iterrows():
        s, d, r = row['STATE_UT_NAME'], row['DISTRICT'], row['ANNUAL']
        if s not in district_rainfall:
            district_rainfall[s] = {}
            districts_by_state[s] = []
        district_rainfall[s][d] = r
        districts_by_state[s].append(d)
        
    # Handle Telangana (using AP data as proxy for common districts)
    if "Andhra Pradesh" in districts_by_state:
        districts_by_state["Telangana"] = districts_by_state["Andhra Pradesh"]
        district_rainfall["Telangana"] = district_rainfall["Andhra Pradesh"]
        
except Exception as e:
    print(f"Could not load district rainfall data: {e}")
    district_rainfall = {}
    districts_by_state = {}

# Load Government Schemes Database
try:
    with open("data/government_schemes.json", "r", encoding="utf-8") as f:
        schemes_db = json.load(f)
except Exception as e:
    print(f"Could not load government schemes: {e}")
    schemes_db = {"central_schemes": [], "crop_schemes": {}, "state_schemes": {}, "condition_schemes": []}

# accuracy (optional)
try:
    accuracy = pickle.load(open("accuracy.pkl", "rb"))
except:
    accuracy = 0

# -------------------------------
# CONSTANTS
# -------------------------------
season_map = {"Kharif": 0, "Rabi": 1, "Summer": 2}

special_crops = [
    "banana", "mango", "grapes", "apple",
    "orange", "papaya", "coconut", "dagussa"
]

crop_npk_priority = {
    "rice": "N",
    "wheat": "NP",
    "maize": "N",
    "cotton": "K",
    "sugarcane": "NK",
    "banana": "K",
    "mango": "P",
    "grapes": "K"
}

# -------------------------------
def get_season():
    m = datetime.now().month
    if m in [6,7,8,9]:
        return "Kharif"
    elif m in [10,11,12,1]:
        return "Rabi"
    else:
        return "Summer"

# -------------------------------
def get_relevant_schemes(crop_name, state, rainfall, problems_count):
    """Return filtered government schemes relevant to this prediction."""
    result = {
        "central": schemes_db.get("central_schemes", []),
        "crop_specific": [],
        "state_specific": [],
        "condition_based": []
    }

    # Crop-specific schemes
    crop_lower = crop_name.lower()
    result["crop_specific"] = schemes_db.get("crop_schemes", {}).get(crop_lower, [])

    # State-specific schemes
    result["state_specific"] = schemes_db.get("state_schemes", {}).get(state, [])

    # Condition-based schemes
    for scheme in schemes_db.get("condition_schemes", []):
        if scheme["condition"] == "low_rainfall" and rainfall < scheme.get("threshold_below", 700):
            result["condition_based"].append(scheme)
        elif scheme["condition"] == "poor_soil" and problems_count > scheme.get("threshold_above", 1):
            result["condition_based"].append(scheme)

    return result

# -------------------------------
def weather_fetch(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={config.weather_api_key}"
        data = requests.get(url, timeout=5).json()

        temp = data["main"]["temp"] - 273.15
        humidity = data["main"]["humidity"]

    except:
        temp, humidity = 25, 50

    return temp, humidity

# -------------------------------
def forecast_fetch(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={config.weather_api_key}&units=metric"
        data = requests.get(url, timeout=5).json()
        
        forecast_data = []
        seen_days = set()
        
        for item in data.get("list", []):
            dt_txt = item["dt_txt"]
            date_obj = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
            day_name = date_obj.strftime("%Y-%m-%d")
            
            # Prefer midday readings
            if day_name not in seen_days and ("09:00:00" in dt_txt or "12:00:00" in dt_txt or "15:00:00" in dt_txt):
                seen_days.add(day_name)
                forecast_data.append({
                    "day": date_obj.strftime("%a"),
                    "temp": round(item["main"]["temp"]),
                    "icon": item["weather"][0]["icon"],
                    "desc": item["weather"][0]["main"]
                })
            
            if len(forecast_data) == 5:
                break
                
        # If the API didn't return expected times, just take the first reading of new days
        if len(forecast_data) < 5:
            seen_days = set()
            forecast_data = []
            for item in data.get("list", []):
                dt_txt = item["dt_txt"]
                date_obj = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
                day_name = date_obj.strftime("%Y-%m-%d")
                if day_name not in seen_days:
                    seen_days.add(day_name)
                    forecast_data.append({
                        "day": date_obj.strftime("%a"),
                        "temp": round(item["main"]["temp"]),
                        "icon": item["weather"][0]["icon"],
                        "desc": item["weather"][0]["main"]
                    })
                if len(forecast_data) == 5:
                    break
                    
    except Exception as e:
        print(f"Forecast fetch error: {e}")
        forecast_data = []

    return forecast_data

# -------------------------------
@app.route("/")
def index():
    return render_template("index.html", districts_by_state=districts_by_state, district_rainfall=district_rainfall)

# -------------------------------
@app.route("/predict", methods=["POST"])
def predict():

    # -------------------------------
    # INPUT
    # -------------------------------
    N = float(request.form["nitrogen"])
    P = float(request.form["phosphorous"])
    K = float(request.form["potassium"])
    ph = float(request.form["ph"])
    city = request.form["city"]
    state = request.form.get("state", "")
    district = request.form.get("district", "")

    # -------------------------------
    # AUTOMATED RAINFALL
    # -------------------------------
    manual_rainfall = request.form.get("rainfall_input", "").strip()
    if manual_rainfall:
        rainfall = float(manual_rainfall)
    else:
        # Use district-wise rainfall if available, else fallback to 1000mm
        rainfall = district_rainfall.get(state, {}).get(district, 1000.0)

    # -------------------------------
    # WEATHER + SEASON
    # -------------------------------
    season = get_season()
    season_encoded = season_map[season]

    temp, humidity = weather_fetch(city)
    forecast_data = forecast_fetch(city)

    # -------------------------------
    # INPUT DATAFRAME
    # -------------------------------
    data = pd.DataFrame([{
        "N": N,
        "P": P,
        "K": K,
        "temperature": temp,
        "humidity": humidity,
        "ph": ph,
        "rainfall": rainfall,
        "season_encoded": season_encoded,
        "month": datetime.now().month
    }])

    # -------------------------------
    # CROP PREDICTION (TOP 3)
    # -------------------------------
    try:
        probs = crop_model.predict_proba(data)[0]
        classes = crop_model.classes_
        top3_idx = np.argsort(probs)[-3:][::-1]
        top3_crops = [classes[i] for i in top3_idx]
        top3_probs = [round(probs[i] * 100, 2) for i in top3_idx]
    except:
        crop_fallback = crop_model.predict(data)[0]
        top3_crops = [crop_fallback, crop_fallback, crop_fallback]
        top3_probs = [100.0, 0.0, 0.0]

    yield_pred = max(0, yield_model.predict(data)[0])  # quintal/hectare
    base_cost = max(0, cost_model.predict(data)[0])

    top3_data = []

    for idx, crop in enumerate(top3_crops):
        crop_code = crop_encoding.get(crop, 0)
        confidence = top3_probs[idx]

        # COST
        inflation = inflation_rates.get(crop, 0.05)
        years_diff = 6
        if crop in special_crops:
            total_cost = base_cost * ((1 + inflation) ** years_diff)
        else:
            total_cost = base_cost

        # MONTHLY REVENUE
        months = {5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
        monthly_revenue = {}
        price_source = "Generic ML Estimate"

        for m in range(5, 13):
            month_name = months[m]
            state_key = (state, crop.lower(), month_name)
            
            if state_key in state_prices:
                price_pred = state_prices[state_key]
                price_source = f"Accurate for {state} (Market Data)"
            else:
                price_pred = price_model.predict([[m, crop_code]])[0]
                if crop in special_crops:
                    seasonal_factor = 1 + 0.25 * math.sin((m-1)*(2*math.pi/12))
                    price_pred *= seasonal_factor

            revenue = yield_pred * price_pred
            monthly_revenue[month_name] = round(max(0, revenue), 2)

        avg_revenue = sum(monthly_revenue.values()) / len(monthly_revenue)
        profit = avg_revenue - total_cost

        best_case_revenue = (avg_revenue * 1.15) * 1.05
        best_case_profit = best_case_revenue - total_cost

        worst_case_revenue = (avg_revenue * 0.75) * 0.90
        worst_case_profit = worst_case_revenue - total_cost

        hist_key = (state, crop.lower())
        price_history = historical_prices.get(hist_key, {})

        top3_data.append({
            "name": crop,
            "confidence": confidence,
            "yield": yield_pred,
            "total_cost": total_cost,
            "monthly_revenue": monthly_revenue,
            "price_source": price_source,
            "price_history": price_history,
            "avg_revenue": avg_revenue,
            "profit": profit,
            "best_case_profit": best_case_profit,
            "worst_case_profit": worst_case_profit,
            "best_case_revenue": best_case_revenue,
            "worst_case_revenue": worst_case_revenue
        })

    # SOIL ANALYSIS & EXPLAINABLE AI (Based on 1st Crop)
    problems = []
    fertilizer_tips = []
    ai_reasons = []
    primary_crop = top3_crops[0]

    if N < 40:
        problems.append("Nitrogen deficiency")
        fertilizer_tips.append("Apply Urea")
    elif N > 80:
        ai_reasons.append(f"High Nitrogen levels ({N}) strongly support {primary_crop}'s vegetative growth.")
    else:
        ai_reasons.append(f"Adequate Nitrogen ({N}) provides a good baseline for {primary_crop}.")

    if P < 40:
        problems.append("Phosphorus deficiency")
        fertilizer_tips.append("Apply DAP")
    
    if K < 40:
        problems.append("Potassium deficiency")
        fertilizer_tips.append("Apply MOP")
    elif K > 60:
        ai_reasons.append(f"Rich Potassium ({K}) aids in disease resistance for this crop.")

    if ph < 5.5:
        problems.append("Soil is acidic")
        fertilizer_tips.append("Add lime")
    elif ph > 7.5:
        problems.append("Soil is alkaline")
        fertilizer_tips.append("Add gypsum")
    else:
        ai_reasons.append(f"Optimal pH ({ph}) maximizes nutrient availability.")

    if not problems:
        problems.append("Soil is balanced")
        fertilizer_tips.append("Maintain compost")

    ai_reasons.append(f"The entered rainfall ({rainfall}) aligns well with the moisture requirements for {primary_crop}.")

    ai_explanation = " ".join(ai_reasons)

    # Get relevant government schemes
    problems_count = len([p for p in problems if p != "Soil is balanced"])
    relevant_schemes = get_relevant_schemes(primary_crop, state, rainfall, problems_count)

    primary_cost = top3_data[0]["total_cost"]
    seed_cost = primary_cost * 0.15
    fertilizer_cost = primary_cost * 0.20
    manure_cost = primary_cost * 0.10
    pesticide_cost = primary_cost * 0.15
    irrigation_cost = primary_cost * 0.15
    machinery_cost = primary_cost * 0.15
    misc_cost = primary_cost * 0.10

    # -------------------------------
    return render_template(
        "result.html",
        top3_data=top3_data,
        primary_crop=top3_data[0],
        
        detected_rainfall=round(rainfall, 2),
        temperature=temp,
        humidity=humidity,
        season=season,

        seed_cost=seed_cost,
        fertilizer_cost=fertilizer_cost,
        manure_cost=manure_cost,
        pesticide_cost=pesticide_cost,
        irrigation_cost=irrigation_cost,
        machinery_cost=machinery_cost,
        misc_cost=misc_cost,

        N=N, P=P, K=K, ph=ph, rainfall=rainfall,
        problems=problems,
        fertilizer_tips=fertilizer_tips,
        ai_explanation=ai_explanation,

        accuracy=accuracy,
        forecast_data=forecast_data,
        schemes=relevant_schemes
    )

# -----------------------------------------------
# CHATBOT API ENDPOINT  (Gemini 2.0 Flash powered)
# -----------------------------------------------
@app.route('/chat', methods=['POST'])
def chat_api():
    try:
        data       = request.json
        user_msg   = data.get('message', '').strip()
        context    = data.get('context', {})
        history    = data.get('history', [])   # [{"role":"user/model", "text":"..."}]

        if not user_msg:
            return jsonify({"response": "Please type a message first!"})

        top_crop  = context.get('top_crop', 'Unknown')
        ctx_block = (
            f"[Dashboard Context]\n"
            f"- Recommended crop: {top_crop}\n"
            f"- Soil NPK: N={context.get('n','?')}  P={context.get('p','?')}  K={context.get('k','?')}\n"
            f"- Soil pH: {context.get('ph','?')}\n"
            f"- Estimated yield: {context.get('yield','?')} Qtl/ha\n"
            f"- Season: {context.get('season','?')}\n"
            f"- Temperature: {context.get('temp','?')}\u00b0C  |  Humidity: {context.get('humidity','?')}%\n"
            f"- Rainfall: {context.get('rainfall','?')} mm\n"
        )
        full_prompt = ctx_block + "\nFarmer's question: " + user_msg

        # ---- Try Gemini (new google-genai SDK) ----
        if _genai_client:
            try:
                # Build history in new SDK format
                chat_history = []
                for turn in history[-6:]:
                    role = "user" if turn.get("role") == "user" else "model"
                    chat_history.append(
                        types.Content(role=role, parts=[types.Part(text=turn.get("text", ""))])
                    )

                chat = _genai_client.chats.create(
                    model=GEMINI_MODEL,
                    config=types.GenerateContentConfig(
                        system_instruction=GEMINI_SYSTEM_PROMPT,
                        max_output_tokens=900,
                        temperature=0.7,
                        thinking_config=types.ThinkingConfig(thinking_budget=0),
                    ),
                    history=chat_history,
                )
                _gemini_rate_wait()   # self-throttle to stay under free tier quota
                response = chat.send_message(
                    full_prompt,
                    config=types.GenerateContentConfig(
                        http_options=types.HttpOptions(timeout=18000),
                    )
                )
                return jsonify({"response": response.text.strip()})

            except Exception as gem_err:
                print(f"[Agri-Bot] Gemini API error: {gem_err}")
                # Fall through to smart fallback

        # ---- Smart Fallback (offline) ----
        user_lower = user_msg.lower()
        if any(w in user_lower for w in ["why", "reason", "recommend"]):
            res = (f"Based on your soil \u2014 N:{context.get('n')}, P:{context.get('p')}, "
                   f"K:{context.get('k')}, pH:{context.get('ph')} \u2014 the model identified "
                   f"{top_crop} as the best fit for your field and current season.")
        elif any(w in user_lower for w in ["improve", "fix", "better", "soil"]):
            res = (f"To improve your soil for {top_crop}: balance NPK with urea/DAP/MOP, "
                   f"add organic compost, and ensure drainage. Contact your nearest KVK for a free soil test.")
        elif any(w in user_lower for w in ["price", "market", "revenue", "profit"]):
            res = (f"Projected revenue for {top_crop}: yield ~{context.get('yield','N/A')} Qtl/ha. "
                   f"See the monthly revenue chart on your dashboard for exact figures.")
        elif any(w in user_lower for w in ["fertilizer", "fertiliser", "urea", "dap", "npk"]):
            res = (f"For {top_crop} with your NPK levels, apply Urea (N), DAP (P), and MOP (K) "
                   f"in split doses as per state agriculture department guidelines.")
        elif any(w in user_lower for w in ["water", "irrigation", "rain"]):
            res = (f"Your area receives ~{context.get('rainfall','?')} mm annual rainfall. "
                   f"For {top_crop}, supplement with drip irrigation during dry spells.")
        else:
            res = (f"{top_crop} looks like a strong choice for your farm! "
                   f"Ask me about soil improvement, fertilizers, pricing, or irrigation.")

        return jsonify({"response": res})

    except Exception as e:
        print(f"[Agri-Bot] Unexpected error: {e}")
        return jsonify({"response": "Sorry, I ran into an issue. Please try again."}), 500

# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)