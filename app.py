import pandas as pd
import plotly.express as px
import streamlit as st

from emissions import (calculate, TRANSPORT_KG_PER_KM, DIET_KG_PER_DAY,
                       INDIA_AVG_TONNES, WORLD_TARGET_TONNES)
from ai_model import build_model, predict_level, recommendations

st.set_page_config(page_title="Carbon Footprint AI", page_icon="🌍", layout="wide")


@st.cache_resource
def get_model():
    return build_model()


clf = get_model()

st.title("🌍 Household Carbon Footprint Calculator with AI Suggestions")
st.caption("AI for Sustainability Virtual Internship project | SDG 12 (Responsible Consumption) & SDG 13 (Climate Action)")

with st.sidebar:
    st.header("Your household")
    members = st.number_input("People in household", 1, 15, 4)

    st.subheader("Home energy")
    kwh = st.number_input("Electricity (kWh / month)", 0, 3000, 200, step=10)
    lpg = st.number_input("LPG cylinders / year", 0, 40, 8)

    st.subheader("Travel (per person)")
    mode = st.selectbox("Main transport", list(TRANSPORT_KG_PER_KM))
    km = st.number_input("Distance travelled (km / week)", 0, 3000, 100, step=10)
    flights = st.number_input("Flight hours / year", 0, 200, 0)

    st.subheader("Food & waste")
    diet = st.selectbox("Diet", list(DIET_KG_PER_DAY), index=1)
    waste = st.number_input("Household waste (kg / week)", 0.0, 100.0, 10.0, step=0.5)
    recycle = st.slider("Waste recycled / composted (%)", 0, 100, 20)

profile = dict(members=members, kwh_month=kwh, lpg_cylinders_year=lpg, mode=mode,
               km_week=km, flight_hours_year=flights, diet=diet,
               waste_kg_week=waste, recycle_pct=recycle)

result = calculate(profile)
total_t = result["total_kg"] / 1000
level, conf = predict_level(clf, profile)

c1, c2, c3 = st.columns(3)
c1.metric("Your footprint (per person)", f"{total_t:.2f} t CO₂e / year")
c2.metric("vs India average", f"{total_t - INDIA_AVG_TONNES:+.2f} t",
          delta_color="inverse")
c3.metric("AI impact level", level, f"{conf*100:.0f}% confidence", delta_color="off")

left, right = st.columns(2)
df = pd.DataFrame({"Category": result["categories"].keys(),
                   "kg CO2e": result["categories"].values()})
left.plotly_chart(px.pie(df, names="Category", values="kg CO2e", hole=0.45,
                         title="Where your emissions come from"),
                  use_container_width=True)

comp = pd.DataFrame({"Who": ["You", "India average", "1.5°C-aligned target"],
                     "t CO2e / year": [total_t, INDIA_AVG_TONNES, WORLD_TARGET_TONNES]})
right.plotly_chart(px.bar(comp, x="Who", y="t CO2e / year", color="Who",
                          title="How you compare"), use_container_width=True)

st.subheader("🤖 AI-powered suggestions to reduce your footprint")
recs = recommendations(profile)
if recs:
    rdf = pd.DataFrame(recs, columns=["Action", "CO2e saved (kg / year)"])
    st.dataframe(rdf, hide_index=True, use_container_width=True)
    best = recs[0]
    st.success(f"Biggest win: **{best[0]}** could save about **{best[1]} kg CO₂e per year**. "
               f"That is roughly {best[1]/21:.0f} mature trees absorbing CO₂ for a year.")
else:
    st.success("Great job! Your lifestyle is already very low-carbon.")

st.caption("Note: values are estimates based on average emission factors (India grid ≈ 0.71 kg CO₂/kWh). "
           "Use for awareness, not as an official carbon audit.")
