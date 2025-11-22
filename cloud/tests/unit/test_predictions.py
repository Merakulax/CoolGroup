import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from core.predictions import analyze_trend
from core.utils import adaptive_aggregate_data

# Mock data for testing adaptive_aggregate_data
# Create data points with steady HR then a spike then steady again
def generate_mock_data(start_time, num_points, interval_seconds, steady_hr, volatile_hr_range, steady_hr_2):
    data = []
    current_time = start_time
    
    # Steady period 1
    for _ in range(num_points // 3):
        data.append({
            'timestamp': int(current_time.timestamp() * 1000),
            'heart_rate': Decimal(str(steady_hr + (_ % 3))),
            'hrv': Decimal(str(50 + (_ % 2))),
            'sleep_score': Decimal('80')
        })
        current_time += timedelta(seconds=interval_seconds)
        
    # Volatile period
    for _ in range(num_points // 3):
        # Alternate between min and max to ensure high volatility
        val = volatile_hr_range[0] if _ % 2 == 0 else volatile_hr_range[1]
        data.append({
            'timestamp': int(current_time.timestamp() * 1000),
            'heart_rate': Decimal(str(val)),
            'hrv': Decimal(str(40 + (_ % 5))),
            'sleep_score': Decimal('75')
        })
        current_time += timedelta(seconds=interval_seconds)
        
    # Steady period 2
    for _ in range(num_points // 3):
        data.append({
            'timestamp': int(current_time.timestamp() * 1000),
            'heart_rate': Decimal(str(steady_hr_2 + (_ % 2))),
            'hrv': Decimal(str(55 + (_ % 3))),
            'sleep_score': Decimal('82')
        })
        current_time += timedelta(seconds=interval_seconds)
        
    return data

@pytest.fixture
def mock_data_adaptive():
    start_time = datetime(2025, 1, 1, 8, 0, 0)
    # 30 points over 30 minutes (1 point/min)
    return generate_mock_data(start_time, 30, 60, 70, (120, 150), 75)

def test_analyze_trend_increasing():
    data = [10, 12, 11, 13, 15]
    assert analyze_trend(data, threshold=0.1) == "trending_up"

def test_analyze_trend_decreasing():
    data = [15, 13, 14, 12, 10]
    assert analyze_trend(data, threshold=0.1) == "trending_down"

def test_analyze_trend_stable():
    data = [10, 11, 10, 11, 10]
    assert analyze_trend(data, threshold=0.1) == "stable"

def test_analyze_trend_insufficient_data():
    data = [10]
    assert analyze_trend(data, threshold=0.1) == "stable"

def test_adaptive_aggregate_data_basic(mock_data_adaptive):
    # Using very short min/max windows to force aggregation at changes
    min_win = 60 * 1000 # 1 minute
    max_win = 5 * 60 * 1000 # 5 minutes
    threshold = 2.0 # Low threshold to detect volatility
    
    aggregated = adaptive_aggregate_data(
        mock_data_adaptive, 
        min_window_ms=min_win, 
        max_window_ms=max_win, 
        threshold=threshold,
        target_metric='heart_rate'
    )
    
    # Expect more windows than fixed 5-min intervals due to volatility
    # Total 30 mins / 5 min window = 6 windows normally.
    # With adaptive, expect more due to volatile section.
    # Check that volatile section creates smaller windows.
    # This is a qualitative check based on data generation.
    # A more robust test would check stdev within each generated window.
    assert len(aggregated) > (len(mock_data_adaptive) * (mock_data_adaptive[1]['timestamp'] - mock_data_adaptive[0]['timestamp'])) / max_win
    
    # Verify that timestamps are increasing
    for i in range(1, len(aggregated)):
        assert aggregated[i]['timestamp'] > aggregated[i-1]['timestamp']
        
    # Verify some aggregation happened (e.g., heart_rate is present and float)
    for item in aggregated:
        assert 'heart_rate' in item
        if item['heart_rate'] is not None:
            assert isinstance(item['heart_rate'], float)


def test_adaptive_aggregate_data_stable_period():
    start_time = datetime(2025, 1, 1, 8, 0, 0)
    # 60 points over 60 minutes (1 point/min), very steady HR
    steady_data = generate_mock_data(start_time, 60, 60, 70, (70,71), 70)

    # Use larger max window to allow merging
    min_win = 5 * 60 * 1000 # 5 minutes
    max_win = 30 * 60 * 1000 # 30 minutes
    threshold = 1.0 # High threshold to ensure stability
    
    aggregated = adaptive_aggregate_data(
        steady_data, 
        min_window_ms=min_win, 
        max_window_ms=max_win, 
        threshold=threshold,
        target_metric='heart_rate'
    )
    
    # Expect fewer windows due to stability (e.g., 60 mins / 30 min max_win = 2 windows)
    assert len(aggregated) <= (len(steady_data) * (steady_data[1]['timestamp'] - steady_data[0]['timestamp'])) / min_win
    assert len(aggregated) >= (len(steady_data) * (steady_data[1]['timestamp'] - steady_data[0]['timestamp'])) / max_win


