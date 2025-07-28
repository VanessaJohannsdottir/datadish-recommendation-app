import sqlite3
import pandas as pd

def get_cities_and_categories(db_path="yelp.db"):
    conn = sqlite3.connect(db_path)
    df_cities = pd.read_sql_query("SELECT DISTINCT city, state FROM business WHERE city IS NOT NULL AND state IS NOT NULL", conn)
    df_categories = pd.read_sql_query("SELECT DISTINCT category FROM business_categories", conn)
    conn.close()

    df_cities["city_state"] = df_cities["city"] + ", " + df_cities["state"]
    cities = sorted(df_cities["city_state"].tolist())
    categories = sorted(df_categories["category"].dropna().unique().tolist())
    return cities, categories

def search_restaurants(locations, categories, min_rating, db_path="yelp.db"):
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

    conditions = ["1=1"]
    params = []

    if locations:
        city_state_pairs = [tuple(loc.split(", ")) for loc in locations]
        city_state_clauses = []
        for city, state in city_state_pairs:
            city_state_clauses.append("(b.city = ? AND b.state = ?)")
            params.extend([city, state])
        conditions.append(f"({' OR '.join(city_state_clauses)})")

    if categories:
        conditions.append(f"bc.categories LIKE '%' || ? || '%'")
        params.append(categories[0])

    if min_rating is not None:
        conditions.append("b.stars >= ?")
        params.append(min_rating)

    final_query = f"{base_query} WHERE {' AND '.join(conditions)} GROUP BY b.business_id"

    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(final_query, conn, params=params)
    conn.close()
    return df
