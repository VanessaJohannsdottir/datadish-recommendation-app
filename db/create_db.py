import os
import pandas as pd
import sqlite3
from time import sleep
from tqdm import tqdm

# Datenbank im Root-Verzeichnis erstellen
db_path = "../yelp.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Pfad zum Datenordner
data_folder = "../data"

# Alle CSV-Dateien im Datenordner sammeln
csv_files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]

# Hilfsfunktion zur Erkennung des Tabellennamens aus Dateinamen
def get_table_name(filename):
    return filename.replace(".csv", "")

print("📥 Importiere CSV-Dateien in Datenbank...\n")

# Jede Datei einzeln mit eigenem Fortschrittsbalken verarbeiten
for file in csv_files:
    file_path = os.path.join(data_folder, file)
    table_name = get_table_name(file)

    print(f"Importiere Tabelle '{table_name}' ...")

    try:
        df = pd.read_csv(file_path)

        # Simulierter Fortschrittsbalken: Schrittweise durch die Zeilen
        row_count = len(df)
        step_size = max(row_count // 50, 1)  # max. 50 Schritte

        with tqdm(total=row_count, ncols=70, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} Zeilen") as bar:
            for i in range(0, row_count, step_size):
                sleep(0.01)  # nur zur visuellen Simulation
                bar.update(step_size)

        # Tabelle schreiben
        df.to_sql(table_name, conn, if_exists="replace", index=False)

        print(f"✅ Tabelle '{table_name}' erfolgreich erstellt.\n")

    except Exception as e:
        print(f"❌ Fehler bei '{table_name}': {e}\n")

# Foreign Keys aktivieren
cursor.execute("PRAGMA foreign_keys = ON;")
conn.commit()
conn.close()

print("✅ Datenbank 'yelp.db' wurde erfolgreich erstellt.")
