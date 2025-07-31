import streamlit as st
import pandas as pd
from helpers.time import is_open_now, format_hours
from helpers.map import render_restaurant_map
from helpers.labels import filter_labels
from helpers.ui import star_rating_string


def render_restaurant_expander(row, top_labels):
    stars = star_rating_string(row['stars'])
    is_open = is_open_now(row.get("hours"))

    with st.expander(f"{row['name']} - {row['city']}, {row['state']} | **{stars}** ({row['stars']} STERNE)"):

        # --- Titel & Öffnungsstatus in einer Zeile --- #
        st.subheader(f"**{row['name']}**")
        st.badge(
            "jetzt geöffnet" if is_open else "jetzt geschlossen",
            icon=":material/check:" if is_open else ":material/close:",
            color="green" if is_open else "primary"
        )

        # --- Bewertungen & Label --- #
        st.markdown(f"**{stars}** ({row['stars']} Sterne)")

        for i, label in enumerate(top_labels):
            readable = next((k for k, v in filter_labels.items() if v == label), label)
            st.badge(
                readable,
                icon=":material/check:",
                color="blue"
            )

        st.divider()

        # --- Öffnungszeiten & Standort --- #
        col_bottom_1, col_bottom_2 = st.columns([1, 2])
        with col_bottom_1:
            st.markdown("**Öffnungszeiten:**")
            st.text(format_hours(row.get("hours")))
        with col_bottom_2:
            st.markdown("**Adresse:**")
            st.badge(f"{row['address']}, \n{row['postal_code']} {row['city']}, {row['state']}", icon=":material/location_on:", color="gray", width="stretch")
            st.write(f"{round(row['distance_km'], 2)} km vom Zentrum")
            if pd.notna(row["latitude"]) and pd.notna(row["longitude"]):
                render_restaurant_map(row["latitude"], row["longitude"])

        st.divider()

        st.write(f"{row.get('categories')}")
        st.markdown("")