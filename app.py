import streamlit as st
from helpers.layout import render_layout
from helpers.db import get_cities_and_categories, search_restaurants
from helpers.time import is_open_now, format_hours
from helpers.geo import get_city_coordinates, filter_by_radius

import sqlite3
import pandas as pd

# ========== Config ==========
st.set_page_config(page_title="DataDish - Restaurant Finder")
render_layout(page_name="index")

# ========== Hauptinhalt ==========
cities, categories = get_cities_and_categories()

prices = ["günstig ($)", "mittel ($$)", "gehoben ($$$)"]
ratings = ["min. ★☆☆☆☆", "min. ★★☆☆☆", "min. ★★★☆☆", "min. ★★★★☆", "min. ★★★★★"]

# ========== Filter ==========
col1, col2 = st.columns(2, gap="large")

with col1:
    sel_location = st.selectbox("Wo?", cities, placeholder="Stadt wählen")
with col2:
    sel_radius = st.slider("Suchradius (in km)", min_value=1, max_value=100, value=20)

sel_category = st.multiselect("Was?", categories, placeholder="Küche wählen")
sel_price = st.select_slider("Preiskategorie", options=prices)
sel_rating = st.selectbox("Bewertungen", ratings, index=2)
st.write("###")
submit_button = st.button("Restaurants finden", type="primary")

if submit_button:
    if not sel_location:
        st.warning("Bitte eine Stadt auswählen.")
    else:
        center_lat, center_lon = get_city_coordinates(sel_location)

        if center_lat is None:
            st.warning("Koordinaten der Stadt konnten nicht ermittelt werden.")
        else:
            result_df = search_restaurants(
                locations=None,  # Kein SQL-Filter auf city
                categories=sel_category,
                min_rating=ratings.index(sel_rating)
            )

            result_df = result_df.dropna(subset=["latitude", "longitude"])
            result_df = filter_by_radius(result_df, center_lat, center_lon, sel_radius)

            # ========== Ergebnisse anzeigen ==========
            with st.container():
                st.title("Gefundene Restaurants")
                if not result_df.empty:
                    st.write(f"**{len(result_df)} Restaurants im Umkreis von {sel_radius} km gefunden.**")

                    for _, row in result_df.iterrows():
                        is_open = is_open_now(row.get("hours"))
                        status_label = "🟢 Jetzt geöffnet" if is_open else "🔴 Geschlossen"

                        with st.expander(f"{row['name']} - {row['city']}, {row['state']} | {status_label}"):
                            st.write(f"{row.get('categories', 'Keine Angabe')}")
                            st.write(f"**{row['name']}**")
                            st.write(f"{row['stars']} Sterne")
                            st.write(f"**Entfernung:** {round(row['distance_km'], 2)} km")
                            st.write(f"{row.get('address', 'Nicht verfügbar')}")
                            st.write("**Öffnungszeiten:**")
                            st.text(format_hours(row.get("hours")))
                            if row.get("latitude") and row.get("longitude"):
                                st.map(pd.DataFrame({
                                    "latitude": [row["latitude"]],
                                    "longitude": [row["longitude"]],
                                }))
                else:
                    st.info("Keine passenden Restaurants im Umkreis gefunden.")

                st.markdown("---")
                if st.button("Zurück zur Suche", type="primary"):
                    st.switch_page("app.py")