# 📄 Übersicht der Datenbereinigung (Yelp-Datensatz)

Dieses Dokument beschreibt **alle Schritte**, die durchgeführt wurden, um den Yelp-Datensatz gründlich zu bereinigen und für weitere Analysen vorzubereiten.

---

## 🔄 1. JSON-Dateien in MySQL importieren

### Warum?
- Damit man schneller auf die Daten zugreifen kann.
- Durch **Indexe** werden SQL-Abfragen schneller.
- Das Löschen und Aktualisieren wird einfacher.
- Die ursprünglichen JSON-Dateien waren zu groß und schwer zu verarbeiten.

📌 Skripte:
- [📥 Reviews importieren](./import_reviews.py)
- [📥 Geschäftsdaten importieren](./import_business.py)

---
 

## 💾 2. Ergebnisse als CSV-Dateien speichern

- Die bereinigten Daten wurden im CSV-Format gespeichert.
- ✅ Vorteil: keine doppelten Attributnamen mehr → kleinere Dateien.

---

## 🗑️ 3. Entfernen von Reviews ohne Bezug zu Restaurants

- Nur Reviews von Geschäften mit der Kategorie `Restaurants` wurden behalten.
- Reviews **vorher**: 6.990.280 (~5,7 GB)
- Reviews **nachher**: 4.724.471 (~2,8 GB)
- ❌ Gelöschte Einträge: 2.265.809

🔧 [SQL-Abfragen](./queries.sql)

---

## 🧹 4. Entfernen von Reviews bei Geschäften mit weniger als 100 Reviews

- Reviews **vorher**: 4.724.471 (~2,8 GB)
- Reviews **nachher**: 3.434.505 (~2,1 GB)
- ❌ Gelöscht: 1.289.966 Reviews

---

## 🧹 5. Entfernen von Geschäften mit <100 Reviews UND ohne Restaurant-Kategorie

| Tabelle                | Vorher         | Nachher        | Nach dem Bereinigen  |
|------------------------|----------------|----------------|----------------------|
| `business`             | 150.346        | 11.798         | 11.785               |
| `business_category`    | 668.549        | 64.485         | 64.379               |
| `business_attributes`  | 1.206.820      | 254.336        | 251.105              |
| `business_hours`       | 801.015        | 76.482         | 76.407               |

---

## 🧼 6. Reinigung der Review-Texte in Batches

- Die Reviews wurden in Gruppen (Batches) bearbeitet und wieder in die Datenbank gespeichert.

🔧 [Reinigungsskript](./cleaning_process.py)

---

## 🧽 7. Reinigungsregeln

Beispieltext:
```
<br>Amazing</br> food &amp; drinks at €15 or $18!! 😋🔥 中文測試\nCheck out: https://www.yummy.de or mail us at best.food@mail.com\nFollow us @myinsta or visit www.bestfood.com\nTry it now!! 😍 \n\nTotally worth it.
```


| Regex / Methode | Beschreibung | Zwischenergebnis |
|------------------|--------------|------------------|
| – (Original) | Originaltext | `<br>Amazing</br>` food &amp; drinks at €15 or $18!! 😋🔥 中文測試\nCheck out: https://www.yummy.de or mail us at best.food@mail.com\nFollow us @myinsta or visit www.bestfood.com\nTry it now!! 😍 \n\nTotally worth it. |
| `text.lower()` | Kleinbuchstaben | `<br>amazing</br>` food &amp; drinks at €15 or $18!! 😋🔥 中文測試\ncheck out: https://www.yummy.de or mail us at best.food@mail.com\nfollow us @myinsta or visit www.bestfood.com\ntry it now!! 😍 \n\ntotally worth it. |
| `re.sub(r'<[^>]+>', ' ', ...)` | HTML-Tags entfernen | amazing food &amp; drinks at €15 or $18!! 😋🔥 中文測試\ncheck out: https://www.yummy.de or mail us at best.food@mail.com\nfollow us @myinsta or visit www.bestfood.com\ntry it now!! 😍 \n\ntotally worth it. |
| `re.sub(r'&[a-z]+;', ' ', ...)` | HTML-Entities entfernen | amazing food drinks at €15 or $18!! 😋🔥 中文測試\ncheck out: https://www.yummy.de or mail us at best.food@mail.com\nfollow us @myinsta or visit www.bestfood.com\ntry it now!! 😍 \n\ntotally worth it. |
| `re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', ' ', ...)` | E-Mail entfernen | amazing food drinks at €15 or $18!! 😋🔥 中文測試\ncheck out: https://www.yummy.de or mail us at \nfollow us @myinsta or visit www.bestfood.com\ntry it now!! 😍 \n\ntotally worth it. |
| `re.sub(r'(https?://\S+\|www\.\S+)', ' ', ...)` | URLs entfernen | amazing food drinks at €15 or $18!! 😋🔥 中文測試\ncheck out: or mail us at \nfollow us @myinsta or visit \ntry it now!! 😍 \n\ntotally worth it. |
| `re.sub(r'@\w+', ' ', ...)` | Social Handles entfernen | amazing food drinks at €15 or $18!! 😋🔥 中文測試\ncheck out: or mail us at \nfollow us or visit \ntry it now!! 😍 \n\ntotally worth it. |
| `unicodedata.normalize('NFKC', ...)` | Unicode normalisieren | (keine sichtbare Änderung, aber z. B. café → cafe) |
| `re.sub(r'[^\x00-\x7F€$]+', ' ', ...)` | Emojis & Nicht-ASCII entfernen (中文 wird entfernt) | amazing food drinks at €15 or $18!! \ncheck out: or mail us at \nfollow us or visit \ntry it now!! \n\ntotally worth it. |
| `re.sub(r'(?<=[a-z])\n\n', ' ', ...)` | Doppelte Zeilenumbrüche entfernen | amazing food drinks at €15 or $18!! \ncheck out: or mail us at \nfollow us or visit \ntry it now!! totally worth it. |
| `re.sub(r'(\d)\s*[,]*\s*%+', r'\1%', ...)` | Prozentzeichen direkt nach Zahl erhalten | (10 , % → 10%) |
| `re.sub(r'(?<!\d)%', '', ...)` | % ohne Zahl entfernen | (nicht angewendet – kein % ohne Zahl) |
| `re.sub(r'(?<=\d)%{2,}', '%', ...)` | doppelte %% → % | (nicht angewendet – kein doppeltes %) |
| `re.sub(r"[!\"#&()*+,\-./:;<=>?@\[\]\\^_``{\|}~]", " ", ...)` | Satzzeichen entfernen (aber € und $ bleiben) | amazing food drinks at €15 or $18 \ncheck out or mail us at \nfollow us or visit \ntry it now totally worth it |
| `re.sub(r"\s+'\b", ' ', ...)` | Apostrophe bereinigen (keine Beeinträchtigung von "can't", "it's" etc.) | (im Beispiel keine Apostrophformen betroffen) |
| `re.sub(r'(.)\1{2,}', r'\1\1', ...)` | Buchstabenwiederholungen kürzen (z. B. sooo → soo) | (nicht angewendet – keine dreifachen Buchstaben) |
| `re.sub(r'\b(?:[a-z]\s){2,}[a-z]\b', ...)` | Buchstaben mit Leerzeichen zusammenfügen (z. B. A M A Z I N G → amazing) | amazing food drinks at €15 or $18 check out or mail us at follow us or visit try it now totally worth it |
| `re.sub(r'\s+', ' ', ...).strip()` | Leerzeichen bereinigen | amazing food drinks at €15 or $18 check out or mail us at follow us or visit try it now totally worth it |
| `if not re.search(r'[a-zA-Z]', text): return ''` | Falls nur Zahlen/Zeichen übrig → ignorieren | (nicht ausgelöst, da Text noch Wörter enthält) |
| `apply jamspell` | Rechtschreibkorrektur via JamSpell | amazing food drinks at €15 or $18 check out or mail us at follow us or visit try it now totally worth it |

---

## ✅ 8. Rechtschreibkorrektur mit JamSpell

- JamSpell wurde verwendet, um Tippfehler automatisch zu korrigieren.
- Die Korrektur berücksichtigt den Kontext → bessere Ergebnisse für NLP.
- Wurde in einem Docker-Container ausgeführt.

---

## 📌 9. Neue Spalte `review_int_id` für schnellere SELECT-Abfragen

```sql
ALTER TABLE review
ADD COLUMN review_int_id BIGINT AUTO_INCREMENT UNIQUE;

CREATE INDEX idx_review_int_id_col ON review (review_int_id);
```

---

## 🗃️ 10. Wichtige Hinweise

- Die **Originaldaten** wurden **nicht überschrieben**.
- Die bereinigten Daten wurden in `review_processed` gespeichert.
- Übersprungene Reviews wurden gespeichert in: [discarded_reviews.zip](../data/discarded_reviews.zip)

---

## ⚠️ 11. Herausforderungen

- Datengröße: ~2,1 GB → zu groß für das kostenlose Streamlit (Limit: 1 GB)
- Lösungen:
    - Hosting mit AWS EC2 `r6g.medium` (8GB RAM, 1 CPU) (~36,79 USD/Monat)
    - Ein Dockerfile wurde erstellt, damit der Service einfach und ohne Oberfläche ausgeführt werden kann.


---

## 📤 12. Reviews exportieren

- Reviews wurden aus der Datenbank gelesen.
- Dann als CSV-Datei gespeichert.

🔧 [Exportskript](./read_review_from_sql_convert_to_csv.py)

---

## 🧾 13. Bereinigung von `business_attributes`

38 Attribute hatten fehlerhafte oder ungewöhnliche Werte. Diese wurden mit [diesem Skript](./fix_business_attributes.py) korrigiert.

### Beispiele:
- **Music**:
```
{'dj': False, u'background_music': False, 'no_music': False, u'jukebox': True, 'live': True, 'video': False, 'karaoke': False} -> ["live", "jukebox"]
```
- **BusinessParking**: 
```
{'garage': True, 'street': False, 'validated': False, 'lot': True, 'valet': False} -> ["garage", "lot"]
```
- **Ambience**:
```
{u'divey': False, u'hipster': False, u'casual': True, u'touristy': False, u'trendy': None, u'intimate': False, u'romantic': False, u'classy': False, u'upscale': False} -> ["casual"]
```
- **GoodForMeal**:
```
{'dessert': True, 'latenight': False, 'lunch': True, 'dinner': True, 'brunch': None, 'breakfast': False} -> ["dessert", "lunch", "dinner"]
```
- **BestNights**: 
```
{'monday': False, 'tuesday': True, 'friday': False, 'wednesday': False, 'thursday': True, 'sunday': True, 'saturday': False} -> ["tuesday", "thursday", "sunday"]
```
- **DietaryRestrictions**:
```
{'dairy-free': False, 'gluten-free': True, 'vegan': False, 'kosher': False, 'halal': False, 'soy-free': False, 'vegetarian': False} -> ["gluten-free"]
```

📌 Wenn der Wert `[]` ist, bedeutet das, dass nichts zutrifft.

---

## 🧾 14. Bereinigung des Business

13 businesses hatten kein Adresseintrag. Diese wurden gelöscht. Alle verknüpften Daten in anderen Tabellen wurden ebenfalls entfernt.

---

## 📤 15. Exportieren des Business 

- Tabellen `business`, `business_attributes`, `business_categories` und `business_hours` wurden aus der Datenbank gelesen.
- Dann als CSV-Dateien gespeichert.

🔧 [Exportskript](./read_all_from_sql_convert_to_csv.py)