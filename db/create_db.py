# Import der CSV-Dateien in meine MySQL-Datenbank
import sqlite3
import pandas as pd
from sqlalchemy import create_engine

# SQLite verbinden
sqlite_conn = sqlite3.connect("../yelp.db")
sqlite_cursor = sqlite_conn.cursor()

# Tabellen auslesen
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in sqlite_cursor.fetchall()]

# MySQL-Verbindung vorbereiten
mysql_user = 'root'
mysql_password = 'DataScienceInstitute'
mysql_host = '127.0.0.1'  # oder IP
mysql_db = 'yelp'

# Engine für MySQL erstellen
mysql_engine = create_engine(f'mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}')

# Tabellen migrieren
for table in tables:
    df = pd.read_sql_query(f"SELECT * FROM {table}", sqlite_conn)
    df.to_sql(table, mysql_engine, if_exists='replace', index=False)
    print(f"Tabelle '{table}' erfolgreich migriert.")

sqlite_conn.close()
