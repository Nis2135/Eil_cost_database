def apply_inflation(df, inflation_rate, forecast_year):

    years = forecast_year - df["Base_Year"]

    df["Forecast_Cost"] = df["Base_Cost"] * (1 + inflation_rate/100) ** years

    return df
