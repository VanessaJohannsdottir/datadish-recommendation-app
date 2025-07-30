import streamlit as st
import folium
from streamlit.components.v1 import html

def render_single_restaurant_map(lat, lon, name):
    m = folium.Map(location=[lat, lon], zoom_start=15)
    folium.Marker([lat, lon], tooltip=name, icon=folium.Icon(color="blue")).add_to(m)
    map_html = m._repr_html_()
    with st.popover("🖈 auf Karte zeigen"):
        html(map_html, height=400, scrolling=False)