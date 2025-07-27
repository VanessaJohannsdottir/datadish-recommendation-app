import sqlite3
import pandas as pd

def get_cities_and_categories(db_path="yelp.db"):
    """Lädt alle verfügbaren Städte und Kategorien aus der Datenbank."""
    conn = sqlite3.connect(db_path)
    city_list = pd.read_sql_query("SELECT DISTINCT city FROM business", conn)
    category_list = pd.read_sql_query("SELECT DISTINCT category FROM business_categories", conn)
    conn.close()

    cities = sorted(city_list["city"].dropna().unique().tolist())
    categories = sorted(category_list["category"].dropna().unique().tolist())
    return cities, categories


def search_restaurants(locations, categories, min_rating, db_path="yelp.db"):
    """Führt die gefilterte Restaurant-Suche durch und liefert ein DataFrame zurück."""

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
        placeholders = ",".join(["?"] * len(locations))
        conditions.append(f"b.city IN ({placeholders})")
        params.extend(locations)

    if categories:
        placeholders = ",".join(["?"] * len(categories))
        # Wichtig: bc ist eine Subquery – also binden wir wieder auf bc.category
        conditions.append(f"bc.categories LIKE '%' || ? || '%'")
        # Nutze LIKE statt IN, weil `categories` ein zusammengesetzter Text ist
        params.append(categories[0])  # optional erweitern für mehrere Kategorien

    if min_rating is not None:
        conditions.append("b.stars >= ?")
        params.append(min_rating)

    final_query = f"{base_query} WHERE {' AND '.join(conditions)} GROUP BY b.business_id"

    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(final_query, conn, params=params)
    conn.close()
    return df
