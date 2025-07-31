import streamlit as st

from helpers.db_connection import get_df

@st.cache_data
def get_labels_for_business(business_id):
    query="SELECT rl.review_id, rl.label FROM review_label rl JOIN reviews r ON rl.review_id = r.review_id WHERE r.business_id = ? ORDER BY r.date DESC"
    labels = get_df(query, db_path="yelp.db", params=(business_id,))
    return labels

@st.cache_data
def get_top_labels(business_id, allowed_labels, threshold=0.1):
    query="SELECT r.business_id, rl.label FROM review_label rl JOIN reviews r ON rl.review_id = r.review_id WHERE r.business_id = ?"
    df = get_df(query, db_path="yelp.db", params=(business_id,))

    top_labels = df[df["label"].isin(allowed_labels)]

    if top_labels.empty:
        return []

    label_counts = top_labels["label"].value_counts()
    total_reviews = df.shape[0]

    label_freq = (label_counts / total_reviews).to_dict()
    frequent_labels = [label for label, freq in label_freq.items() if freq >= threshold]

    return frequent_labels