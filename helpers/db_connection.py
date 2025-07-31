import sqlite3
import pandas as pd

def get_connection(db_path="yelp.db"):
    return sqlite3.connect(db_path)

def get_df(query, db_path, params=None):
    conn = get_connection(db_path)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df