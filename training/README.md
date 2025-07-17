# Review-Sampling-Strategie – Projektübersicht

In dieser Phase des Projekts war es das Ziel, eine repräsentative, vielfältige und informationsreiche Stichprobe von Bewertungen zu erstellen, die für die manuelle Labelvergabe und das Training eines maschinellen Lernmodells verwendet werden kann. Wir haben drei verschiedene Sampling-Strategien getestet, um eine Teilmenge von ca. 100.000 Bewertungen aus einem Pool von 3 Millionen zu extrahieren. Jede Bewertung ist mit einem bestimmten business_id verknüpft und enthält einen Bewertungstext sowie eine Sternebewertung (1 bis 5 Sterne).

Wir haben die drei Ansätze hinsichtlich Fairness, Vielfalt, Informationsgehalt und Umsetzbarkeit verglichen.

---

## Option 1: Zufällige 3 %-Stichprobe pro Business

Bei diesem Ansatz wurden 3 % der Bewertungen für jedes Business rein zufällig ausgewählt.

🟢 Vorteile:

- Sehr einfach umzusetzen  
- Garantiert eine faire Verteilung über alle Businesses hinweg  
- Schnell und speichereffizient

🔴 Nachteile:

- Bewertungslänge wird nicht berücksichtigt – kurze, wenig informative Texte werden genauso oft gezogen wie lange  
- Keine Garantie, dass unterschiedliche Sternebewertungen berücksichtigt werden

📎 Code-Referenz: [random_sampling_per_business.py](./random_sampling_per_business.py)

---

## Option 2: Länge-basierte gewichtete Stichprobe pro Business

Hier wurden weiterhin 3 % der Bewertungen pro Business gezogen, aber längere Bewertungen wurden mit einer höheren Wahrscheinlichkeit ausgewählt (gewichtetes Sampling basierend auf Textlänge).

🟢 Vorteile:

- Erhält die businessweite Vielfalt  
- Bevorzugt aussagekräftige, ausführlichere Bewertungen  
- Beibehaltung einer gewissen Zufälligkeit

🔴 Nachteile:

- Keine Gewährleistung für Ausgewogenheit hinsichtlich Sternebewertungen  
- Businesses mit vielen kurzen Bewertungen können unterrepräsentiert sein

📎 Code-Referenz: [random_sampling_per_business_by_review_len.py](./random_sampling_per_business_by_review_len.py)

---

## Option 3: Stratifiziert nach Sternen + Länge-gewichtetes Sampling pro Business

Dieser finale und gewählte Ansatz kombiniert mehrere Kriterien:

- Die Bewertungen werden zunächst nach Sternebewertung (1–5) aufgeteilt  
- Es wird versucht, aus jeder Sternkategorie gleich viele Bewertungen zu ziehen (soweit vorhanden)  
- Innerhalb jeder Sternkategorie erfolgt ein gewichtetes Sampling zugunsten längerer Bewertungen

🟢 Vorteile:

- Stellt sicher, dass alle Sentiment-Bereiche (über Sterne) abgedeckt werden  
- Bevorzugt inhaltlich reichere Bewertungen  
- Zufälligkeit bleibt erhalten  
- Optimal für ein Modell, das auf unterschiedliche Meinungen und Textlängen generalisieren soll

🔴 Nachteile:

- Etwas komplexere Logik erforderlich  
- Bei sehr einseitiger Sternverteilung pro Business kann die Gleichverteilung nicht immer exakt erreicht werden (wird aber robust gehandhabt)

📎 Code-Referenz: [random_sampling_per_business_by_len_stars.py](./random_sampling_per_business_by_len_stars.py)

---

## Finale Entscheidung & Begründung

Nach sorgfältiger Abwägung aller Vor- und Nachteile fiel die Entscheidung auf Option 3: das stratifizierte und längen-gewichtete Sampling unter Berücksichtigung der Sternebewertung. Dieser Ansatz liefert die qualitativ hochwertigste, ausgewogenste und informativste Stichprobe von ca. 104.000 Bewertungen.

Damit ist gewährleistet, dass das zu annotierende Trainingsdatenset ein breites Spektrum an Meinungen und Schreibstilen abdeckt – eine entscheidende Voraussetzung für ein robustes Modell, das auf die restlichen 3 Millionen Bewertungen angewendet werden soll.
