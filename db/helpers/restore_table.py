import sqlite3
import pandas as pd

# Konfiguriere Pfade und Tabellennamen
db_file = "../../yelp.db"
csv_file = "../../data/business_categories.csv"
table_name = "business_categories"

# CSV laden
df = pd.read_csv(csv_file)

# Verbindung zur Datenbank
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Tabelle leeren
cursor.execute(f"DELETE FROM {table_name}")
print(f"Inhalt von '{table_name}' gelöscht.")

# CSV-Daten einfügen
df.to_sql(table_name, conn, if_exists='append', index=False)
print(f"Daten aus '{csv_file}' in '{table_name}' eingefügt.")

# Verbindung schließen
conn.commit()
conn.close()