"""
finance.py
----------
Market price data and sentiment-correlation utilities.

Requires:  pip install yfinance

Public API
----------
get_price_history(ticker, days)
    Fetch OHLCV data for a ticker over the last *days* calendar days.
    Returns a pandas DataFrame or None on failure.

get_current_price(ticker)
    Return the latest closing price as a float, or None.

correlate_sentiment_price(ticker, sentiment_rows, days)
    Given a list of DB rows (each with a 'score' and 'last_scraped'),
    compute the Pearson correlation between daily mean sentiment and
    next-day price return.  Returns a dict with 'correlation', 'p_value',
    'n_days', and aligned DataFrames for plotting.

get_multi_ticker_summary(tickers)
    Return a DataFrame of latest price, 1-day change %, and 5-day change %
    for a list of tickers.  Used by the dashboard market overview panel.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal: lazy yfinance import so the rest of the app doesn't crash if
# yfinance isn't installed yet.
# ---------------------------------------------------------------------------

def _yf():
    try:
        import yfinance as yf
        return yf
    except ImportError:
        raise ImportError(
            "yfinance is required for finance features. "
            "Run: pip install yfinance"
        )


# ---------------------------------------------------------------------------
# Price data
# ---------------------------------------------------------------------------

def get_price_history(
    ticker: str,
    days: int = 30,
) -> Optional[pd.DataFrame]:
    """
    Fetch daily OHLCV data for *ticker* over the last *days* calendar days.

    Returns
    -------
    DataFrame with columns [Open, High, Low, Close, Volume] indexed by date,
    or None if the fetch fails or returns empty data.
    """
    yf = _yf()
    end   = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    try:
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(start=start.strftime("%Y-%m-%d"),
                                end=end.strftime("%Y-%m-%d"),
                                interval="1d")
        if df.empty:
            logger.warning("get_price_history: no data returned for %s", ticker)
            return None

        df.index = pd.to_datetime(df.index).normalize().tz_localize(None)
        return df[["Open", "High", "Low", "Close", "Volume"]]

    except Exception:
        logger.warning("get_price_history: failed for %s", ticker, exc_info=True)
        return None


def get_current_price(ticker: str) -> Optional[float]:
    """Return the most recent closing price for *ticker*, or None."""
    df = get_price_history(ticker, days=5)
    if df is None or df.empty:
        return None
    return round(float(df["Close"].iloc[-1]), 4)


def get_multi_ticker_summary(tickers: list[str]) -> pd.DataFrame:
    """
    Return a summary DataFrame for a list of tickers.

    Columns: ticker, name (from TICKER_MAP), price, change_1d_pct, change_5d_pct
    Rows with failed fetches are included with NaN prices.
    """
    from target_profiles import TICKER_MAP

    rows = []
    for ticker in tickers:
        df = get_price_history(ticker, days=10)
        if df is not None and len(df) >= 2:
            price      = round(float(df["Close"].iloc[-1]), 2)
            chg_1d     = round((df["Close"].iloc[-1] / df["Close"].iloc[-2] - 1) * 100, 2)
            chg_5d_idx = max(0, len(df) - 6)
            chg_5d     = round((df["Close"].iloc[-1] / df["Close"].iloc[chg_5d_idx] - 1) * 100, 2)
        else:
            price = chg_1d = chg_5d = float("nan")

        rows.append({
            "ticker":       ticker,
            "name":         TICKER_MAP.get(ticker, ticker),
            "price":        price,
            "change_1d_%":  chg_1d,
            "change_5d_%":  chg_5d,
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Sentiment ↔ price correlation
# ---------------------------------------------------------------------------

def correlate_sentiment_price(
    ticker: str,
    sentiment_rows: list[dict],
    days: int = 30,
) -> Optional[dict]:
    """
    Compute Pearson correlation between daily mean sentiment score and
    next-day price return for *ticker*.

    Parameters
    ----------
    ticker         : Yahoo Finance ticker symbol.
    sentiment_rows : list of dicts, each with 'score' (float) and
                     'last_scraped' (ISO-8601 string).
    days           : lookback window in calendar days.

    Returns
    -------
    dict with:
        correlation  : float [-1, 1]
        p_value      : float
        n_days       : int  (number of aligned trading days)
        sentiment_df : DataFrame with date + mean_sentiment
        price_df     : DataFrame with date + next_day_return
    or None if there is insufficient data.
    """
    try:
        from scipy.stats import pearsonr
    except ImportError:
        logger.warning("scipy not installed — skipping correlation. pip install scipy")
        return None

    price_df = get_price_history(ticker, days=days + 5)
    if price_df is None or len(price_df) < 5:
        return None

    # ---- Build daily sentiment series ------------------------------------ #
    records = []
    for row in sentiment_rows:
        try:
            dt    = pd.to_datetime(row["last_scraped"]).normalize().tz_localize(None)
            score = float(row["score"])
            records.append({"date": dt, "score": score})
        except Exception:
            continue

    if not records:
        return None

    sent_df = (
        pd.DataFrame(records)
        .groupby("date")["score"]
        .mean()
        .rename("mean_sentiment")
        .reset_index()
    )

    # ---- Build next-day return series ------------------------------------ #
    price_df = price_df.copy()
    price_df["next_day_return"] = price_df["Close"].pct_change().shift(-1)
    price_df = price_df.dropna(subset=["next_day_return"]).reset_index()
    price_df = price_df.rename(columns={"index": "date"})
    price_df["date"] = pd.to_datetime(price_df["date"]).dt.normalize()

    # ---- Align on trading dates ------------------------------------------ #
    merged = pd.merge(sent_df, price_df[["date", "next_day_return"]], on="date", how="inner")

    if len(merged) < 3:
        logger.info("correlate_sentiment_price: only %d aligned days for %s — skipping", len(merged), ticker)
        return None

    corr, p_val = pearsonr(merged["mean_sentiment"], merged["next_day_return"])

    return {
        "correlation":  round(corr, 4),
        "p_value":      round(p_val, 4),
        "n_days":       len(merged),
        "sentiment_df": merged[["date", "mean_sentiment"]],
        "price_df":     merged[["date", "next_day_return"]],
        "merged_df":    merged,
    }
