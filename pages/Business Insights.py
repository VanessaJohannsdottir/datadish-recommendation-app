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
from helpers.labels import filter_categories
import matplotlib.pyplot as plt

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

radius_options = [5, 10, 20, 50, 100]
selected_radius = st.sidebar.selectbox("🔎 Wähle den Suchradius (in km)", radius_options, index=2)

# === Oberer Bereich ===
st.title(f"{business['name']}")
st.write(f"{business['address']}, {business['city']}, {business['state']}")

st.markdown("---")

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
    avg_rating = get_average_rating_nearby(businesses, business["business_id"], radius_km=selected_radius)
    delta = round(business["stars"] - avg_rating, 2)
    stars = star_rating_string(avg_rating)

    if delta > 0:
        delta_color = "green"
        delta_symbol = "▲"
    elif delta < 0:
        delta_color = "red"
        delta_symbol = "▼"
    else:
        delta_color = "gray"
        delta_symbol = "–"

    # Layout mit zwei Spalten
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"**Sternebewertung der Konkurrenz ({selected_radius} km):**")

    with col2:
        st.markdown(
            f"""
            <div style='text-align:right'>
                <small style='color:gray'>Ø im Umkreis</small><br>
                <span style='font-size: 22px; font-weight: bold;'>{avg_rating:.2f}</span><br>
                <span style='font-size: 18px;'>{stars}</span><br>
                <span style='color:{delta_color}; font-size: 14px;'>{delta_symbol} {abs(delta):.2f}</span>
            </div>
            """,
            unsafe_allow_html=True
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


st.markdown(f"#### **Häufigste Kategorien im Umkreis**")

with st.spinner("Analysiere Kategorien..."):
    top_cats = get_top_categories_nearby(business["business_id"], radius_km=selected_radius)

if top_cats:
    df = pd.DataFrame(top_cats)
    df = df.rename(columns={"category": "Kategorie", "count": "Anzahl Betriebe"})

    # Gesamte Kategorien anzeigen
    st.markdown("**Alle Kategorien**")
    st.table(df.sort_values("Anzahl Betriebe", ascending=False))

    df_filtered = df[df["Kategorie"].isin(filter_categories)]

    if not df_filtered.empty:
        st.markdown("**Relevante Unterkategorien**")
        st.table(df_filtered.sort_values("Anzahl Betriebe", ascending=False))
    else:
        st.info("Keine Unterkategorien aus der Filterliste in der Umgebung gefunden.")
else:
    st.info("Keine Kategorien im Umkreis gefunden.")


st.markdown("---")


st.markdown("#### Erwähnte Aspekte in Bewertungen")
with st.spinner("Analysiere Labels..."):
    label_freq = get_label_frequencies(business["business_id"])

    if label_freq:
        df_labels = pd.DataFrame.from_dict(label_freq, orient="index", columns=["Anteil"])
        df_labels = df_labels.sort_values("Anteil", ascending=False)
        df_labels["Anteil (%)"] = (df_labels["Anteil"] * 100).round(1)

        # Matplotlib-Plot
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.bar(df_labels.index, df_labels["Anteil (%)"], color="#8b0a20")
        ax.set_title("Erwähnte Aspekte in Bewertungen", fontsize=14)
        ax.set_ylabel("Anteil in %", fontsize=12)
        ax.set_xlabel("Label", fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        plt.tight_layout()
        st.pyplot(fig)

    else:
        st.info("Keine Labels für dieses Business vorhanden.")


st.markdown("---")


st.markdown("#### Entwicklung der Bewertungen im Zeitverlauf")
with st.spinner("Lade Bewertungshistorie..."):
    rating_history = get_monthly_rating_history(business["business_id"])

if rating_history:
    df_history = pd.DataFrame(rating_history)
    df_history["month"] = pd.to_datetime(df_history["month"])
    df_history = df_history.sort_values("month")

    # Matplotlib-Plot
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(df_history["month"], df_history["average_rating"], color="#8b0a20", linewidth=2, marker="o", markersize=3)
    ax.set_title("Entwicklung der Bewertungen im Zeitverlauf", fontsize=14)
    ax.set_xlabel("Monat", fontsize=12)
    ax.set_ylabel("Ø Bewertung", fontsize=12)
    ax.set_ylim(0, 5.2)
    ax.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)

else:
    st.info("Keine Bewertungshistorie verfügbar.")
