import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import json
from collections import Counter

API = "http://localhost:8000"

st.set_page_config(page_title="AI Scraper Dashboard", layout="wide")

st.title("AI Web Scraper Analytics Dashboard")

# Fetch data
res = requests.get(f"{API}/results").json()

data = res["results"]

if not data:
    st.warning("No data yet.")
    st.stop()

df = pd.DataFrame(data)

df["last_scraped"] = pd.to_datetime(df["last_scraped"])

# -------------------------------
# METRICS
# -------------------------------

metrics = requests.get(f"{API}/metrics").json()

col1, col2, col3 = st.columns(3)

col1.metric("Total Records", metrics["total_records"])
col2.metric("Unique URLs", metrics["unique_urls"])
col3.metric("Positive Sentiment", metrics["sentiment_breakdown"].get("POSITIVE",0))

st.divider()

# -------------------------------
# SENTIMENT DISTRIBUTION
# -------------------------------

st.subheader("Sentiment Distribution")

sentiment_counts = df["sentiment"].value_counts()

fig = px.pie(
    names=sentiment_counts.index,
    values=sentiment_counts.values,
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# SENTIMENT TREND
# -------------------------------

st.subheader("Sentiment Trend")

trend = df.groupby([
    pd.Grouper(key="last_scraped", freq="H"),
    "sentiment"
]).size().reset_index(name="count")

fig = px.line(
    trend,
    x="last_scraped",
    y="count",
    color="sentiment"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# SCRAPING ACTIVITY
# -------------------------------

st.subheader("Scraping Activity")

activity = df.groupby(
    pd.Grouper(key="last_scraped", freq="H")
).size().reset_index(name="scrapes")

fig = px.bar(
    activity,
    x="last_scraped",
    y="scrapes"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# KEYWORD ANALYTICS
# -------------------------------

st.subheader("Top Keywords")

keywords = []

for row in df["keywords"]:
    if isinstance(row, list):
        keywords.extend(row)

kw_series = pd.Series(keywords).value_counts().head(20)

st.bar_chart(kw_series)

# -------------------------------
# TOPICS
# -------------------------------

st.subheader("Topic Frequency")

topics = []

for t in df["topics"]:
    if isinstance(t, list):
        topics.extend(t)

topic_counts = pd.Series(topics).value_counts().head(15)

st.bar_chart(topic_counts)

# -------------------------------
# EMOTION ANALYSIS
# -------------------------------

st.subheader("Emotion Analysis")

emotion_totals = Counter()

for e in df["emotions"]:
    if isinstance(e, dict):
        emotion_totals.update(e)

emotion_df = pd.DataFrame(
    emotion_totals.items(),
    columns=["emotion","count"]
)

fig = px.bar(
    emotion_df,
    x="emotion",
    y="count"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# DATA TABLE
# -------------------------------

st.subheader("Scraped Data")

st.dataframe(df)
