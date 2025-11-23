import json
import os
from core import llm
from core.utils import DecimalEncoder
from core.llm import ACTIVITY_EXPERT_SCHEMA

def handler(event, context):
    print(f"Activity Expert Received: {json.dumps(event)}")
    
    sensor_data = event.get('sensor_data')
    if not sensor_data:
        return {'error': 'Missing sensor_data'}
        
    sensor_str = json.dumps(sensor_data, cls=DecimalEncoder)
    
    # Fast path for Sleep
    if sensor_data.get('sleep_status') == 'ASLEEP':
        return {
            "activity_type": "Sleeping",
            "intensity": "Low",
            "reasoning": "User is marked as ASLEEP in sensor data."
        }
    
    prompt = f"""Analyze the user's physical activity context.
    Sensor Data: {sensor_str}
    
    Rules:
    - Sleeping: Heart Rate < 60 AND (sleep_status='ASLEEP' OR (step_count=0 AND accelerometer nearly zero)).
    - Sedentary: Low movement, low HR (Sitting, Desk work).
    - Commuting: High speed (>10km/h) AND low steps.
    - Running/Workout: High HR (>110) AND High movement (MUST have steps > 0 OR accelerometer variance).
    - Meditating: Low HR (<60) AND Awake AND Stationary.
    - Stress/Anxiety: High HR (>100) AND Low movement (Stationary, 0 steps).
    
    Determine the activity type based on these rules. If HR is high but steps are 0 and movement is low, it is NOT a workout (unless explicitly marked), it is likely Stress/Anxiety."""
    
    result = llm.invoke_model_structured(prompt, "Analyze Activity", ACTIVITY_EXPERT_SCHEMA, temperature=0.5)
    
    if not result:
        return {'error': 'Activity Model Failed'}
        
    return result
