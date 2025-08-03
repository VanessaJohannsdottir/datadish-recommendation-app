import pandas as pd
import numpy as np
from transformers import RobertaTokenizer
from tqdm import tqdm

#  CONFIG
INPUT_CSV = "../data/reviews.csv"
OUTPUT_CSV = "training_dataset_70k_balanced_token.csv"
REVIEW_TEXT_COL = "text"
STAR_COL = "stars"
ID_COL = "review_id"
SAMPLE_SIZE = 70000
TOKEN_MIN = 200
TOKEN_MAX = 256
TARGET_PER_STAR = SAMPLE_SIZE // 5

#  Tokenizer laden
tokenizer = RobertaTokenizer.from_pretrained("roberta-base")

# Daten einlesen
print("Lade Reviews...")
df = pd.read_csv(INPUT_CSV)

df = df[[ID_COL, REVIEW_TEXT_COL, STAR_COL]].dropna()

#  Token-Längen berechnen
# Zuerst berechnen wir für jede Bewertung, wie viele Tokens (also Wörter bzw. Teile davon) sie enthält. Diese Anzahl speichern wir in einer neuen Spalte im DataFrame.

# Im nächsten Schritt filtern wir alle Bewertungen heraus, deren Token-Anzahl zwischen 200 und 256 liegt.

# Mit diesem Filter behalten wir nur die Bewertungen, die für uns eine passende Länge haben – also weder zu kurz noch zu lang.
print(" Berechne Tokenlängen...")
token_lengths = []
for text in tqdm(df[REVIEW_TEXT_COL], desc="Tokenisierung"):
    tokens = tokenizer.tokenize(str(text))
    token_lengths.append(len(tokens))

df["token_count"] = token_lengths

#  Filter: Nur Texte mit 200–256 Tokens
df_filtered = df[(df["token_count"] >= TOKEN_MIN) & (df["token_count"] <= TOKEN_MAX)]

#  Gleichmäßig pro Sternewert samplen
sampled_rows = []

print(" Samplen pro Stern-Level:")

# Wir wählen pro Sterne-Bewertung gleich viele Reviews, damit die Labels im Training gut verteilt sind.
for star in sorted(df_filtered[STAR_COL].unique()):
    group = df_filtered[df_filtered[STAR_COL] == star]
    print(f"{star} Sterne: {len(group)} Kandidaten")

    if len(group) < TARGET_PER_STAR:
        raise ValueError(f"Nicht genug Reviews mit {star} Sternen und {TOKEN_MIN}-{TOKEN_MAX} Tokens (benötigt: {TARGET_PER_STAR}, gefunden: {len(group)})")

    sampled = group.sample(n=TARGET_PER_STAR, random_state=42)
    sampled_rows.append(sampled)

#  Zusammenführen und zufällig mischen
df_sampled = pd.concat(sampled_rows).sample(frac=1, random_state=42)

#  Nur review_id & text exportieren
df_sampled = df_sampled[[ID_COL, REVIEW_TEXT_COL]]

#  Speichern
print(f"\n Speichere {len(df_sampled)} Reviews nach: {OUTPUT_CSV}")
df_sampled.to_csv(OUTPUT_CSV, index=False)

print("Fertig.")
