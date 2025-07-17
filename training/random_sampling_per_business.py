import pandas as pd
import numpy as np


# Pfade und Konfigurationen
INPUT_CSV = "../data/reviews.csv"                        # Input-Pfad zur CSV mit allen Reviews
OUTPUT_CSV = "random_sampling_per_business.csv"          # Output-Pfad für die Stichprobe
REVIEW_TEXT_COL = "text"                                 # Spaltenname für Review-Texte
STAR_COL = "stars"                                       # Spaltenname für Sterne-Bewertungen
BUSINESS_ID_COL = "business_id"                          # Spaltenname für Business-IDs
SAMPLE_PERCENT = 0.03                                    # 3% Stichprobe pro Business

#Daten einlesen
print("Loading data...")
df = pd.read_csv(INPUT_CSV)


#Funktion für stratifizierte Stichprobe (pro Business)
def sample_group(group):
    sample_size= max(1, int(len(group) * SAMPLE_PERCENT))  #Mindestens 1 Review
    return group.sample(n=sample_size, random_state=42)

#Stichprobe ziehen
print("Sampling 3% of reviews per business...")
df_sampled = df.groupby(BUSINESS_ID_COL, group_keys=False).apply(sample_group)



#Ergebnisse speichern
print(f"Saving sampled dataset to: {OUTPUT_CSV}")
df_sampled.to_csv(OUTPUT_CSV, index=False)  

print(f"✅ Done. Sampled {len(df_sampled):,} reviews from {df[BUSINESS_ID_COL].nunique():,} businesses.")
