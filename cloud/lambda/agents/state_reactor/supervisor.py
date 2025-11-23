import json
import os
from core import llm
from core.utils import DecimalEncoder
from core.llm import SUPERVISOR_SCHEMA

def handler(event, context):
    print(f"Supervisor Received: {json.dumps(event)}")
    
    experts_result = event.get('experts_result', {})
    predictive_context = event.get('predictive_context', {})
    
    prompt = f"""You are the Supervisor of the Tamagotchi Health System.
Your goal is to synthesize the reports from three Expert Agents (Activity, Vitals, Wellbeing) and determine the final Pet State.

--- EXPERT REPORTS ---
[ACTIVITY EXPERT]: {json.dumps(experts_result.get('activity'), cls=DecimalEncoder)}
[VITALS EXPERT]: {json.dumps(experts_result.get('vitals'), cls=DecimalEncoder)}
[WELLBEING EXPERT]: {json.dumps(experts_result.get('wellbeing'), cls=DecimalEncoder)}

--- CONTEXT ---
Predictive Trends: {json.dumps(predictive_context, cls=DecimalEncoder)}

--- RULES ---
- Prioritize VITALS for safety (e.g., if Vitals says 'Critical', state is SICKNESS).
- Prioritize ACTIVITY for context (e.g., if Activity is 'Running', state is EXERCISE).
- Prioritize WELLBEING for mood (e.g., if Wellbeing is 'Exhausted', state is TIRED/STRESS).
- Conflict Resolution: Activity 'Sedentary' + Wellbeing 'Stressed' -> STRESS (Work). Activity 'Sedentary' + Wellbeing 'Calm' -> NEUTRAL/HAPPY.

IMPORTANT: Provide the 'reasoning' as a detailed technical explanation of why this state was chosen.

Based on these reports, call the 'pet_state_supervisor_decision' tool to finalize the state.
"""
    
    result = llm.invoke_model_structured(prompt, "Synthesize the state.", SUPERVISOR_SCHEMA, temperature=0.3)
    
    if not result:
        return {'error': 'Supervisor Model Failed'}
        
    return result
