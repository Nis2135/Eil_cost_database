
import streamlit as st
from database import get_chemical_costs
from forecast import apply_inflation

import streamlit as st

st.image("eil_logo.png", width=100)

st.title("Chemical Cost Database")

forecast_year = st.number_input("Forecast Year", value=2030)

inflation_rate = st.slider(
    "Inflation Rate %",
    0.0,
    10.0,
    2.0
)

run_forecast = st.button("Run Forecast")


df = get_chemical_costs()

st.subheader("Chemical Cost Library")

st.dataframe(df)


if run_forecast:

    forecast_df = apply_inflation(df, inflation_rate, forecast_year)

    st.subheader("Forecast Results")

    st.dataframe(forecast_df)
