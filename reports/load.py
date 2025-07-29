from reports import table
import streamlit as st

# Lädt die Tabelle (Datenbasis) nur einmal beim ersten Start , nicht bei jedem Seiten_Reload
@st.cache_resource
def init_server():
    return table.Table()