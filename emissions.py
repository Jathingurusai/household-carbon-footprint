"""Emission factors and footprint calculation (approximate, India-focused).

Sources for typical values: CEA India grid factor, IPCC/DEFRA-style averages.
These are estimates for education, not an official audit.
"""

# kg CO2e per unit
GRID_KG_PER_KWH = 0.71          # India average grid emission factor
LPG_KG_PER_CYLINDER = 42.5      # 14.2 kg cylinder x ~3 kg CO2 per kg
TRANSPORT_KG_PER_KM = {
    "Car (petrol/diesel)": 0.17,
    "Two-wheeler": 0.04,
    "Bus": 0.09,
    "Train / Metro": 0.04,
    "Auto-rickshaw": 0.08,
    "Walk / Cycle": 0.0,
}
FLIGHT_KG_PER_HOUR = 90.0       # approx per passenger flight hour
DIET_KG_PER_DAY = {
    "Vegan": 1.5, "Vegetarian": 1.7, "Eggetarian": 2.0, "Non-vegetarian": 2.8,
}
WASTE_KG_CO2_PER_KG = 0.5       # landfilled waste
RECYCLE_REDUCTION = 0.6         # share of emissions avoided on recycled waste

INDIA_AVG_TONNES = 2.0          # per-person yearly average (approx)
WORLD_TARGET_TONNES = 2.3       # per-person level compatible with 1.5C goals


def calculate(p: dict) -> dict:
    """p: profile dict. Returns yearly kg CO2e per category and total."""
    members = max(p["members"], 1)
    electricity = p["kwh_month"] * 12 * GRID_KG_PER_KWH
    lpg = p["lpg_cylinders_year"] * LPG_KG_PER_CYLINDER
    energy = (electricity + lpg) / members            # per person

    travel = (p["km_week"] * 52 * TRANSPORT_KG_PER_KM[p["mode"]]
              + p["flight_hours_year"] * FLIGHT_KG_PER_HOUR)

    food = DIET_KG_PER_DAY[p["diet"]] * 365

    waste_kg = p["waste_kg_week"] * 52 / members
    waste = waste_kg * WASTE_KG_CO2_PER_KG * (1 - RECYCLE_REDUCTION * p["recycle_pct"] / 100)

    cats = {"Home energy": energy, "Travel": travel, "Food": food, "Waste": waste}
    cats = {k: round(v, 1) for k, v in cats.items()}
    return {"categories": cats, "total_kg": round(sum(cats.values()), 1)}
