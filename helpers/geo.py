import sqlite3
import pandas as pd
from math import radians, cos, sin, sqrt, atan2

def get_city_coordinates(city, db_path="yelp.db"):
    conn = sqlite3.connect(db_path)
    query = """
        SELECT latitude, longitude 
        FROM business 
        WHERE city = ? AND latitude IS NOT NULL AND longitude IS NOT NULL 
        LIMIT 1
    """
    result = pd.read_sql_query(query, conn, params=[city])
    conn.close()

    if not result.empty:
        return result.iloc[0]["latitude"], result.iloc[0]["longitude"]
    return None, None


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    diff_lat = radians(lat2 - lat1)
    diff_lon = radians(lon2 - lon1)
    a = sin(diff_lat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(diff_lon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def filter_by_radius(df, center_lat, center_lon, radius_km):
    def calc_distance(row):
        return haversine(center_lat, center_lon, row["latitude"], row["longitude"])

    df["distance_km"] = df.apply(calc_distance, axis=1)
    return df[df["distance_km"] <= radius_km]
