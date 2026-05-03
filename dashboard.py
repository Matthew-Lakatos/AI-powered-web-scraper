"""
dashboard.py
------------
Streamlit dashboard for the AI web intelligence + finance pipeline.

Sections
--------
1. Sidebar  — pipeline controls, URL submission, mode selection
2. Market Overview — live price ticker summary for all tracked equities
3. Sentiment vs Price — per-ticker correlation chart
4. Sentiment Distribution / Trend / Activity
5. Keywords / Topics / Emotions
6. Propaganda flags
7. Semantic Topic Clustering (PCA on embeddings)
8. Raw data table
"""

import json
import logging

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from collections import Counter

API = "http://localhost:8000"

st.set_page_config(
    page_title="AI Web Intelligence & Finance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def safe_parse(value):
    if value is None:
        return []
    try:
        return json.loads(value)
    except Exception:
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return value


def api_post(endpoint: str, **kwargs) -> bool:
    try:
        r = requests.post(f"{API}{endpoint}", timeout=10, **kwargs)
        return r.status_code == 200
    except Exception:
        return False


def load_results() -> pd.DataFrame:
    try:
        res = requests.get(f"{API}/results", timeout=10).json()
        data = res.get("results", [])
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df["last_scraped"] = pd.to_datetime(df["last_scraped"], errors="coerce", utc=True)
        return df
    except Exception:
        return pd.DataFrame()


# ---------------------------------------------------------------------------
# Sidebar — controls
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🔍 Controls")

    st.subheader("Pipeline mode")
    mode = st.radio(
        "Run pipeline as:",
        ["General", "Finance"],
        help=(
            "Finance mode scrapes curated financial news sources, "
            "market indices, government spending sites, and SEC filings. "
            "General mode uses the default URL set."
        ),
    )

    st.divider()

    # ---- Custom URL input ------------------------------------------------ #
    st.subheader("Add URLs")
    custom_urls = st.text_area(
        "Enter URLs to analyse (one per line)",
        height=140,
        placeholder=(
            "https://www.reuters.com/markets/\n"
            "https://www.usaspending.gov/explorer\n"
            "https://finance.yahoo.com/news/"
        ),
    )

    col_a, col_b = st.columns(2)

    if col_a.button("▶ Run", use_container_width=True):
        url_list = [u.strip() for u in custom_urls.splitlines() if u.strip()]
        if not url_list:
            # No custom URLs — run default or finance set
            endpoint = "/run-finance" if mode == "Finance" else "/run-default"
            ok = api_post(endpoint)
        else:
            ok = api_post("/analyze", json={"urls": url_list})
        if ok:
            st.success("Pipeline started ✓")
        else:
            st.error("API unreachable — is the server running?")

    if col_b.button("🔄 Refresh", use_container_width=True):
        st.rerun()

    st.divider()

    # ---- Discovery ------------------------------------------------------- #
    st.subheader("Topic Discovery")
    topic = st.text_input("Discover URLs by topic", placeholder="e.g. Federal Reserve")
    if st.button("Discover", use_container_width=True):
        ok = api_post("/discover", params={"topic": topic})
        st.success("Discovery queued ✓") if ok else st.error("API unreachable")

    st.divider()

    # ---- Crawl ----------------------------------------------------------- #
    st.subheader("Site Crawl")
    seed = st.text_input("Seed URL", placeholder="https://example.com")
    if st.button("Crawl", use_container_width=True):
        ok = api_post("/crawl", params={"url": seed})
        st.success("Crawl started ✓") if ok else st.error("API unreachable")

    st.divider()

    # ---- Filters --------------------------------------------------------- #
    st.subheader("Filters")
    min_cred = st.slider("Min credibility", 0.0, 1.0, 0.0, 0.05)


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

df = load_results()

if df.empty:
    st.title("AI Web Intelligence & Finance Dashboard")
    st.warning("No data yet — run the pipeline using the sidebar controls.")
    st.stop()

filtered_df = df[df["credibility"].fillna(0) >= min_cred].copy()

# ---------------------------------------------------------------------------
# Header metrics
# ---------------------------------------------------------------------------

st.title("AI Web Intelligence & Finance Dashboard")

try:
    metrics = requests.get(f"{API}/metrics", timeout=5).json()
except Exception:
    metrics = {}

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total records",  metrics.get("total_records", len(df)))
c2.metric("Unique URLs",    metrics.get("unique_urls",   df["url"].nunique()))
c3.metric("Positive",       metrics.get("sentiment_breakdown", {}).get("POSITIVE", 0))
c4.metric("Negative",       metrics.get("sentiment_breakdown", {}).get("NEGATIVE", 0))
c5.metric("Filtered",       len(filtered_df))

st.divider()


# ---------------------------------------------------------------------------
# 1. Market Overview — live prices
# ---------------------------------------------------------------------------

st.subheader("📈 Market Overview")

try:
    from finance import get_multi_ticker_summary
    from target_profiles import TICKER_MAP

    tradeable = [t for t in TICKER_MAP if not t.startswith("^")]
    indices   = [t for t in TICKER_MAP if t.startswith("^")]

    with st.spinner("Fetching live prices…"):
        eq_df  = get_multi_ticker_summary(tradeable)
        idx_df = get_multi_ticker_summary(indices)

    col_eq, col_idx = st.columns([3, 1])

    with col_eq:
        st.markdown("**Equities**")
        def colour_change(val):
            if pd.isna(val):
                return ""
            colour = "green" if val > 0 else ("red" if val < 0 else "grey")
            return f"color: {colour}"

        st.dataframe(
            eq_df.style
                .applymap(colour_change, subset=["change_1d_%", "change_5d_%"])
                .format({"price": "${:.2f}", "change_1d_%": "{:+.2f}%", "change_5d_%": "{:+.2f}%"}, na_rep="—"),
            use_container_width=True,
            hide_index=True,
        )

    with col_idx:
        st.markdown("**Indices**")
        st.dataframe(
            idx_df.style
                .applymap(colour_change, subset=["change_1d_%", "change_5d_%"])
                .format({"price": "{:,.2f}", "change_1d_%": "{:+.2f}%", "change_5d_%": "{:+.2f}%"}, na_rep="—"),
            use_container_width=True,
            hide_index=True,
        )

except ImportError:
    st.info("Install yfinance to enable live market data: `pip install yfinance`")
except Exception as e:
    st.warning(f"Market data unavailable: {e}")

st.divider()


# ---------------------------------------------------------------------------
# 2. Sentiment vs Price correlation
# ---------------------------------------------------------------------------

st.subheader("🔗 Sentiment vs Price")

try:
    from finance import correlate_sentiment_price, get_price_history
    from target_profiles import TICKER_MAP, TARGETS

    ticker_options = {t["name"]: t["ticker"] for t in TARGETS if t.get("ticker")}
    selected_name  = st.selectbox("Select entity", list(ticker_options.keys()))
    selected_ticker = ticker_options[selected_name]
    lookback_days   = st.slider("Lookback (days)", 7, 90, 30)

    # Filter DB rows to articles mentioning this entity
    entity_rows = filtered_df[
        filtered_df["url"].str.contains(selected_name.lower().replace(" ", ""), case=False, na=False)
        | filtered_df.get("targets", pd.Series(dtype=str)).str.contains(selected_name, na=False)
    ]

    sentiment_input = entity_rows[["score", "last_scraped"]].to_dict("records")

    col_chart, col_corr = st.columns([3, 1])

    with col_chart:
        price_df = get_price_history(selected_ticker, days=lookback_days)
        if price_df is not None:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=price_df.index, y=price_df["Close"],
                name="Close price", line=dict(color="#1f77b4"),
            ))
            fig.update_layout(
                title=f"{selected_name} ({selected_ticker}) — {lookback_days}d price",
                xaxis_title="Date", yaxis_title="Price (USD)",
                height=350, margin=dict(l=0, r=0, t=40, b=0),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No price data available for this ticker.")

    with col_corr:
        if sentiment_input:
            result = correlate_sentiment_price(selected_ticker, sentiment_input, days=lookback_days)
            if result:
                st.metric("Correlation", f"{result['correlation']:+.3f}")
                st.metric("p-value",     f"{result['p_value']:.3f}")
                st.metric("Trading days", result["n_days"])
                if result["p_value"] < 0.05:
                    st.success("Statistically significant (p < 0.05)")
                else:
                    st.info("Not significant at p < 0.05")
            else:
                st.info("Not enough aligned data for correlation.")
        else:
            st.info("No sentiment records match this entity yet.")

except ImportError:
    st.info("Install yfinance + scipy for correlation analysis: `pip install yfinance scipy`")
except Exception as e:
    st.warning(f"Correlation panel unavailable: {e}")

st.divider()


# ---------------------------------------------------------------------------
# 3. Sentiment distribution + trend
# ---------------------------------------------------------------------------

col_dist, col_trend = st.columns(2)

with col_dist:
    st.subheader("Sentiment Distribution")
    counts = filtered_df["sentiment"].value_counts()
    fig = px.pie(names=counts.index, values=counts.values, hole=0.35,
                 color=counts.index,
                 color_discrete_map={"POSITIVE": "#2ecc71", "NEGATIVE": "#e74c3c", "NEUTRAL": "#95a5a6"})
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300)
    st.plotly_chart(fig, use_container_width=True)

with col_trend:
    st.subheader("Sentiment Trend")
    trend = (
        filtered_df
        .groupby([pd.Grouper(key="last_scraped", freq="h"), "sentiment"])
        .size()
        .reset_index(name="count")
    )
    fig = px.line(trend, x="last_scraped", y="count", color="sentiment",
                  color_discrete_map={"POSITIVE": "#2ecc71", "NEGATIVE": "#e74c3c", "NEUTRAL": "#95a5a6"})
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300)
    st.plotly_chart(fig, use_container_width=True)

st.divider()


# ---------------------------------------------------------------------------
# 4. Keywords / Topics / Emotions
# ---------------------------------------------------------------------------

col_kw, col_topic, col_emo = st.columns(3)

with col_kw:
    st.subheader("Top Keywords")
    kws = []
    for k in filtered_df["keywords"]:
        parsed = safe_parse(k) if isinstance(k, str) else (k or [])
        kws.extend(parsed)
    if kws:
        kw_series = pd.Series(kws).value_counts().head(20)
        st.bar_chart(kw_series)
    else:
        st.info("No keywords yet.")

with col_topic:
    st.subheader("Topic Frequency")
    topics = []
    for t in filtered_df["topics"]:
        parsed = safe_parse(t) if isinstance(t, str) else (t or [])
        topics.extend(parsed)
    if topics:
        topic_series = pd.Series(topics).value_counts().head(15)
        st.bar_chart(topic_series)
    else:
        st.info("No topics yet.")

with col_emo:
    st.subheader("Emotion Analysis")
    emotion_totals = Counter()
    for e in filtered_df["emotions"]:
        parsed = safe_parse(e) if isinstance(e, str) else (e or {})
        if isinstance(parsed, dict):
            emotion_totals.update({k: float(v) for k, v in parsed.items()})
    if emotion_totals:
        emo_df = pd.DataFrame(emotion_totals.items(), columns=["emotion", "score"])
        fig = px.bar(emo_df, x="emotion", y="score",
                     color="emotion", color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=0), height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No emotion data yet.")

st.divider()


# ---------------------------------------------------------------------------
# 5. Propaganda flags
# ---------------------------------------------------------------------------

st.subheader("🚩 Propaganda Flags")

prop_rows = filtered_df[filtered_df["propaganda_score"].fillna(0) > 0.1].copy()

if not prop_rows.empty:
    prop_rows = prop_rows.sort_values("propaganda_score", ascending=False)
    fig = px.bar(
        prop_rows.head(20),
        x="url", y="propaganda_score",
        color="propaganda_score",
        color_continuous_scale="Reds",
        labels={"propaganda_score": "Score", "url": "URL"},
    )
    fig.update_layout(xaxis_tickangle=-35, height=350, margin=dict(l=0, r=0, t=10, b=80))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No significant propaganda signals detected yet.")

st.divider()


# ---------------------------------------------------------------------------
# 6. Semantic Topic Clustering
# ---------------------------------------------------------------------------

st.subheader("🗺 Semantic Topic Clustering")

if "embedding" in filtered_df.columns:
    try:
        embeddings = []
        indices    = []

        for i, e in enumerate(filtered_df["embedding"]):
            if isinstance(e, str):
                try:
                    e = json.loads(e)
                except Exception:
                    continue
            if isinstance(e, list) and len(e) > 0:
                embeddings.append(e)
                indices.append(i)

        if len(embeddings) > 10:
            from sklearn.decomposition import PCA

            reduced = PCA(n_components=2).fit_transform(np.array(embeddings))

            cluster_df = pd.DataFrame({
                "x":         reduced[:, 0],
                "y":         reduced[:, 1],
                "sentiment": filtered_df["sentiment"].iloc[indices].values,
                "url":       filtered_df["url"].iloc[indices].values,
            })

            fig = px.scatter(
                cluster_df, x="x", y="y",
                color="sentiment", hover_data=["url"],
                color_discrete_map={"POSITIVE": "#2ecc71", "NEGATIVE": "#e74c3c", "NEUTRAL": "#95a5a6"},
            )
            fig.update_layout(height=420, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"Need at least 11 records with embeddings — have {len(embeddings)} so far.")

    except Exception as exc:
        st.info(f"Clustering unavailable: {exc}")

st.divider()


# ---------------------------------------------------------------------------
# 7. Semantic Search
# ---------------------------------------------------------------------------

st.subheader("🔎 Semantic Search")

query = st.text_input("Search scraped content by meaning", placeholder="Federal Reserve interest rate decision")

if query:
    try:
        res = requests.get(f"{API}/semantic-search", params={"query": query, "k": 10}, timeout=10)
        if res.status_code == 200:
            results = res.json().get("results", [])
            if results:
                for r in results:
                    score = r.pop("score", None)
                    label = f"score={score:.3f}" if score is not None else ""
                    st.markdown(f"**{r.get('url', r)}** {label}")
            else:
                st.info("No results found.")
    except Exception:
        st.warning("Semantic search unavailable — is the API running?")

st.divider()


# ---------------------------------------------------------------------------
# 8. Raw data table
# ---------------------------------------------------------------------------

st.subheader("📋 Scraped Data")

display_cols = [c for c in ["url", "sentiment", "score", "credibility",
                             "propaganda_score", "topics", "summary", "last_scraped"]
                if c in filtered_df.columns]

st.dataframe(
    filtered_df[display_cols].sort_values("last_scraped", ascending=False),
    use_container_width=True,
)
