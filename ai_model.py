"""AI part: a Random Forest that classifies a lifestyle as Low / Medium / High
impact, plus a recommendation engine that ranks actions by estimated CO2 saved."""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from emissions import (calculate, TRANSPORT_KG_PER_KM, DIET_KG_PER_DAY,
                       GRID_KG_PER_KWH, FLIGHT_KG_PER_HOUR)

FEATURES = ["kwh_month", "lpg_cylinders_year", "km_week", "transport_idx",
            "flight_hours_year", "diet_idx", "waste_kg_week", "recycle_pct", "members"]
MODES = list(TRANSPORT_KG_PER_KM)
DIETS = list(DIET_KG_PER_DAY)


def _row(p):
    return [p["kwh_month"], p["lpg_cylinders_year"], p["km_week"], MODES.index(p["mode"]),
            p["flight_hours_year"], DIETS.index(p["diet"]), p["waste_kg_week"],
            p["recycle_pct"], p["members"]]


def _label(total_kg):
    t = total_kg / 1000
    return "Low" if t < 2.0 else "Medium" if t < 4.0 else "High"


def build_model(n=4000, seed=42):
    """Train on synthetic Indian-household profiles labelled via emission factors."""
    rng = np.random.default_rng(seed)
    X, y = [], []
    for _ in range(n):
        p = {
            "members": int(rng.integers(1, 7)),
            "kwh_month": float(rng.uniform(30, 600)),
            "lpg_cylinders_year": int(rng.integers(2, 16)),
            "km_week": float(rng.uniform(0, 400)),
            "mode": MODES[int(rng.integers(0, len(MODES)))],
            "flight_hours_year": float(rng.choice([0, 0, 0, 2, 5, 10, 20])),
            "diet": DIETS[int(rng.integers(0, len(DIETS)))],
            "waste_kg_week": float(rng.uniform(2, 25)),
            "recycle_pct": float(rng.uniform(0, 100)),
        }
        X.append(_row(p))
        y.append(_label(calculate(p)["total_kg"]))
    X = pd.DataFrame(X, columns=FEATURES)
    clf = RandomForestClassifier(n_estimators=150, random_state=seed).fit(X, y)
    return clf


def predict_level(clf, p):
    X = pd.DataFrame([_row(p)], columns=FEATURES)
    proba = clf.predict_proba(X)[0]
    classes = list(clf.classes_)
    best = int(np.argmax(proba))
    return classes[best], float(proba[best])


def recommendations(p):
    """Return list of (action, kg_saved_per_year) sorted by impact."""
    base = calculate(p)["total_kg"]
    ideas = []

    def test(label, **changes):
        q = {**p, **changes}
        saved = base - calculate(q)["total_kg"]
        if saved > 5:
            ideas.append((label, round(saved)))

    test("Cut electricity use by 20% (LED lights, 5-star appliances, fewer AC hours)",
         kwh_month=p["kwh_month"] * 0.8)
    test("Move to a 3 kW rooftop solar / buy green power for half your usage",
         kwh_month=p["kwh_month"] * 0.5)
    if p["mode"] in ("Car (petrol/diesel)", "Two-wheeler", "Auto-rickshaw"):
        test("Shift your commute to bus / metro / train", mode="Train / Metro")
        test("Carpool or combine trips to cut travel distance by 30%",
             km_week=p["km_week"] * 0.7)
    if p["flight_hours_year"] > 0:
        test("Replace half of your flights with train travel",
             flight_hours_year=p["flight_hours_year"] / 2)
    if p["diet"] == "Non-vegetarian":
        test("Go vegetarian 3 days a week (use 'Eggetarian' average as proxy)",
             diet="Eggetarian")
    if p["diet"] in ("Non-vegetarian", "Eggetarian"):
        test("Switch to a vegetarian diet", diet="Vegetarian")
    if p["recycle_pct"] < 80:
        test("Segregate and recycle at least 80% of household waste", recycle_pct=80)
    test("Reduce household waste by 25% (compost kitchen waste, avoid single-use plastic)",
         waste_kg_week=p["waste_kg_week"] * 0.75)
    test("Switch cooking to induction / biogas for part of your LPG use",
         lpg_cylinders_year=max(p["lpg_cylinders_year"] - 3, 0))

    return sorted(ideas, key=lambda x: -x[1])[:6]
