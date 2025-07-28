import streamlit as st
from helpers.layout import render_layout

import sqlite3
import pandas as pd

# ========== Page Config & Layout ==========
st.set_page_config(
    page_title="Business Insights"
)
render_layout(page_name="pages")

# ========== Main ==========
st.title("Business Insights")