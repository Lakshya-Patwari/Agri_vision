from pathlib import Path
import pickle
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

BASE_DIR = Path(__file__).resolve().parent

CROP_DATASET = BASE_DIR / "data" / "final_crop_recommendation.csv"
COST_DATASET = BASE_DIR / "data" / "final_cost_of_cultivation_with_fruits.csv"
REVENUE_DATASET = BASE_DIR / "data" / "final_revenue.csv"

SEASON_MAPPING = {"kharif": 0, "rabi": 1, "summer": 2}

# -------------------------------
def load_data():
    crop = pd.read_csv(CROP_DATASET)
    cost = pd.read_csv(COST_DATASET)
    revenue = pd.read_csv(REVENUE_DATASET)

    crop = crop.rename(columns={"label": "Commodity"})
    crop["Commodity"] = crop["Commodity"].str.strip().str.lower()

    cost["Commodity"] = cost["Commodity"].str.strip().str.lower()
    revenue["Commodity"] = revenue["Commodity"].str.strip().str.lower()

    return crop, cost, revenue

# -------------------------------
def build_dataset():
    crop, cost, revenue = load_data()

    # COST
    cost = cost.groupby("Commodity", as_index=False).mean(numeric_only=True)
    cost["total_cost"] = cost["cul_cost_c2"]
    cost["yield_per_hectare"] = cost["derived_yield"]

    # PRICE
    price_col = [c for c in revenue.columns if "Modal Price" in c][0]
    revenue["price"] = pd.to_numeric(revenue[price_col], errors="coerce")

    revenue_grouped = revenue.groupby("Commodity")["price"].mean().reset_index()

    df = crop.merge(cost, on="Commodity", how="left")
    df = df.merge(revenue_grouped, on="Commodity", how="left")

    df["price_per_quintal"] = df["price"]
    df["revenue"] = df["yield_per_hectare"] * df["price_per_quintal"]

    df["ph"] = df["ph"].fillna(6.5)
    df.fillna(df.median(numeric_only=True), inplace=True)

    if "season" not in df.columns:
        df["season"] = "summer"

    df["season"] = df["season"].str.lower()
    df["season_encoded"] = df["season"].map(SEASON_MAPPING).fillna(2)

    df["month"] = (df.index % 12) + 1

    df = df.rename(columns={"Commodity": "crop_name"})

    return df, revenue

# -------------------------------
def compute_inflation(revenue):
    price_col = [c for c in revenue.columns if "Modal Price" in c][0]
    revenue["price"] = pd.to_numeric(revenue[price_col], errors="coerce")

    inflation_rates = {}

    grouped = revenue.groupby("Commodity")["price"].mean().reset_index()

    for crop in grouped["Commodity"].unique():
        inflation_rates[crop] = 0.05

    pickle.dump(inflation_rates, open("inflation.pkl", "wb"))

# -------------------------------
def train_models(df):

    features = ["N","P","K","temperature","humidity","ph","rainfall","season_encoded","month"]
    X = df[features]

    y_crop = df["crop_name"]
    y_yield = df["yield_per_hectare"]
    y_cost = df["total_cost"]

    # Crop model
    X_train, X_test, y_train, y_test = train_test_split(X, y_crop, test_size=0.2, random_state=42)
    crop_model = RandomForestClassifier(n_estimators=200)
    crop_model.fit(X_train, y_train)

    # Yield model
    yield_model = RandomForestRegressor(n_estimators=200)
    yield_model.fit(X, y_yield)

    # Cost model
    cost_model = RandomForestRegressor(n_estimators=200)
    cost_model.fit(X, y_cost)

    # -------------------------------
    # PRICE MODEL (XGBOOST)
    # -------------------------------
    df["crop_encoded"] = df["crop_name"].astype("category").cat.codes

    X_price = df[["month", "crop_encoded"]]
    y_price = df["price_per_quintal"]

    price_model = XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=6)
    price_model.fit(X_price, y_price)

    # Save mapping
    crop_mapping = dict(enumerate(df["crop_name"].astype("category").cat.categories))
    reverse_mapping = {v: k for k, v in crop_mapping.items()}

    pickle.dump(reverse_mapping, open("crop_encoding.pkl", "wb"))

    # Save models
    pickle.dump(crop_model, open("crop_model.pkl","wb"))
    pickle.dump(yield_model, open("yield_model.pkl","wb"))
    pickle.dump(cost_model, open("cost_model.pkl","wb"))
    pickle.dump(price_model, open("price_model.pkl","wb"))

    print("✅ Training complete")

# -------------------------------
if __name__ == "__main__":
    df, revenue = build_dataset()
    compute_inflation(revenue)
    train_models(df)