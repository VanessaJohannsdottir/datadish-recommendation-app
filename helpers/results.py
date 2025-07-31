import streamlit as st
import pandas as pd

from helpers.time import is_open_now, format_hours
from helpers.map import render_single_restaurant_map
from helpers.db_reviews import get_top_labels
from helpers.labels import filter_labels
from helpers.ui import star_rating_string

def render_restaurant_expander(row):
    stars = star_rating_string(row['stars'])
    is_open = is_open_now(row.get("hours"))

    with st.expander(f"{row['name']} - {row['city']}, {row['state']} | **{stars}** ({row['stars']} Sterne)"):
        st.subheader(f"**{row['name']}**")
        st.write(f"{round(row['distance_km'], 2)} vom Zentrum")
        st.write(f"{row.get('categories')}")

        st.markdown(f"**{stars}** ({row['stars']} Sterne)")

        st.badge(
            "jetzt geöffnet" if is_open else "jetzt geschlossen",
            icon=":material/check:" if is_open else ":material/close:",
            color="green" if is_open else "red"
        )

        st.markdown("**Öffnungszeiten:**")
        st.text(format_hours(row.get("hours")))

        st.text(f"{row['address']}, {row['postal_code']} {row['city']}, {row['state']}")

        if pd.notna(row["latitude"]) and pd.notna(row["longitude"]):
            render_single_restaurant_map(row["latitude"], row["longitude"], row['name'])

        st.divider(width=50)

        st.subheader("Bewertungen")
        st.write(reviews_df)
