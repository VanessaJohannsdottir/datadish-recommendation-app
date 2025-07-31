import streamlit as st
import folium
from streamlit.components.v1 import html

def render_restaurant_map(lat, lon):
    m = folium.Map(location=[lat, lon], zoom_start=15)
    folium.Marker([lat, lon], icon=folium.Icon(color="red")).add_to(m)
    map_html = m._repr_html_()
    with st.popover("Karte anzeigen", icon=":material/distance:", use_container_width=False):
        html(map_html, height=300, scrolling=False)