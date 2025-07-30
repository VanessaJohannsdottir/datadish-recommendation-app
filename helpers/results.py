import streamlit as st
import pandas as pd

from helpers.time import is_open_now, format_hours
from helpers.map import render_single_restaurant_map
from helpers.db import get_reviews_by_business_id

def render_restaurant_expander(row):
    stars = "★" * int(row['stars']) + "☆" * (5 - int(row['stars']))
    is_open = is_open_now(row.get("hours"))
    reviews_df = get_reviews_by_business_id(row['business_id'])

    with st.expander(f"{row['name']} - {row['city']}, {row['state']} | **{stars}** ({row['stars']} Sterne)"):
        st.subheader(f"**{row['name']}**")
        st.write(f"{round(row['distance_km'], 2)} vom Zentrum")
        st.write(f"{row.get('categories')}")

        st.markdown(f"**{stars}** ({row['stars']} Sterne)")
        #st.divider(width=50)
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
            pass

        st.divider(width=50)

        st.subheader("Bewertungen")
        st.write(reviews_df)
