import streamlit as st
import pandas as pd

st.title("EIL Chemical Cost Database")

year = st.selectbox(
    "Select Cost Year",
    [2024, 2025, 2026, 2027]
)

data = {
    "Chemical": ["Methanol", "Glycol", "Corrosion Inhibitor"],
    "Cost ($/kg)": [1.2, 2.1, 3.5]
}

df = pd.DataFrame(data)

st.write("Chemical Cost Table")
st.dataframe(df)

st.write("Selected year:", year)
