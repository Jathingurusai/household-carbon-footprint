# Household Carbon Footprint Calculator with AI Suggestions

Built for the 1M1B AI for Sustainability Virtual Internship (IBM SkillsBuild & AICTE).

## What it does
- Takes household inputs: electricity, LPG, transport, flights, diet, waste.
- Calculates yearly CO2e per person using emission factors.
- A Random Forest model classifies the lifestyle as Low / Medium / High impact.
- A recommendation engine tests "what-if" changes and ranks them by CO2 saved.

## Run
```
pip install -r requirements.txt
streamlit run app.py
```

## Files
- `emissions.py`  emission factors and calculation
- `ai_model.py`   Random Forest classifier and recommendation engine
- `app.py`        Streamlit web interface

## SDGs
SDG 12 Responsible Consumption and Production, SDG 13 Climate Action.
