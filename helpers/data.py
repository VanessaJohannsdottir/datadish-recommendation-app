import streamlit as st
import sqlite3
import pandas as pd

def get_connection(db_path="yelp.db"):
    return sqlite3.connect(db_path)

def get_df(query, db_path, params=None):
    conn = get_connection(db_path)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

@st.cache_data
def get_all_businesses():
    """
    Liefert alle (dauerhaft) geöffneten Businesses inklusive Kategorie-Infos.
    """
    query = """
        SELECT 
            b.business_id, b.name, b.address, b.city, b.state, b.postal_code,
            b.latitude, b.longitude, b.stars, bc.categories
        FROM business b
        LEFT JOIN (
            SELECT business_id, GROUP_CONCAT(category, ' · ') AS categories
            FROM business_categories
            GROUP BY business_id
        ) bc ON b.business_id = bc.business_id
        WHERE b.is_open = 1
    """
    return get_df(query, db_path="yelp.db").to_dict(orient="records")

@st.cache_data
def get_cities():
    """
    Gibt alle Städte zurück.
    """
    cities_query = "SELECT DISTINCT city, state FROM business WHERE city IS NOT NULL AND state IS NOT NULL"
    df_cities = get_df(cities_query, db_path="yelp.db")

    df_cities["city_state"] = df_cities["city"] + ", " + df_cities["state"]
    cities = sorted(df_cities["city_state"].tolist())
    return cities

@st.cache_data
def get_restaurants(locations, categories, min_rating):
    """
    Gibt alle GEFILTERTEN Restaurants zurück.
    """
    base_query = """
        SELECT 
            b.*, 
            bc.categories,
            bh.hours
        FROM business b
        LEFT JOIN (
            SELECT 
                business_id, 
                GROUP_CONCAT(category, ' · ') AS categories
            FROM (
                SELECT DISTINCT business_id, category 
                FROM business_categories
            )
            GROUP BY business_id
        ) bc ON b.business_id = bc.business_id
        LEFT JOIN (
            SELECT 
                business_id, 
                GROUP_CONCAT(day_of_week || ': ' || hours, ' · ') AS hours
            FROM (
                SELECT DISTINCT business_id, day_of_week, hours
                FROM business_hours
            )
            GROUP BY business_id
        ) bh ON b.business_id = bh.business_id
    """
    conditions = ["1=1 AND b.is_open = 1"]
    params = []

    if locations:
        city_state_pairs = [tuple(loc.split(", ")) for loc in locations]
        city_state_clauses = []
        for city, state in city_state_pairs:
            city_state_clauses.append("(b.city = ? AND b.state = ?)")
            params.extend([city, state])
        conditions.append(f"({' OR '.join(city_state_clauses)})")

    if categories:
        category_clauses = []
        for category in categories:
            category_clauses.append("bc.categories LIKE '%' || ? || '%'")
            params.append(category)
        conditions.append(f"({' OR '.join(category_clauses)})")

    if min_rating is not None:
        conditions.append("b.stars >= ?")
        params.append(min_rating)

    final_query = f"{base_query} WHERE {' AND '.join(conditions)} GROUP BY b.business_id"

    restaurants = get_df(final_query, db_path="yelp.db", params=params)
    return restaurants

@st.cache_data
def get_labels_for_business(business_id):
    """
    Gibt alle Label pro Business zurück.
    """
    query="SELECT rl.review_id, rl.label FROM review_label rl JOIN reviews r ON rl.review_id = r.review_id WHERE r.business_id = ? ORDER BY r.date DESC"
    labels = get_df(query, db_path="yelp.db", params=(business_id,))
    return labels


@st.cache_data
def get_labels_for_business(business_id, allowed_labels=None):
    """
    Holt alle Labels und zugehörige Review-IDs für ein Business aus der Datenbank.
    Optional können die Labels auf eine erlaubte Liste eingeschränkt werden.

    Returns: pd.DataFrame: DataFrame mit Spalten 'label' und 'review_id'.
    """
    query = """
        SELECT rl.label, rl.review_id
        FROM review_label rl
        JOIN reviews r ON rl.review_id = r.review_id
        WHERE r.business_id = ?
    """
    df = get_df(query, db_path="yelp.db", params=(business_id,))

    if allowed_labels is not None:
        df = df[df["label"].isin(allowed_labels)]
    return df


@st.cache_data
def get_top_labels(business_id, allowed_labels: list, threshold=0.2):
    """
    Gibt alle Labels zurück, die bei mindestens threshold-Anteil der Reviews eines Businesses vorkommen (bezogen auf positive_labels)
    """
    df = get_labels_for_business(business_id, allowed_labels)

    if df.empty:
        return []
    total_reviews = df["review_id"].nunique()

    if total_reviews == 0:
        return []
    label_counts = df.groupby("label")["review_id"].nunique()
    label_freq = (label_counts / total_reviews).to_dict()
    top_labels = [label for label, freq in label_freq.items() if freq >= threshold]
    return top_labels

@st.cache_data
def get_labels_for_businesses(business_ids):
    """
    Nimmt eine Liste an business_ids entgegen und gibt die entsprechende Liste mit business_id, label & review_id zurück.
    """
    placeholders = ','.join('?' for _ in business_ids)
    query = f"SELECT r.business_id, rl.label, rl.review_id FROM review_label rl JOIN reviews r ON rl.review_id = r.review_id WHERE r.business_id IN ({placeholders})"
    return get_df(query, db_path="yelp.db", params=business_ids)

