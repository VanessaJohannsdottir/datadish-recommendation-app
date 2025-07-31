import streamlit as st
import pandas as pd
from helpers.layout import render_layout
from helpers.data import get_all_businesses
from helpers.ui import star_rating_string
from helpers.statistics import (
    get_average_rating_nearby,
    get_rating_trend,
    get_top_competitors_nearby,
    get_label_frequencies
)

# === Layout & Konfiguration ===
st.set_page_config(
    page_title="Business Insights",
    initial_sidebar_state="expanded"
)
render_layout(page_name="pages")

# === Sidebar: Navigation + Auswahl ===
businesses = get_all_businesses()
selected_business_name = st.sidebar.selectbox("Wähle ein Business", [b["name"] for b in businesses])
business = next(b for b in businesses if b["name"] == selected_business_name)

# === Oberer Bereich ===
st.title(f"{business['name']}")

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("**Eigene Sternebewertung:**")
    st.markdown("3-Monats-Tendenz:")
with col2:
    stars = star_rating_string(business["stars"])
    st.markdown(f"{stars} ({business['stars']} Sterne)")

    with st.spinner("Analysiere Trend..."):
        trend = get_rating_trend(business["business_id"])
        st.markdown(f"📈 {trend}")

st.markdown("---")

# Vergleich mit Umgebung
with st.spinner("Vergleich läuft..."):
    avg_rating = get_average_rating_nearby(business["business_id"], radius_km=20)

delta = round(business["stars"] - avg_rating, 2)
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("**Sternebewertung der Konkurrenz (20 km):**")
with col2:
    st.metric(
        label="Ø im Umkreis",
        value=f"{avg_rating:.2f} ⭐",
        delta=f"{delta:+.2f}"
    )

st.markdown("**Top-Konkurrenten in der Nähe:**")
competitors = get_top_competitors_nearby(business["business_id"], radius_km=20)
for c in competitors:
    st.markdown(f"- {c['name']} ({c['stars']} Sterne)")

st.markdown("---")

# === Alle Labels (inkl. Häufigkeit) ===
st.subheader("Erwähnte Aspekte in Bewertungen")
with st.spinner():
    label_freq = get_label_frequencies(business["business_id"])
    if label_freq:
        df_labels = pd.DataFrame.from_dict(label_freq, orient="index", columns=["Anteil"])
        df_labels = df_labels.sort_values("Anteil", ascending=False)
        df_labels["Anteil (%)"] = (df_labels["Anteil"] * 100).round(1)
        st.bar_chart(df_labels["Anteil (%)"])
    else:
        st.info("Keine Labels für dieses Business vorhanden.")

