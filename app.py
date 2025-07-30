import streamlit as st
from helpers.layout import render_layout
from helpers.db import get_cities_and_categories, search_restaurants
from helpers.time import is_open_now, format_hours
from helpers.geo import get_city_coordinates, filter_by_radius
# from helpers.map import render_single_restaurant_map # Es gibt keine map.py-Datei im Ordner helpers. Hebe das Auskommentieren bitte erst auf, nachdem du die Datei hinzugefügt hast.
from helpers.results import render_restaurant_expander

from reports.load import init_server


# ========== Config ==========
st.set_page_config(
    page_title="DataDish - Restaurant Finder",
    initial_sidebar_state="collapsed"
)
render_layout(
    page_name="index"
)

# Diese Funktion ist verantwortlich für das Laden aller CSV-Dateien und Datensätze.
# Sie muss zu Beginn der Anwendung ausgeführt werden und darf weder entfernt noch verschoben werden.
# Das Initialisieren kann bis zu 20 Sekunden dauern, da umfangreiche Daten verarbeitet werden.
# Die geladenen Ergebnisse werden zwischengespeichert (Cache), sodass spätere Zugriffe ohne Verzögerung erfolgen können.
init_server()

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

        open_now = result_df[result_df["hours"].apply(is_open_now)]
        closed_now = result_df[~result_df["hours"].apply(is_open_now)]

        # ========== Ergebnisse anzeigen ==========
        with st.container():
            if not result_df.empty:
                if st.button("zurück zur Suche", icon=":material/arrow_back:"):
                    st.session_state["show_results"] = False
                    st.rerun()

                st.title("Gefundene Restaurants")
                total_found = len(open_now) + len(closed_now)
                st.write(f"**{total_found} Restaurants im Umkreis von {st.session_state['sel_radius']} km um {st.session_state["sel_location"]} gefunden.**")

                if not open_now.empty:
                    st.markdown('''**:green[jetzt geöffnet]**''')
                    for _, row in open_now.iterrows():
                        render_restaurant_expander(row)

                if not closed_now.empty:
                    st.markdown('''**:red[jetzt geschlossen]**''')
                    for _, row in closed_now.iterrows():
                        render_restaurant_expander(row)
            else:
                if st.button("zurück zur Suche", icon=":material/arrow_back:"):
                    st.session_state["show_results"] = False
                    st.rerun()
                st.info("Keine passenden Restaurants im Umkreis gefunden.")

