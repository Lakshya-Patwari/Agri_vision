from flask import Flask, render_template, request
import pandas as pd
import pickle
import requests
import config
from datetime import datetime
import math

app = Flask(__name__)

# -------------------------------
# LOAD MODELS
# -------------------------------
crop_model = pickle.load(open("crop_model.pkl", "rb"))
yield_model = pickle.load(open("yield_model.pkl", "rb"))
cost_model = pickle.load(open("cost_model.pkl", "rb"))
price_model = pickle.load(open("price_model.pkl", "rb"))
crop_encoding = pickle.load(open("crop_encoding.pkl", "rb"))
inflation_rates = pickle.load(open("inflation.pkl", "rb"))

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
@app.route("/")
def home():
    return render_template("index.html")

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
    rainfall = float(request.form["rainfall"])
    city = request.form["city"]

    # -------------------------------
    # WEATHER + SEASON
    # -------------------------------
    season = get_season()
    season_encoded = season_map[season]

    temp, humidity = weather_fetch(city)

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
    # CROP PREDICTION
    # -------------------------------
    crop = crop_model.predict(data)[0]
    crop_code = crop_encoding.get(crop, 0)
   
    try:
        probs = crop_model.predict_proba(data)
        confidence = round(max(probs[0]) * 100, 2)
    except:
        confidence = 0

    # -------------------------------
    # YIELD
    # -------------------------------
    yield_pred = max(0, yield_model.predict(data)[0])  # quintal/hectare

    # -------------------------------
    # PRICE (XGBOOST)
    # -------------------------------
    

    # -------------------------------
    # COST (WITH INFLATION)
    # -------------------------------
    inflation = inflation_rates.get(crop, 0.05)
    years_diff = 6

    base_cost = max(0, cost_model.predict(data)[0])

    if crop in special_crops:
        total_cost = base_cost * ((1 + inflation) ** years_diff)
    else:
        total_cost = base_cost

    # -------------------------------
    # MONTHLY REVENUE
    # -------------------------------
    months = {
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }

    monthly_revenue = {}

    for m in range(5, 13):

        price_pred = price_model.predict([[m, crop_code]])[0]
        if crop in special_crops:
            seasonal_factor = 1 + 0.25 * math.sin((m-1)*(2*math.pi/12))
            price_pred *= seasonal_factor

        revenue = yield_pred * price_pred

        monthly_revenue[months[m]] = round(max(0, revenue), 2)

    # -------------------------------
    # FINAL CALCULATIONS
    # -------------------------------
    avg_revenue = sum(monthly_revenue.values()) / len(monthly_revenue)
    profit = avg_revenue - total_cost

    # -------------------------------
    # COST BREAKDOWN
    # -------------------------------
    seed_cost = total_cost * 0.15
    fertilizer_cost = total_cost * 0.20
    manure_cost = total_cost * 0.10
    pesticide_cost = total_cost * 0.15
    irrigation_cost = total_cost * 0.15
    machinery_cost = total_cost * 0.15
    misc_cost = total_cost * 0.10

    # -------------------------------
    # SOIL ANALYSIS
    # -------------------------------
    problems = []
    fertilizer_tips = []

    if N < 40:
        problems.append("Nitrogen deficiency")
        fertilizer_tips.append("Apply Urea")

    if P < 40:
        problems.append("Phosphorus deficiency")
        fertilizer_tips.append("Apply DAP")

    if K < 40:
        problems.append("Potassium deficiency")
        fertilizer_tips.append("Apply MOP")

    if ph < 5.5:
        problems.append("Soil is acidic")
        fertilizer_tips.append("Add lime")

    elif ph > 7.5:
        problems.append("Soil is alkaline")
        fertilizer_tips.append("Add gypsum")

    if not problems:
        problems.append("Soil is balanced")
        fertilizer_tips.append("Maintain compost")

    # -------------------------------
    return render_template(
        "result.html",
        prediction=crop,
        confidence=confidence,

        predicted_profit=profit,
        predicted_revenue=avg_revenue,
        predicted_yield=yield_pred,

        monthly_revenue=monthly_revenue,

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
        total_cost=total_cost,

        N=N, P=P, K=K, ph=ph, rainfall=rainfall,
        problems=problems,
        fertilizer_tips=fertilizer_tips,

        accuracy=accuracy
    )

# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)