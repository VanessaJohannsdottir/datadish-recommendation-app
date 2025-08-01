import pandas as pd
import sqlite3

from collections import Counter

from helpers.data import get_df
from helpers.geo import haversine
from datetime import datetime, timedelta
from collections import defaultdict


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

def get_monthly_rating_history(business_id, db_path="yelp.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
        SELECT date, stars
        FROM reviews
        WHERE business_id = ?
    """
    cursor.execute(query, (business_id,))
    reviews = cursor.fetchall()
    conn.close()

    monthly_ratings = defaultdict(list)
    for date_str, stars in reviews:
        try:
            month = datetime.strptime(date_str[:10], "%Y-%m-%d").strftime("%Y-%m")
            monthly_ratings[month].append(stars)
        except Exception as e:
            print(f"Fehler beim Parsen von '{date_str}': {e}")

    history = []
    for month in sorted(monthly_ratings.keys()):
        ratings = monthly_ratings[month]
        avg = sum(ratings) / len(ratings)
        history.append({
            "month": month,
            "average_rating": round(avg, 2)
        })

    return history

def get_top_categories_nearby(business_id, radius_km=20, db_path="yelp.db", top_n=5):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT latitude, longitude
        FROM business
        WHERE business_id = ?
    """, (business_id,))
    result = cursor.fetchone()
    if not result:
        return []
    lat1, lon1 = result

    cursor.execute("""
        SELECT business_id, latitude, longitude
        FROM business
        WHERE business_id != ?
    """, (business_id,))
    all_businesses = cursor.fetchall()

    nearby_ids = []
    for b_id, lat2, lon2 in all_businesses:
        if lat2 and lon2:
            dist = haversine(lat1, lon1, lat2, lon2)
            if dist <= radius_km:
                nearby_ids.append(b_id)

    if not nearby_ids:
        return []

    placeholders = ",".join(["?"] * len(nearby_ids))

    query = f"""
        SELECT category
        FROM business_categories
        WHERE business_id IN ({placeholders})
    """
    cursor.execute(query, nearby_ids)
    results = cursor.fetchall()
    conn.close()

    counter = Counter([row[0] for row in results if row[0]])
    return [
        {"category": cat, "count": count}
        for cat, count in counter.most_common(top_n)
    ]