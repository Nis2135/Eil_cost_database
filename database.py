import pyodbc
import pandas as pd


def connect_db():

    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=localhost\\MSSQLSERVER01;"
        "DATABASE=Cost_Estimation;"
        "Trusted_Connection=yes;"
    )

    return conn


def get_chemical_costs():

    conn = connect_db()

    query = """
    SELECT Chemical_Name, Cost
    FROM dbo.Chemical_Cost_Library
    """

    df = pd.read_sql(query, conn)

    return df
