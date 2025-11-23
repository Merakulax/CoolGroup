import json
import os
from core import llm
from core.utils import DecimalEncoder
from core.llm import WELLBEING_EXPERT_SCHEMA

def handler(event, context):
    print(f"Wellbeing Expert Received: {json.dumps(event)}")
    
    sensor_data = event.get('sensor_data')
    history = event.get('history', 'No history')
    
    sensor_str = json.dumps(sensor_data, cls=DecimalEncoder)
    
    prompt = f"""Analyze the user's mental wellbeing and recovery.
    Sensor Data: {sensor_str}
    History: {history}
    
    Rules:
    - Exhausted: Poor sleep history or high cumulative stress.
    - Stressed: High stress score (>80).
    - Calm: Low stress, good HRV.
    """
    
    result = llm.invoke_model_structured(prompt, "Analyze Wellbeing", WELLBEING_EXPERT_SCHEMA, temperature=0.5)
    
    if not result:
        return {'error': 'Wellbeing Model Failed'}
        
    return result
