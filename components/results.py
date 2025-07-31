import streamlit as st

from helpers.data import (
    get_restaurants,
    get_labels_for_businesses,
    get_top_labels
)
from helpers.labels import filter_labels, positive_labels, rating_options
from helpers.time import is_open_now
from helpers.geo import get_city_coordinates, filter_by_radius

from components.single_expander import render_restaurant_expander

def render_results():
    '''
    Gibt eine Ergebnisliste der gefilterten Restaurants aus. Dabei wird der session_state["show_results"] auf True gesetzt.
    '''
    city, state = st.session_state["sel_location"].split(", ")
    center_lat, center_lon = get_city_coordinates(city, state)

    if center_lat is None:
        st.warning("Koordinaten der Stadt konnten nicht ermittelt werden.")
    else:
        # DF mit gefilterten Businesses (außer Labels)
        result_df = get_restaurants(
            locations=None,
            categories=st.session_state["sel_category"],
            min_rating=rating_options[st.session_state["sel_rating"]]
        )

        result_df = result_df.dropna(subset=["latitude", "longitude"])
        result_df = filter_by_radius(result_df, center_lat, center_lon, st.session_state["sel_radius"]) # gewählten Radius mit einbeziehen

        selected_labels = [filter_labels[label] for label in st.session_state["sel_labels"]] # -> Liste mit label-keys

        business_ids = result_df["business_id"].tolist() # -> Liste mit business_ids aus result_df
        labels_df = get_labels_for_businesses(business_ids) # -> DF mit Labels

        review_counts = labels_df.groupby("business_id")["review_id"].nunique() # Anzahl an Gesamtbewertungen pro Business

        if not selected_labels:
            result_df["top_labels"] = result_df["business_id"].apply(
                lambda b_id: get_top_labels(b_id, allowed_labels=list(filter_labels.values()), threshold=0.3)
            )
        else:
            @st.cache_data
            def has_required_labels(business_id):
                total_reviews = review_counts.get(business_id, 0)
                if total_reviews == 0:
                    return False
                business_labels = labels_df[labels_df["business_id"] == business_id]
                for label in selected_labels:
                    cnt = business_labels[business_labels["label"] == label]["review_id"].nunique()
                    if cnt / total_reviews < 0.3:
                        return False
                return True
            result_df = result_df[result_df["business_id"].apply(has_required_labels)]

            result_df["top_labels"] = result_df["business_id"].apply(
                lambda b_id: get_top_labels(b_id, allowed_labels=list(filter_labels.values()), threshold=0.3)
            )

        # ========== Ergebnisse anzeigen ==========
        result_df["open_now"] = result_df["hours"].apply(is_open_now)
        open_now = result_df[result_df["open_now"]]
        closed_now = result_df[~result_df["open_now"]]

        with st.container():
            if not result_df.empty:
                if st.button("zurück zur Suche", icon=":material/arrow_back:"):
                    st.session_state["show_results"] = False
                    st.rerun()

                st.title("Gefundene Restaurants")
                total_found = len(open_now) + len(closed_now)
                st.write(f"**{total_found} Restaurants im Umkreis von {st.session_state['sel_radius']} km um {st.session_state['sel_location']} gefunden.**")

                if not open_now.empty:
                    st.markdown('''**:green[jetzt geöffnet]**''')
                    for _, row in open_now.iterrows():
                        render_restaurant_expander(row, row["top_labels"])

                if not closed_now.empty:
                    st.markdown('''**:primary[jetzt geschlossen]**''')
                    for _, row in closed_now.iterrows():
                        render_restaurant_expander(row, row["top_labels"])
            else:
                if st.button("zurück zur Suche", icon=":material/arrow_back:"):
                    st.session_state["show_results"] = False
                    st.rerun()
                st.info("Keine passenden Restaurants im Umkreis gefunden.")