import numpy as np
from datetime import datetime, timedelta
from core import database, utils

def analyze_trend(data_points: list[float], threshold: float = 0.1) -> str:
    """
    Analyzes a list of numerical data points to determine if there's a trend.
    Returns "trending_up", "trending_down", or "stable".

    :param data_points: A list of numerical values (e.g., HRV over time).
    :param threshold: The minimum percentage change required to consider it a trend.
    :return: A string indicating the trend.
    """
    if len(data_points) < 2:
        return "stable"

    # Simple heuristic: compare start and end points
    start_value = data_points[0]
    end_value = data_points[-1]

    percentage_change = (end_value - start_value) / start_value if start_value != 0 else 0

    if percentage_change > threshold:
        return "trending_up"
    elif percentage_change < -threshold:
        return "trending_down"
    else:
        return "stable"

def get_predictive_context(user_id: str, historical_data: list[dict]) -> dict:
    """
    Generates a predictive context for a user based on historical health data.
    Fetches 24-hour aggregated window for better trend analysis.

    :param user_id: The ID of the user.
    :param historical_data: A list of dictionaries (legacy/immediate context).
    :return: A dictionary with predictive insights.
    """
    # Fetch last 24 hours of data
    end_ts = int(datetime.now().timestamp() * 1000)
    start_ts = int((datetime.now() - timedelta(hours=24)).timestamp() * 1000)
    
    raw_range_data = database.get_health_data_range(user_id, start_ts, end_ts)
    
    # Aggregate into adaptive buckets based on volatility
    # If HR is steady, we get 2-hour chunks. If volatile, we get 5-min chunks.
    aggregated_data = utils.adaptive_aggregate_data(
        raw_range_data, 
        min_window_ms=300000,    # 5 Minutes
        max_window_ms=7200000,   # 2 Hours
        threshold=10.0,          # HR StdDev threshold
        target_metric='heart_rate',
        metrics=['heart_rate', 'hrv', 'sleep_score']
    )
    
    # Use aggregated data for trends if available, else fallback to raw history
    data_source = aggregated_data if aggregated_data else historical_data

    hrv_data = [d.get('hrv', 0) for d in data_source if d.get('hrv') is not None]
    heart_rate_data = [d.get('heart_rate', 0) for d in data_source if d.get('heart_rate') is not None]
    sleep_score_data = [d.get('sleep_score', 0) for d in data_source if d.get('sleep_score') is not None]

    hrv_trend = analyze_trend(hrv_data)
    heart_rate_trend = analyze_trend(heart_rate_data)
    sleep_score_trend = analyze_trend(sleep_score_data)

    # Basic heuristic for overall readiness
    overall_readiness = "neutral"
    if hrv_trend == "trending_up" and sleep_score_trend == "trending_up":
        overall_readiness = "high"
    elif hrv_trend == "trending_down" and sleep_score_trend == "trending_down":
        overall_readiness = "low"
    
    # Placeholder for more complex predictions (e.g., risk of burnout)
    burnout_risk = "low"
    if hrv_trend == "trending_down" and sleep_score_trend == "trending_down" and len(data_source) > 5:
        # More sophisticated logic here, e.g., sustained low HRV and sleep
        burnout_risk = "medium"


    return {
        "user_id": user_id,
        "hrv_trend": hrv_trend,
        "heart_rate_trend": heart_rate_trend,
        "sleep_score_trend": sleep_score_trend,
        "overall_readiness": overall_readiness,
        "burnout_risk": burnout_risk,
        "analysis_window": "24h_adaptive" if aggregated_data else "recent_raw"
    }
