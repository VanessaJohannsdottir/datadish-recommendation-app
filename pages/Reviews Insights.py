import streamlit as st
from helpers.layout import render_layout

import reports.data_access as da
import reports.load as ld
import reports.review_reports as review_reports

# ========== Page Config & Layout ==========
render_layout(page_name="Review Insights")

#Lade Daten einmalig beim Start
tbl = ld.init_server()

#Zugriffsschicht auf die Daten über DataAccess
db = da.DataAccess(tbl)

st.title("Reviews Insights")

# Abschnitt 1: Top_Bewertungen & Schwachstellen nach Themen (Labels)
review_reports.top_n_section(db)
st.divider()

#  Abschnitt 2: Verbindung zwischen Labels und Sternebewertungen
review_reports.star(db)
st.divider()

# Abschnitt 3: Wie Gäste Preis_Leistung empfinden (Kombi aus Geschmack/Stimmung & Preis)
review_reports.Preis_Leistung(db)
st.divider()

#  Abschnitt 4: Häufigste Begriffe je Sternbewertung (WordCloud)
review_reports.word_cloud_section(db)
st.divider()

#  Abschnitt 5: Entwicklung der Labels im Zeitverlauf (inkl. Corona-Effekt)
review_reports.reviews_star_per_year_section(db)
st.divider()

# Abschnitt 6: Interaktive Karte mit Businesses nach Bewertung & Stadt
review_reports.business_on_map_section(db)

