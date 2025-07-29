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

if "show_results" not in st.session_state:
    st.session_state.show_results = False

# ========== Main ==========
cities, categories = get_cities_and_categories()

prices = ["günstig ($)", "mittel ($$)", "gehoben ($$$)"]
rating_options = {
    "min. ★☆☆☆☆": 1.0,
    "min. ★★☆☆☆": 2.0,
    "min. ★★★☆☆": 3.0,
    "min. ★★★★☆": 4.0,
    "min. ★★★★★": 5.0
}
ratings = list(rating_options.keys())

# ========== Filter ==========
if not st.session_state.get("show_results"):
    col1, col2 = st.columns(2, gap="large")

    with col1:
        sel_location = st.selectbox(
            "Wo?",
            cities,
            index=cities.index(st.session_state.get("sel_location")) if st.session_state.get("sel_location") else None,
            placeholder="Stadt wählen"
        )
    with col2:
        sel_radius = st.slider(
            "Suchradius (in km)",
            min_value=1,
            max_value=100,
            value=st.session_state.get("sel_radius", 15)
        )

    sel_category = st.multiselect(
        "Was?",
        categories,
        default=st.session_state.get("sel_category", []),
        placeholder="Küche wählen"
    )
    sel_price = st.select_slider(
        "Preiskategorie",
        options=prices
    )
    sel_rating = st.selectbox(
        "Bewertungen",
        rating_options,
        index=ratings.index(st.session_state.get("sel_rating")) if st.session_state.get("sel_rating") else 2
    )
    submit_button = st.button(
        "Restaurants finden",
        type="primary"
    )

    if submit_button:
        if not sel_location:
            st.warning("Bitte eine Stadt auswählen.")
        else:
            st.session_state["show_results"] = True
            st.session_state["sel_location"] = sel_location
            st.session_state["sel_radius"] = sel_radius
            st.session_state["sel_category"] = sel_category
            st.session_state["sel_rating"] = sel_rating
            st.rerun()

if st.session_state.get("show_results"):
    city, state = st.session_state["sel_location"].split(", ")
    center_lat, center_lon = get_city_coordinates(city, state)

    if center_lat is None:
        st.warning("Koordinaten der Stadt konnten nicht ermittelt werden.")
    else:
        result_df = search_restaurants(
            locations=None,
            categories=st.session_state["sel_category"],
            min_rating=rating_options[st.session_state["sel_rating"]]
        )

        result_df = result_df.dropna(subset=["latitude", "longitude"])
        result_df = filter_by_radius(result_df, center_lat, center_lon, st.session_state["sel_radius"])

        # ========== Ergebnisse anzeigen ==========
        with st.container():
            st.title("Gefundene Restaurants")
            if not result_df.empty:
                if st.button("zurück zur Suche", icon=":material/arrow_back:"):
                    st.session_state["show_results"] = False
                    st.rerun()

                st.title("Gefundene Restaurants")
                st.write(f"**{len(result_df)} Restaurants im Umkreis von {st.session_state["sel_radius"]} km gefunden.**")

                for _, row in result_df.iterrows():
                    is_open = is_open_now(row.get("hours"))
                    status_label = " 🟢 Jetzt geöffnet" if is_open else " 🔴 Geschlossen"

                    with st.expander(f"{row['name']} - {row['city']}, {row['state']}  |  {status_label}"):
                        st.write(f"{row.get('categories')}")

                        st.write(f"**{row['name']}** ({round(row['distance_km'], 2)} vom Zentrum)")

                        stars = "★" * int(row['stars']) + "☆" * (5 - int(row['stars']))
                        st.markdown(f"**{stars}** ({row['stars']} Sterne)")

                        st.text(f"{row['address']}")

                        st.write("**Öffnungszeiten:**")
                        st.text(format_hours(row.get("hours")))

                        if row.get("latitude") and row.get("longitude"):
                            st.map(pd.DataFrame({
                                "latitude": [row["latitude"]],
                                "longitude": [row["longitude"]],
                            }))
            else:
                if st.button("zurück zur Suche", icon=":material/arrow_back:"):
                    st.session_state["show_results"] = False
                    st.rerun()
                st.info("Keine passenden Restaurants im Umkreis gefunden.")

