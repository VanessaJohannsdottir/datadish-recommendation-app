# DataDish - finde Dein passendes Restaurant im Handumdrehen
### Analyse von Restaurantdaten aus dem [YELP-Dataset](https://business.yelp.com/data/resources/open-dataset/)
👥 [Samaneh Asghari](https://github.com/samaneh-asghari)
👥 [Karlheinz Nerpel](https://github.com/User-1175)
👥 [Vanessa Bletz](https://github.com/VanessaJohannsdottir)

Dieses Dashboard bietet tiefgehende Einblicke in die Welt der Gastronomie, indem es **Bewertungen** und **Geschäftsdaten** analysiert. Entdecke **Trends**, verstehe **Kundenfeedback** und gewinne **wertvolle** Erkenntnisse!

---

## Infos zum Datensatz
- **6,990,280** Reviews
- **150,346** Businesses
- **11** Metropolitan areas
- **200,100** Pictures

## TECH-STACK

| Task            | Technologie                                                   |
|-----------------|---------------------------------------------------------------|
| Datenverwaltung | **MySQL, SQLite**                                             |
| Datenanalyse    | **Python, Pandas**                                            |
| Visualisierung  | **[Streamlit](https://docs.streamlit.io/)** - Version: 1.47.0 |

---

## 💬 GOOD TO KNOW

### ➕ Datenstandort

Die Daten befinden sich im Ordner [`data`](./data/) – dort liegt eine `.zip`-Datei. Diese sollte vor der Nutzung entpackt werden.

### ➕ Datenbereinigung

Die Daten wurden bereits bereinigt. Details zum Ablauf der Bereinigung sind in der Datei[`README zur Bereinigung`](./cleaning/README.md) zu finden.

### ➕ Training

Der Trainingsdatensatz für die Textklassifikation befindet sich im Ordner  [`data`](./data/).  
Er enthält:

- den finalen Datensatz [`training_dataset`](./training/training_dataset_70k_balanced_token.zip) mit ca. **70.000 Reviews**  
- ein ausführliches [`README zur Training`](./training/README.md), das alle Schritte zur Erstellung dokumentiert  
- alle verwendeten **Scripts**, z. B. für das Sampling  

Die Reviews wurden mit mehreren Sampling-Strategien ausgewählt, um eine gute **Balance zwischen Länge, Sternebewertung und Business-Vielfalt** zu erreichen.  
Ziel ist es, ein robustes Modell für die spätere automatische Multi-Label-Klassifikation zu trainieren.

--- 
## 🚀 APP STARTEN

### ➕ Datenbank erstellen

Die ZIPs aus `/data` enthalten alle wichtigen CSV-Dateien, die wir für die Erstellung der DB brauchen. 
Führe beim Initialisierung des Projekts das Skript `/db/create_db.py` aus, um initial eine Datenbank zu erhalten. Diese wird im root-Ordner unter `yelp.db` zu finden sein, wenn das Skript ausgeführt wurde.

### ➕ Streamlit starten

Ist die Datenbank erstellt, können wir die Streamlit-App starten. Dazu in der Console im Projektordner den Befehl `streamlit run app.py` ausführen.

---

### 🐳 Alternativ: Start mit Docker

Die einfachste Möglichkeit, die Anwendung vollständig zu starten, ist per Docker Compose.  
Dabei werden automatisch alle Abhängigkeiten installiert und die Anwendung lauffähig gemacht – **kein manuelles Setup nötig**.

#### ✅ So startest du das Projekt:

- 👉 **Wenn du macOS oder Linux verwendest**, führe einfach folgendes Skript im Terminal aus:
  ```bash
  ./start.sh
  ```

- 👉 **Wenn du Windows verwendest**, kannst du einfach einen Doppelklick auf `start.bat` machen oder es in der Eingabeaufforderung ausführen:
  ```cmd
  start.bat
  ```

#### 📝 Hinweise:

- Beim **ersten Start** lädt Docker alle Abhängigkeiten und verarbeitet die **großen Datendateien** (z. B. ZIPs).
- ⏳ **Das kann einige Minuten dauern**, bitte etwas Geduld mitbringen.
- Sobald alles fertig ist, wird automatisch dein Browser geöffnet mit der Anwendung unter [`http://localhost:8501`](http://localhost:8501).

> 📌 Hinweis: Stelle sicher, dass Docker und Docker Compose auf deinem System installiert sind.

---

## 🆕 Mögliche Verbesserungen 🆕

| IMPROVEMENT                        | IST                                                           | SOLL                                                    |
|------------------------------------|---------------------------------------------------------------|---------------------------------------------------------|
| **Styling-Methode ändern**         | Styling über `st.markdown()`                                  | Komponenten erstellen und vor Ort stylen                |
| **Ladezustände anpassen**          | keine Ladezustände integriert                                 | -                                                       |
| **Zeitzonen berücksichtigen**      | bei Öffnungszeiten wird die Zeitzone des Rechners hergenommen | Zeitzone des Standorts verwenden                        |
| **Öffnungszeiten-Format anpassen** | Öffnungszeiten unformatiert                                   | Öffnungszeiten formatieren                              |
| **Sortierung der Ergebnisseite**   | Ergebnisse werden nach Reihenfolge aus DB ausgegeben          | Sortierung nach Sternen, Namen oder Entfernung zu Stadt |