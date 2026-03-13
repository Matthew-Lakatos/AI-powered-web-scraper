import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

st.title("Web Sentiment & NLP Dashboard")

# Stats
stats = requests.get(f"{API_URL}/stats").json()
st.subheader("Pipeline Stats")
st.json(stats)

# Results
data = requests.get(f"{API_URL}/results").json()["results"]
df = pd.DataFrame(data, columns=[
    "url", "sentiment", "score", "keywords", "topics", "summary", "emotions", "last_scraped"
])

st.subheader("Scraped Results")
st.dataframe(df)

# Trigger scrape
st.subheader("Trigger New Scrape")
urls = st.text_area("Enter URLs (one per line)").splitlines()
if st.button("Scrape"):
    requests.post(f"{API_URL}/scrape", json=urls)
    st.success("Scrape triggered!")
