import pandas as pd
import numpy as np



# CONFIGURATION
INPUT_CSV = "../data/reviews.csv"                    # Input-Pfad zur CSV mit allen Reviews
OUTPUT_CSV = "../data/training_dataset_104k.csv"     # Output-Pfad für das Trainingsset
REVIEW_TEXT_COL = "text"                             # Spaltenname für Review-Texte
STAR_COL = "stars"                                   # Spaltenname für Sterne-Bewertungen (1-5)
BUSINESS_ID_COL = "business_id"                      # Spaltenname für Business-IDs
SAMPLE_PERCENT = 0.03                                # 3% der Reviews pro Business werden gesampelt

#Daten einlesen
print("Loading data...")
df = pd.read_csv(INPUT_CSV)

#SAMPLING FUNCTION
def sample_group(reviews_per_business):
    # Gesamt-Samplegröße berechnen (mindestens 1 Review)
    n_total = max(1, int(len(reviews_per_business) * SAMPLE_PERCENT))  # sample at least 1 total

    # Verfügbare Sterne-Bewertungen ermitteln (ohne NaN)
    stars = reviews_per_business[STAR_COL].unique()
    stars = [s for s in stars if pd.notnull(s)]
    
    # Target-Anzahl pro Sterne-Wert (mindestens 1)
    n_per_star = max(1, n_total // len(stars))  

    sampled_rows = []

    # Pro Sterne-Bewertung samplen
    for star_value in stars:
        # Gruppe für diesen Stern-Wert
        star_group = reviews_per_business[reviews_per_business[STAR_COL] == star_value]

        if len(star_group) == 0:
            continue

        # Samplegröße für diesen Stern (nicht mehr als vorhanden)
        n_star = min(n_per_star, len(star_group))

        # Sampling-Gewichte basierend auf Textlänge
        lengths = star_group[REVIEW_TEXT_COL].str.len()
        weights = lengths / lengths.sum()

        # Zufällige Auswahl mit Gewichtung
        sampled_indices = np.random.choice(
            star_group.index, size=n_star, replace=False, p=weights
        )

        sampled_rows.append(reviews_per_business.loc[sampled_indices])

    result = pd.concat(sampled_rows)

    # Falls Sample zu klein: Ergänzen aus Restgruppe
    if len(result) < n_total:
        remaining_n = n_total - len(result)
        remaining_group = reviews_per_business.drop(result.index)

        if not remaining_group.empty:
            lengths = remaining_group[REVIEW_TEXT_COL].str.len()
            weights = lengths / lengths.sum()

            extra_indices = np.random.choice(
                remaining_group.index, size=min(remaining_n, len(remaining_group)), replace=False, p=weights
            )
            result = pd.concat([result, reviews_per_business.loc[extra_indices]])

    return result

# EXECUTION
print("Sampling 3% of reviews per business...")
df_sampled = df.groupby(BUSINESS_ID_COL, group_keys=False).apply(sample_group)

#SAVE RESULTS
print(f"Saving sampled dataset to: {OUTPUT_CSV}")
df_sampled.to_csv(OUTPUT_CSV, index=False)

# SUMMARY
print(f"✅ Done. Sampled {len(df_sampled):,} reviews from {df[BUSINESS_ID_COL].nunique():,} businesses.")
