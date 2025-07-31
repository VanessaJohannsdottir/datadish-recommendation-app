import streamlit as st

from helpers.layout import render_layout
from helpers.data import get_cities
from helpers.labels import filter_labels, filter_categories, rating_options

from components.results import render_results

# ========== Config ==========
st.set_page_config(
    page_title="Startseite",
    initial_sidebar_state="collapsed"
)
render_layout(
    page_name="index"
)

if "show_results" not in st.session_state:
    st.session_state.show_results = False

# ========== Main ==========
cities = get_cities()
categories =  filter_categories

positive_label_values = list(filter_labels.values())

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
            value=st.session_state.get("sel_radius", 20)
        )

    sel_category = st.multiselect(
        "Was?",
        categories,
        default=st.session_state.get("sel_category", []),
        placeholder="Küche wählen"
    )
    sel_rating = st.selectbox(
        "Bewertungen",
        rating_options,
        index=ratings.index(st.session_state.get("sel_rating")) if st.session_state.get("sel_rating") else 2
    )
    sel_labels = st.pills(
        "Besondere Wünsche?",
        filter_labels,
        selection_mode="multi"
    )
    submit_button = st.button(
        "Restaurants finden",
        type="primary",
        disabled=sel_location is None
    )

    if submit_button:
        st.session_state["show_results"] = True
        st.session_state["sel_location"] = sel_location
        st.session_state["sel_radius"] = sel_radius
        st.session_state["sel_category"] = sel_category
        st.session_state["sel_rating"] = sel_rating
        st.session_state["sel_labels"] = sel_labels
        st.rerun()

if st.session_state.get("show_results"):
    render_results()