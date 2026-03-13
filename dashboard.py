import streamlit as st
import requests
import pandas as pd

from config import settings

API_URL = f"http://{settings.api_host}:{settings.api_port}"


def main():
    st.title("Web Sentiment & NLP Dashboard")

    # Stats
    st.subheader("Pipeline Stats")
    try:
        stats = requests.get(f"{API_URL}/stats").json()
        st.json(stats)
    except Exception as e:
        st.error(f"Could not fetch stats: {e}")

    # Results
    st.subheader("Scraped Results")
    try:
        data = requests.get(f"{API_URL}/results").json()["results"]
        df = pd.DataFrame(
            data,
            columns=[
                "url",
                "sentiment",
                "score",
                "keywords",
                "topics",
                "summary",
                "emotions",
                "last_scraped",
            ],
        )
        st.dataframe(df)
    except Exception as e:
        st.error(f"Could not fetch results: {e}")

    # Trigger scrape
    st.subheader("Trigger New Scrape")
    urls_text = st.text_area("Enter URLs (one per line)")
    urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
    if st.button("Scrape") and urls:
        try:
            resp = requests.post(f"{API_URL}/scrape", json=urls)
            if resp.status_code == 200:
                st.success("Scrape triggered!")
            else:
                st.error(f"Error triggering scrape: {resp.text}")
        except Exception as e:
            st.error(f"Error triggering scrape: {e}")


if __name__ == "__main__":
    main()
