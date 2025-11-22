import json
from decimal import Decimal
from statistics import mean, stdev

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

def adaptive_aggregate_data(data_items, min_window_ms=300000, max_window_ms=3600000, threshold=5.0, target_metric='heart_rate', metrics=['heart_rate', 'hrv', 'sleep_score']):
    """
    Aggregates data using adaptive time windows based on volatility of a target metric.
    - Steady data (low stdev) -> Larger windows (up to max_window_ms).
    - Volatile data (high stdev) -> Smaller windows (down to min_window_ms).
    
    :param data_items: List of raw data dicts.
    :param min_window_ms: Minimum window size (e.g., 5 mins).
    :param max_window_ms: Maximum window size (e.g., 1 hour).
    :param threshold: Standard deviation threshold for the target metric.
    :param target_metric: The metric key to check volatility against.
    :param metrics: List of keys to aggregate.
    :return: List of aggregated dicts.
    """
    if not data_items:
        return []

    sorted_data = sorted(data_items, key=lambda x: x.get('timestamp', 0))
    results = []
    
    n = len(sorted_data)
    batch_start_idx = 0
    
    while batch_start_idx < n:
        batch_values_target = []
        batch_items = []
        
        batch_start_ts = sorted_data[batch_start_idx].get('timestamp', 0)
        
        current_idx = batch_start_idx
        
        while current_idx < n:
            item = sorted_data[current_idx]
            ts = item.get('timestamp', 0)
            
            # Extract target value for volatility check
            val = item.get(target_metric)
            if val is not None:
                if isinstance(val, Decimal): val = float(val)
                batch_values_target.append(val)
            
            batch_items.append(item)
            
            duration = ts - batch_start_ts
            
            # Check constraints
            # 1. If we haven't reached min_window, keep adding (unless we hit end)
            if duration < min_window_ms:
                current_idx += 1
                continue
                
            # 2. If we reached max_window, stop here
            if duration >= max_window_ms:
                current_idx += 1
                break
                
            # 3. Check Volatility (only if we have enough data points)
            if len(batch_values_target) > 2:
                try:
                    volatility = stdev(batch_values_target)
                except:
                    volatility = 0
                
                if volatility > threshold:
                    # High volatility detected! Close this kernel now to keep it small/detailed.
                    current_idx += 1
                    break
            
            # If stable, continue expanding this kernel
            current_idx += 1
            
        # Finalize aggregation for this batch
        agg_item = {'timestamp': batch_start_ts}
        
        # Calculate means for all requested metrics
        for key in metrics:
            values = []
            for item in batch_items:
                v = item.get(key)
                if v is not None:
                    if isinstance(v, Decimal): v = float(v)
                    values.append(v)
            
            agg_item[key] = mean(values) if values else None
        
        # Add duration for debug/context
        agg_item['window_duration_min'] = (sorted_data[current_idx-1]['timestamp'] - batch_start_ts) / 60000
            
        results.append(agg_item)
        
        # Advance
        batch_start_idx = current_idx
        
    return results

def aggregate_data_by_window(data_items, window_ms=3600000, metrics=['heart_rate', 'hrv', 'sleep_score']):
    """
    Aggregates a list of data items into time windows.
    
    :param data_items: List of dicts containing 'timestamp' and metric values.
    :param window_ms: Window size in milliseconds (default: 1 hour).
    :param metrics: List of keys to aggregate (calculate mean).
    :return: List of aggregated dicts.
    """
    if not data_items:
        return []

    # Sort by timestamp
    sorted_data = sorted(data_items, key=lambda x: x.get('timestamp', 0))
    
    aggregated_results = []
    current_window_start = sorted_data[0]['timestamp']
    current_window_end = current_window_start + window_ms
    
    current_batch = {key: [] for key in metrics}
    current_batch_count = 0
    
    for item in sorted_data:
        ts = item.get('timestamp', 0)
        
        # If item is outside current window, process the batch and start a new one
        if ts >= current_window_end:
            # Finalize current window
            agg_item = {'timestamp': current_window_start}
            for key in metrics:
                values = current_batch[key]
                if values:
                    agg_item[key] = mean(values)
                else:
                    agg_item[key] = None # Or keep it missing
            
            if current_batch_count > 0:
                aggregated_results.append(agg_item)
            
            # Reset for next window(s)
            # Handle gaps: simple approach, jump to next item's window
            current_window_start = ts - (ts % window_ms) # Align to grid if preferred, or just use ts
            # Or strictly follow windows:
            # while ts >= current_window_end:
            #    current_window_start += window_ms
            #    current_window_end += window_ms
            
            # Let's just start the new window at the current item for simplicity in this version
            current_window_start = ts
            current_window_end = current_window_start + window_ms
            current_batch = {key: [] for key in metrics}
            current_batch_count = 0
        
        # Add item to current batch
        for key in metrics:
            val = item.get(key)
            if val is not None:
                # Handle Decimal from DynamoDB
                if isinstance(val, Decimal):
                    val = float(val)
                current_batch[key].append(val)
        current_batch_count += 1

    # Process the final batch
    agg_item = {'timestamp': current_window_start}
    for key in metrics:
        values = current_batch[key]
        if values:
            agg_item[key] = mean(values)
        else:
            agg_item[key] = None
    
    if current_batch_count > 0:
        aggregated_results.append(agg_item)
        
    return aggregated_results
