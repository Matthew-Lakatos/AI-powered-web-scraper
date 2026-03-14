import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from collections import Counter
import numpy as np

API = "http://localhost:8000"

st.set_page_config(page_title="AI Scraper Dashboard", layout="wide")

st.title("AI Web Intelligence Dashboard")

# -------------------------
# USER URL INPUT
# -------------------------

st.subheader("Analyze Websites")

urls = st.text_area(
    "Enter URLs (one per line)"
)

col1, col2 = st.columns(2)

if col1.button("Submit URLs"):

    url_list = [u.strip() for u in urls.split("\n") if u.strip()]

    if not url_list:
        st.warning("Please enter at least one URL")

    else:

        response = requests.post(
            f"{API}/analyze",
            json={"urls": url_list}
        )

        if response.status_code == 200:
            st.success("URLs submitted for analysis")
        else:
            st.error("Submission failed")


if col2.button("Refresh Data"):
    st.rerun()

# -------------------------
# GLOBAL DISCOVERY
# -------------------------

st.subheader("Global Discovery")

topic = st.text_input("Topic")

if st.button("Discover and Analyze"):

    requests.post(
        f"{API}/discover",
        params={"topic": topic}
    )

    st.success("Discovery started")

# -------------------------
# WEBSITE CRAWL
# -------------------------

st.subheader("Website Crawl")

crawl_url = st.text_input("Seed URL")

if st.button("Start Crawl"):

    requests.post(
        f"{API}/crawl",
        params={"url": crawl_url}
    )

    st.success("Crawler started")

# -------------------------
# SEMANTIC SEARCH
# -------------------------

st.subheader("Semantic Search")

query = st.text_input("Search by meaning (not keywords)")

semantic_results = None

if query:

    try:

        res = requests.get(
            f"{API}/semantic-search",
            params={"query": query, "k": 10}
        )

        if res.status_code == 200:
            semantic_results = res.json()

    except Exception:
        st.warning("Semantic search unavailable")

if semantic_results:

    st.write("### Semantic Results")

    for r in semantic_results["results"]:

        st.write(r)

# -------------------------
# LOAD DATA
# -------------------------

res = requests.get(f"{API}/results").json()
data = res["results"]

if not data:
    st.warning("No data yet.")
    st.stop()

df = pd.DataFrame(data)

df["last_scraped"] = pd.to_datetime(df["last_scraped"])

# -------------------------
# FILTERS
# -------------------------

st.subheader("Data Filters")

credibility_threshold = st.slider(
    "Minimum Credibility",
    min_value=0.0,
    max_value=1.0,
    value=0.0,
    step=0.05
)

filtered_df = df[df["credibility"].fillna(0) >= credibility_threshold]

# -------------------------
# METRICS
# -------------------------

metrics = requests.get(f"{API}/metrics").json()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Records", metrics["total_records"])
col2.metric("Unique URLs", metrics["unique_urls"])
col3.metric("Positive Sentiment", metrics["sentiment_breakdown"].get("POSITIVE", 0))
col4.metric("Filtered Records", len(filtered_df))

st.divider()

# -------------------------
# SENTIMENT DISTRIBUTION
# -------------------------

st.subheader("Sentiment Distribution")

sentiment_counts = filtered_df["sentiment"].value_counts()

fig = px.pie(
    names=sentiment_counts.index,
    values=sentiment_counts.values
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------
# SENTIMENT TREND
# -------------------------

st.subheader("Sentiment Trend")

trend = filtered_df.groupby([
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

# -------------------------
# SCRAPING ACTIVITY
# -------------------------

st.subheader("Scraping Activity")

activity = filtered_df.groupby(
    pd.Grouper(key="last_scraped", freq="H")
).size().reset_index(name="scrapes")

fig = px.bar(activity, x="last_scraped", y="scrapes")

st.plotly_chart(fig, use_container_width=True)

# -------------------------
# KEYWORDS
# -------------------------

st.subheader("Top Keywords")

keywords = []

for k in filtered_df["keywords"]:
    if isinstance(k, list):
        keywords.extend(k)

if keywords:

    kw_series = pd.Series(keywords).value_counts().head(20)

    st.bar_chart(kw_series)

# -------------------------
# TOPICS
# -------------------------

st.subheader("Topic Frequency")

topics = []

for t in filtered_df["topics"]:
    if isinstance(t, list):
        topics.extend(t)

if topics:

    topic_series = pd.Series(topics).value_counts().head(15)

    st.bar_chart(topic_series)

# -------------------------
# EMOTIONS
# -------------------------

st.subheader("Emotion Analysis")

emotion_totals = Counter()

for e in filtered_df["emotions"]:
    if isinstance(e, dict):
        emotion_totals.update(e)

if emotion_totals:

    emotion_df = pd.DataFrame(
        emotion_totals.items(),
        columns=["emotion", "count"]
    )

    fig = px.bar(emotion_df, x="emotion", y="count")

    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# TOPIC CLUSTERING (Embeddings)
# -------------------------

st.subheader("Semantic Topic Clustering")

if "embedding" in filtered_df.columns:

    try:

        embeddings = []

        for e in filtered_df["embedding"]:
            if isinstance(e, list):
                embeddings.append(e)

        if len(embeddings) > 10:

            embeddings = np.array(embeddings)

            # simple PCA projection
            from sklearn.decomposition import PCA

            pca = PCA(n_components=2)

            reduced = pca.fit_transform(embeddings)

            cluster_df = pd.DataFrame({
                "x": reduced[:, 0],
                "y": reduced[:, 1],
                "sentiment": filtered_df["sentiment"].values[:len(reduced)]
            })

            fig = px.scatter(
                cluster_df,
                x="x",
                y="y",
                color="sentiment"
            )

            st.plotly_chart(fig, use_container_width=True)

    except Exception:

        st.info("Embedding clustering will activate once embeddings are stored.")

# -------------------------
# DATA TABLE
# -------------------------

st.subheader("Scraped Data")

st.dataframe(filtered_df)
