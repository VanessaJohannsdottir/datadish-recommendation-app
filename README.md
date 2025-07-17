# 📊 Projektübersicht

### Willkommen zu unserem Projekt!   
Dieses Dashboard bietet tiefgehende Einblicke in die Welt der Gastronomie, indem es **Bewertungen** und **Geschäftsdaten** analysiert. Entdecke **Trends**, verstehe **Kundenfeedback** und gewinne **wertvolle** Erkenntnisse!

# WegWeiser - finde Dein passendes Restaurant im Handumdrehen
### Analyse von Restaurantdaten aus dem [YELP-Dataset](https://business.yelp.com/data/resources/open-dataset/)
[Samaneh Asghari](https://github.com/samaneh-asghari), [Karlheinz Nerpel](https://github.com/User-1175) & [Vanessa Bletz](https://github.com/VanessaJohannsdottir)


## 📁 Datenstandort

Die Daten befinden sich im Ordner [`data`](./data/) – dort liegt eine `.zip`-Datei.  
Diese sollte vor der Nutzung entpackt werden.

## 🧹 Datenbereinigung

Die Daten wurden bereits bereinigt.  
Details zum Ablauf der Bereinigung sind in der Datei  
[`README zur Bereinigung`](./cleaning/README.md) zu finden.


## 🧠 Training

Der Trainingsdatensatz für die Textklassifikation befindet sich im Ordner  [`data`](./data/).  
Er enthält:

- den finalen Datensatz [`training_dataset`](./data/training_dataset_104k.zip) mit ca. **104.000 Reviews**  
- ein ausführliches [`README zur Training`](./training/README.md), das alle Schritte zur Erstellung dokumentiert  
- alle verwendeten **Scripts**, z. B. für das Sampling  

Die Reviews wurden mit mehreren Sampling-Strategien ausgewählt, um eine gute **Balance zwischen Länge, Sternebewertung und Business-Vielfalt** zu erreichen.  
Ziel ist es, ein robustes Modell für die spätere automatische Multi-Label-Klassifikation zu trainieren.

---

## ALLGEMEIN
- **6,990,280** Reviews
- **150,346** Businesses
- **11** Metropolitan areas
- **200,100** Pictures

### Nutzereingaben

- Ort/Bundesstaat
- Kategorie (Sushi, Pizza, BBQ, ...)
- Bewertungen
- Preiskategorie (optional)
  
**Parameter-Dropdown:**
- kinderfreundlich
- hundefreundlich
- Parkplatz vorhanden
- Sauberkeit
- Drunkness-Score (optional)
- Romance-Score (optional)
- Lieferung möglich (optional)
- Reaktionszeit (optional)


### App-Ausgabe:

- Bilder
- Name
- Adresse / Map
- Kategorie
- Bewertungen
- Preisspanne
- Öffnungszeiten
- Parameter-Batches


## TECH-STACK

| Task            | Technologie                                 |
|-----------------|---------------------------------------------|
| Datenverwaltung | **MySQL, SQLite**                           |
| Datenanalyse    | **Python, Pandas, Seaborn**                 |
| Visualisierung  | **[Streamlit](https://docs.streamlit.io/)** |
