def apply_inflation(df, inflation_rate, forecast_year, base_year=2025):

    years = forecast_year - base_year

    df["Forecast_Cost"] = df["Cost"] * (1 + inflation_rate/100) ** years

    return df
