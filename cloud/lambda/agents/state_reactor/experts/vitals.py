import json
import os
from core import llm
from core.utils import DecimalEncoder
from core.llm import VITALS_EXPERT_SCHEMA

def handler(event, context):
    print(f"Vitals Expert Received: {json.dumps(event)}")
    
    sensor_data = event.get('sensor_data')
    if not sensor_data:
        return {'error': 'Missing sensor_data'}
        
    sensor_str = json.dumps(sensor_data, cls=DecimalEncoder)
    
    prompt = f"""Analyze the user's physiological safety.
    Sensor Data: {sensor_str}
    
    Rules:
    - Critical: HR > 180 or SpO2 < 90.
    - Abnormal: Fever (BodyTemp > 37.5).
    - Elevated: HR > 100 at rest.
    - Normal: Everything within standard ranges.
    """
    
    result = llm.invoke_model_structured(prompt, "Analyze Vitals", VITALS_EXPERT_SCHEMA, temperature=0.2)
    
    if not result:
        return {'error': 'Vitals Model Failed'}
        
    return result
