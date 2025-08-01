import streamlit as st
import pandas as pd
from helpers.layout import render_layout
from helpers.data import get_all_businesses
from helpers.ui import star_rating_string
from helpers.statistics import (
    get_average_rating_nearby,
    get_rating_trend,
    get_top_competitors_nearby,
    get_label_frequencies,
    get_monthly_rating_history,
    get_top_categories_nearby
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
with st.spinner("Lade Konkurrenzdaten..."):
    competitors = get_top_competitors_nearby(business["business_id"], radius_km=20)

if competitors:
    for c in competitors:
        stars_comp = star_rating_string(c["stars"])
        st.markdown(f"- **{c['name']}**: {stars_comp} ({c['stars']} Sterne)")
else:
    st.info("Keine Konkurrenten im Umkreis gefunden.")


st.markdown("---")


st.markdown(f"**Häufigste Kategorien im Umkreis** (20 km)")
with st.spinner("Analysiere Kategorien..."):
    top_cats = get_top_categories_nearby(business["business_id"], radius_km=20)

if top_cats:
    cols = st.columns(len(top_cats))
    for col, cat in zip(cols, top_cats):
        col.metric(label=cat["category"], value=f"{cat['count']} Betriebe")
else:
    st.info("Keine Kategorien im Umkreis gefunden.")


st.markdown("---")


st.markdown("**Erwähnte Aspekte in Bewertungen**")
with st.spinner():
    label_freq = get_label_frequencies(business["business_id"])
    if label_freq:
        df_labels = pd.DataFrame.from_dict(label_freq, orient="index", columns=["Anteil"])
        df_labels = df_labels.sort_values("Anteil", ascending=False)
        df_labels["Anteil (%)"] = (df_labels["Anteil"] * 100).round(1)
        st.bar_chart(df_labels["Anteil (%)"])
    else:
        st.info("Keine Labels für dieses Business vorhanden.")


st.markdown("---")


st.markdown("**Entwicklung der Bewertungen im Zeitverlauf**")
with st.spinner("Lade Bewertungshistorie..."):
    rating_history = get_monthly_rating_history(business["business_id"])

if rating_history:
    df_history = pd.DataFrame(rating_history)
    df_history["month"] = pd.to_datetime(df_history["month"])
    df_history = df_history.sort_values("month")

    st.line_chart(df_history.set_index("month")["average_rating"])
else:
    st.info("Keine Bewertungshistorie verfügbar.")
