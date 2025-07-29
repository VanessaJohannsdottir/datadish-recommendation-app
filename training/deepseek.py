import pandas as pd
import requests
import os
from time import sleep
import argparse

# Configuration
DEEPSEEK_API_KEY = "XXX"
INPUT_CSV = "filtered_index_training_dataset_70k_balanced_token.csv"
API_URL = "https://api.deepseek.com/v1/chat/completions"
DELAY_BETWEEN_REQUESTS = 0.2


# FINAL STRICT PROMPT VERSION
PROMPT_TEMPLATE = """You are a strict, rule-based multi-label classifier for restaurant reviews. Apply these rules with ZERO flexibility.

**DO NOT CREATE NEW LABEL AND ONLY USE THE ALLOWED LABELS**

ALLOWED LABELS (ONLY USE THESE):
friendly_staff, slow_service, rude_staff, professional_service, unprofessional_service,
delicious_food, poor_taste, overcooked, fresh_ingredients,
low_quality_ingredients, unhygienic, spoiled,
cozy_atmosphere, noisy_environment, cleanliness, dirty,
good_value, overpriced, positive, negative

RULES:
1. Assign ALL labels that explicitly match their definitions
2. MUST assign ONE sentiment label (positive/negative) last
3. NEVER infer - require explicit evidence for each label
4. If no labels match except sentiment, assign only sentiment

STRICT LABEL DEFINITIONS:
### Service:
- friendly_staff: Assign only if the staff is explicitly described as kind, welcoming, or warm (e.g., “smiled warmly,” “friendly welcome,” “remembered my name”).
- slow_service: Assign only if the review explicitly mentions long waits, slow delivery, or delay (e.g., “waited 30 minutes,” “kitchen backed up,” “took forever to get food”).
- rude_staff: Assign only if the staff is described as rude, impolite, dismissive, or unprofessional (e.g., “rolled eyes,” “ignored us,” “was mean,” “did not care”).
- professional_service: Assign only if the staff is called skilled, attentive, or knowledgeable (e.g., “explained the wine list,” “recommended dishes with confidence”).
- unprofessional_service: Assign only if staff demonstrates clear incompetence (e.g., "didn't know the menu", "spilled drinks repeatedly")

### Food & Drinks:
- delicious_food: Assign only if food is explicitly described as “delicious,” “amazing,” “incredible,” “tasty,” or similar enthusiastic terms.
- poor_taste: Assign if:
  * Food is bland/flavorless ("no flavor", "needed salt") OR
  * Has unpleasant flavors ("metallic taste", "tasted like soap")
- overcooked: Assign only if the food is described as dry, burnt, rubbery, mushy, or otherwise badly cooked. Do NOT assign if the complaint is only about taste or ingredients.
- fresh_ingredients: Assign only if ingredients are described as fresh, crisp, or high-quality (e.g., “everything tasted fresh,” “ingredients were high quality”).
- low_quality_ingredients: Assign only if ingredients are described as low-quality, processed, or artificial (e.g., “cheap cheese,” “tasted like it came from a can”).
- unhygienic: Assign only if hygiene issues are mentioned (e.g., “hair in food,” “dirty utensils,” “cockroach,” “food was undercooked and unsafe”).
- spoiled: Assign only if food is described as sour, rotten, expired, or spoiled (e.g., “milk was sour,” “smelled rotten”).

### Ambience & Hygiene:
- cozy_atmosphere: Assign only if the place is described as “cozy,” “romantic,” “intimate,” or mentions warm lighting, candles, quiet ambiance.
- noisy_environment: Assign only if the review clearly mentions noise (e.g., “too loud,” “couldn’t hear,” “music was blasting”).
- cleanliness: Assign only if the review praises cleanliness (e.g., “tables were spotless,” “floors were immaculate,” “very clean inside”).
- dirty: Assign only if visible dirt is mentioned (e.g., “sticky tables,” “filthy bathroom,” “trash on the floor”).

### Price & Value:
- good_value: Assign only if price is described as fair or a good deal (e.g., “worth the price,” “great deal,” “huge portion for $10”).
- overpriced: Assign only if price is described as too high or not worth it (e.g., “too expensive for the portion,” “not worth it”).

SENTIMENT RULES:
POSITIVE ONLY IF:
- Explicit return intent ("I'll return") OR
- Explicit recommendation ("I recommend") OR
- Clear positive conclusion despite minor complaints

NEGATIVE MUST ASSIGN WHEN:
- Any hygiene/safety issue (unhygienic/spoiled) OR
- Explicit refusal to return OR
- Multiple complaints outweigh positives OR
- "Never coming back" or similar

TIE-BREAKER ORDER:
1. Explicit return intent → Positive
2. Explicit refusal → Negative
3. Equal positives/negatives → Positive
4. When in doubt → Negative

ABSOLUTELY PROHIBITED:
- Creating new labels
- Interpreting sarcasm/irony
- Considering reviewer history
- Using non-present tense evidence
- Counting words without explicit labels

EDGE CASE EXAMPLES:
1. "Great food but rude staff" → delicious_food, rude_staff, negative
2. "Burnt steak but I'll return" → overcooked, positive
3. "Everything terrible" → negative

FORMAT:
Return ONLY comma-separated labels ending with sentiment (e.g., 'fresh_ingredients,positive' or 'slow_service,negative'). If you realize a mistake, IMMEDIATELY output the corrected labels WITHOUT any extra text, explanations, or apologies.

Review to classify: {review_text}"""

def classify_review(text):
    """Send review to DeepSeek API with strict error handling"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a STRICT rule-based classifier. Follow ALL rules exactly."},
            {"role": "user", "content": PROMPT_TEMPLATE.format(review_text=text)}
        ],
        "temperature": 0,
        "max_tokens": 50  # Limit response length
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip().replace(" ", "")
    except Exception as e:
        print(f"API Error: {str(e)[:100]}...")
        return None

def validate_labels(labels_str):
    """Ensure labels strictly comply with rules"""
    if not labels_str:
        return None
        
    allowed_labels = {
        'friendly_staff', 'slow_service', 'rude_staff', 'professional_service', 'unprofessional_service',
        'delicious_food', 'poor_taste', 'overcooked', 'fresh_ingredients',
        'low_quality_ingredients', 'unhygienic', 'spoiled',
        'cozy_atmosphere', 'noisy_environment', 'cleanliness', 'dirty',
        'good_value', 'overpriced', 'positive', 'negative'
    }
    
    labels = [l.strip() for l in labels_str.split(',') if l.strip()]
    
    # Must have exactly one sentiment label at end
    if not labels or labels[-1] not in {'positive', 'negative'}:
        return None
        
    # Check all labels are allowed
    labels = [l for l in labels if l in allowed_labels]
    
    if not labels or labels[-1] not in {'positive', 'negative'}:
        return None
        
    return labels

def process_reviews(start:int, end:int):
    print(f"Processing reviews between {start} and {end} ...")
    
    OUTPUT_CSV = "deepseek_70k_balanced_token_labeled_%d_%d.csv" % (start, end)
    counter = 0
    """Verarbeitet Reviews, klassifiziert sie und speichert Labels einzeln"""
    # Falls Ausgabedatei nicht existiert, erstelle sie
    if not os.path.exists(OUTPUT_CSV):
        pd.DataFrame(columns=['review_id', 'label']).to_csv(OUTPUT_CSV, index=False)

    processed_ids = []
    # Lade bereits verarbeitete review_ids
    try:
        existing_df = pd.read_csv(OUTPUT_CSV)
        processed_ids = existing_df['review_id'].astype(str).unique().tolist()
    except:
        existing_df = pd.DataFrame(columns=['review_id', 'label'])

    counter+=len(processed_ids)
    # Lade Input-Daten
    try:
        input_df = pd.read_csv(INPUT_CSV)
        input_df = input_df[(input_df["id"]>=start) & (input_df["id"]<=end)]
        
        
        print(f"will skip: {len(processed_ids)}")
        print(f"total before: {len(input_df)}")
        input_df = input_df[input_df["review_id"].isin(processed_ids)==False]
        # input_df = input_df[:2]  # Nur zum Testen begrenzt, später entfernen
        print(f"total after: {len(input_df)}")
        
        for _, row in input_df.iterrows():
            counter+=1
            
            review_id = row['review_id']
            if review_id in processed_ids:
                print(f"skipped: {counter}")
                continue

            print(f"Processing ID: {review_id}")
            labels_str = classify_review(row['text'])
            sleep(DELAY_BETWEEN_REQUESTS)

            if not labels_str:
                print("Keine Antwort erhalten.")
                continue

            labels = validate_labels(labels_str)
            if not labels:
                print(f"Ungültige Labels: {labels_str}")
                continue

            print(counter, ":", review_id, labels)

            # Neue Zeilen als DataFrame vorbereiten
            new_rows = pd.DataFrame([{'review_id': review_id, 'label': label} for label in labels])

            # Direkt an CSV anhängen
            new_rows.to_csv(OUTPUT_CSV, mode='a', index=False, header=False)

    except Exception as e:
        print(f"Fehler beim Verarbeiten: {e}")
    finally:
        print(f"Verarbeitung abgeschlossen. Ergebnisse gespeichert in {OUTPUT_CSV}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set start and end rows")
    parser.add_argument("--start", type=int, help="start id to process")
    parser.add_argument("--end", type=int, help="end id to process")
    args = parser.parse_args()

    process_reviews(args.start, args.end)