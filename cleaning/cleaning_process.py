import argparse
import time
import mysql.connector
from mysql.connector import Error
import re
import unicodedata
import requests

session = requests.Session()
def clean_with_jamspell_api(text: str, jamspell_port) -> str:
    try:
        response = session.post(
            f"http://localhost:{jamspell_port}/clean",
            json={"text": text},
            timeout=120
        )
        if response.status_code == 200:
            return response.json().get("corrected", text)
        else:
            print("Error from JamSpell API:", response.status_code)
            return text
    except requests.exceptions.RequestException as e:
        print("Connection to JamSpell API failed:", e)
        return text

connection  = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='DataScienceInstitute',
    database='yelp_db'
)

def clean_review(text, jamspell_port):
    if not isinstance(text, str):
        return ''

    # Alles klein
    text = text.lower()

    # HTML-Tags & Entities entfernen
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&[a-z]+;', ' ', text)

    # E-Mails, URLs, Socials
    text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', ' ', text)
    text = re.sub(r'(https?://\S+|www\.\S+)', ' ', text)
    text = re.sub(r'@\w+', ' ', text)

    # Unicode normalisieren
    text = unicodedata.normalize('NFKC', text)

    # Entferne Emojis & nicht-ASCII außer € $
    text = re.sub(r'[^\x00-\x7F€$]+', ' ', text)

    # Zeilenumbrüche entfernen
    text = re.sub(r'(?<=[a-z])\n\n', ' ', text)

    # ✅ Prozent vor Satzzeichen behandeln
    # Erlaube % nur direkt nach Zahl
    text = re.sub(r'(\d)\s*[,]*\s*%+', r'\1%', text)  # 10 , % → 10%
    text = re.sub(r'(?<!\d)%', '', text)              # % ohne Zahl davor → weg
    text = re.sub(r'(?<=\d)%{2,}', '%', text)         # doppelte %% → %

    # ✅ Satzzeichen entfernen (aber Apostrophs erlauben!)
    text = re.sub(r"[!\"#&()*+,\-./:;<=>?@\[\]\\^_`{|}~]", " ", text)

    # ✅ Ungültige Apostrophs entfernen (außer in Wörtern wie can't, it's)
    text = re.sub(r"\s+'\b", ' ', text)
    text = re.sub(r"\b'\s+", ' ', text)
    text = re.sub(r"'{2,}", '', text)
    text = re.sub(r"\s'{1}\s", ' ', text)

    # Wiederholte Buchstaben reduzieren (sooo → soo)
    text = re.sub(r'(.)\1{2,}', r'\1\1', text)

    # A M A Z I N G → amazing
    text = re.sub(r'\b(?:[a-z]\s){2,}[a-z]\b', lambda m: m.group(0).replace(' ', ''), text)

    # Whitespace säubern
    text = re.sub(r'\s+', ' ', text).strip()

    # Wenn nur Zahlen übrig bleiben, ignorieren
    if not re.search(r'[a-zA-Z]', text):
        return ''

    # JamSpell-Korrektur über API
    text = clean_with_jamspell_api(text, jamspell_port)

    return text


def process(row, jamspell_port):

    old_text = row['text']
    row['text'] = clean_review(row['text'],jamspell_port)  # Beispiel: Alles großschreiben
    
    if len(row['text'])==0 :
        return (None,old_text)

    return (row, old_text)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jam', type=int, required=True, help='Jamspell port')
    parser.add_argument('--start', type=int, required=True, help='Start offset')
    parser.add_argument('--end', type=int, required=True, help='End offset')
    args = parser.parse_args()

    jamspell_port = args.jam
    range_start = args.start
    range_end = args.end
    batch_size = 10000
    count = 0

    connection = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='DataScienceInstitute',
        database='yelp_db'
    )

    try:
        cursor = connection.cursor(dictionary=True)
        current_id = range_start
        batch_num = 0
        while current_id < range_end:
            next_id = min(current_id + batch_size, range_end)
            print(f"Fetching reviews with review_int_id between {current_id} and {next_id}")
            cursor.execute(f"""
                SELECT business_id, review_id, user_id, stars, date, text, useful, funny, cool, review_int_id
                FROM review
                WHERE review_int_id >= %s AND review_int_id < %s
            """, (current_id, next_id))
            
            rows = cursor.fetchall()
            print(f"fetched rows.")
            
            if not rows:
                break

            batch_num += 1
            start_time = time.time()

            print('-'*20)
            print(f'{len(rows)} has been fetched.')
            data_to_insert = []

            internal = 0
            for row in rows:
                internal_start_time = time.time()
                processed, original_text = process(row,jamspell_port)
                if processed is None:
                    with open(f"discarded_reviews.csv", "a", encoding="utf-8") as f:
                        f.write(f"{row['review_id']},{original_text.strip()}\n")
                    continue

                data_to_insert.append((
                    processed['business_id'],
                    processed['review_id'],
                    processed['user_id'],
                    processed['stars'],
                    processed['date'],
                    processed['text'],
                    processed['useful'],
                    processed['funny'],
                    processed['cool'],
                    processed['review_int_id']
                ))
                internal_duration = time.time() - internal_start_time
                print(f'row: {internal} has been processed in {internal_duration:.2f} Sek.')
                internal+=1
                
            if data_to_insert:
                insert_query = """
                    INSERT INTO review_processed (
                        business_id, review_id, user_id,
                        stars, date, text, useful, funny, cool, review_int_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.executemany(insert_query, data_to_insert)
                connection.commit()
            duration = time.time() - start_time
            count += 1
            print(f"[{count}] Offset {current_id}: {len(rows)} Zeilen verarbeitet in {duration:.2f} Sek.")
            print('-'*20)
            current_id = next_id

    except Error as e:
        print("Fehler:", e)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Verbindung geschlossen.")
            
main()
