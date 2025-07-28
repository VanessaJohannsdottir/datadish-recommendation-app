import streamlit as st
from helpers.layout import render_layout

import sqlite3
import pandas as pd

# ========== Page Config & Layout ==========
st.set_page_config(
    page_title="Ergebnisse"
)
render_layout(page_name="pages")

if "filter_data" not in st.session_state:
    st.warning("Keine Filterkriterien gefunden. Bitte zurück zur Suche.")
    st.stop()

filters = st.session_state["filter_data"]
sel_location = filters["location"]
sel_category = filters["category"]
sel_price = filters["price"]
sel_rating = filters["rating"]

# Abfrage vorbereiten
base_query = "SELECT DISTINCT b.* FROM business b"
joins = ""
conditions = ["1=1"]
params = []

if sel_location:
    placeholders = ",".join(["?"] * len(sel_location))
    conditions.append(f"b.city IN ({placeholders})")
    params.extend(sel_location)

if sel_category:
    joins += " JOIN business_categories bc ON b.business_id = bc.business_id"
    placeholders = ",".join(["?"] * len(sel_category))
    conditions.append(f"bc.category IN ({placeholders})")
    params.extend(sel_category)

if sel_rating:
    conditions.append("b.stars >= ?")
    params.append(["min. ★☆☆☆☆", "min. ★★☆☆☆", "min. ★★★☆☆", "min. ★★★★☆", "min. ★★★★★"].index(sel_rating))

# SQL ausführen
query = f"{base_query} {joins} WHERE {' AND '.join(conditions)}"
conn = sqlite3.connect("./yelp.db")
result_df = pd.read_sql_query(query, conn, params=params)
conn.close()

# Ergebnisse
with st.container():
    st.title("Gefundene Restaurants")
    if not result_df.empty:
        st.write(f"**{len(result_df)} Restaurants gefunden.**")

        offene = result_df[result_df["is_open"] == 1]
        geschlossene = result_df[result_df["is_open"] == 0]

        if not offene.empty:
            for _, row in offene.iterrows():
                with st.expander(f"{row['name']} - {row['city']}, {row['state']} \n **{row['stars']} Sterne**"):
                    st.write(f"**{row['name']}**")
        else:
            st.info("Keine offenen Restaurants gefunden.")

        if not geschlossene.empty:
            st.subheader("Geschlossene Restaurants")
            for _, row in geschlossene.iterrows():
                st.markdown(f"**{row['name']}**  \n{row['city']}  \n{row['stars']} Sterne")
    else:
        st.info("Keine passenden Restaurants gefunden.")

    st.markdown("---")
    if st.button("Zurück zur Suche", type="primary"):
        st.switch_page("app.py")