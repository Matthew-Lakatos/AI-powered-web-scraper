import statistics


def detect_spike(current_count, historical_counts):

    if not historical_counts:
        return False

    avg = statistics.mean(historical_counts)

    if current_count > avg * 2:
        return True

    return False


def sentiment_shift(current, previous):

    if previous is None:
        return False

    if abs(current - previous) > 0.5:
        return True

    return False


def check_alert(narrative):

    alerts = []

    if detect_spike(narrative["current_count"], narrative["history"]):
        alerts.append("Narrative spike detected")

    if sentiment_shift(
        narrative["sentiment"],
        narrative.get("previous_sentiment")
    ):
        alerts.append("Sentiment shift detected")

    return alerts
