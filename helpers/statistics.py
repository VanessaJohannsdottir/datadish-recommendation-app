import pandas as pd

from helpers.data import get_df
from helpers.geo import haversine
from datetime import datetime, timedelta

def get_average_rating_nearby(business_id: str, radius_km: float = 20.0) -> float:
    query = """
        SELECT b1.business_id, b1.latitude, b1.longitude, b1.stars,
               b2.latitude AS center_lat, b2.longitude AS center_lon
        FROM business b1, business b2
        WHERE b2.business_id = ?
          AND b1.business_id != ?
          AND b1.is_open = 1
          AND b1.latitude IS NOT NULL AND b1.longitude IS NOT NULL
    """
    df = get_df(query, db_path="yelp.db", params=(business_id, business_id))
    if df.empty:
        return 0.0

    df["distance_km"] = df.apply(
        lambda row: haversine(
            row["latitude"], row["longitude"],
            row["center_lat"], row["center_lon"]
        ), axis=1
    )

    nearby = df[df["distance_km"] <= radius_km]
    return nearby["stars"].mean() if not nearby.empty else 0.0

def get_rating_trend(business_id: str) -> str:
    three_months_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    query = """
        SELECT stars, date FROM reviews
        WHERE business_id = ?
        AND date >= ?
        ORDER BY date ASC
    """
    df = get_df(query, db_path="yelp.db", params=(business_id, three_months_ago))
    if len(df) < 3:
        return "zu wenig Daten"

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df["rolling"] = df["stars"].rolling(window=3).mean()

    if df["rolling"].iloc[-1] > df["rolling"].iloc[0]:
        return "steigend"
    elif df["rolling"].iloc[-1] < df["rolling"].iloc[0]:
        return "fallend"
    else:
        return "gleichbleibend"

def get_top_competitors_nearby(business_id: str, radius_km: float = 20.0, top_n: int = 3) -> list:
    query = """
        SELECT b1.business_id, b1.name, b1.latitude, b1.longitude, b1.stars,
               b2.latitude AS center_lat, b2.longitude AS center_lon
        FROM business b1, business b2
        WHERE b2.business_id = ?
          AND b1.business_id != ?
          AND b1.is_open = 1
          AND b1.latitude IS NOT NULL AND b1.longitude IS NOT NULL
    """
    df = get_df(query, db_path="yelp.db", params=(business_id, business_id))
    if df.empty:
        return []

    df["distance_km"] = df.apply(
        lambda row: haversine(
            row["latitude"], row["longitude"],
            row["center_lat"], row["center_lon"]
        ), axis=1
    )

    nearby = df[df["distance_km"] <= radius_km]
    top = nearby.sort_values(by="stars", ascending=False).head(top_n)
    return top[["name", "stars"]].to_dict(orient="records")

def get_label_frequencies(business_id: str) -> dict:
    query = """
        SELECT rl.label
        FROM review_label rl
        JOIN reviews r ON rl.review_id = r.review_id
        WHERE r.business_id = ?
    """
    df = get_df(query, db_path="yelp.db", params=(business_id,))
    if df.empty:
        return {}

    total_reviews_query = "SELECT COUNT(*) AS count FROM reviews WHERE business_id = ?"
    total_reviews_df = get_df(total_reviews_query, db_path="yelp.db", params=(business_id,))
    total_reviews = total_reviews_df["count"].iloc[0]

    label_counts = df["label"].value_counts()
    frequencies = (label_counts / total_reviews).to_dict()
    return frequencies