import pandas as pd
import numpy as np



# KONFIGURATION - Pfade und Parameter
INPUT_CSV = "../data/reviews.csv"                               # Eingabedatei mit allen Reviews
OUTPUT_CSV = "random_sampling_per_business_by_review_len.csv"   # Ausgabedatei für die Stichprobe  
REVIEW_TEXT_COL = "text"                                        # Spaltenname für den Review-Text
STAR_COL = "stars"                                              # Spaltenname für die Sterne-Bewertung (1-5)
BUSINESS_ID_COL = "business_id"                                 # Spaltenname für die Business-ID
SAMPLE_PERCENT = 0.03                                           # Prozentsatz der zu samplenden Reviews pro Business (3%)


# Lade die gesamten Review-Daten in einen DataFrame
print("Loading data...")
df = pd.read_csv(INPUT_CSV)

# SAMPLING-FUNKTION (LÄNGEN-GEWICHTET)
def sample_group(group):
    
    # Berechne Sample-Größe (mindestens 1 Review, auch bei kleinen Businesses)
    sample_size = max(1, int(len(group) * SAMPLE_PERCENT))  
    
    # Berechne Gewichtungen basierend auf Textlängen
    lengths = group[REVIEW_TEXT_COL].str.len()  # Länge jedes Reviews
    weights = lengths / lengths.sum()           

    # Ziehe Stichprobe mit längen-gewichteter Wahrscheinlichkeit
    sampled_indices = np.random.choice(
        group.index,        # Auswahl aus allen Indizes der Gruppe
        size=sample_size ,  
        replace=False,      
        p=weights           # Verwendung der berechneten Gewichte
        )         
    return group.loc[sampled_indices]            # Rückgabe der gesampleten Zeilen


# DATENPROZESSIERUNG
print("Sampling 3% of reviews per business...")
# Wende die Sampling-Funktion auf jede Business-Gruppe an
df_sampled = df.groupby(BUSINESS_ID_COL, group_keys=False).apply(sample_group)

# ERGEBNISSPEICHERUNG
print(f"Saving sampled dataset to: {OUTPUT_CSV}")
df_sampled.to_csv(OUTPUT_CSV, index=False)

# Berechne und zeige Statistik der gezogenen Stichprobe
print(f"✅ Done. Sampled {len(df_sampled):,} reviews from {df[BUSINESS_ID_COL].nunique():,} businesses.")
