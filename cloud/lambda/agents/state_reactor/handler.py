import json
from datetime import datetime
from core import database, llm, context, actions, predictions
from core.utils import DecimalEncoder
from core.llm import PET_STATE_TOOL_SCHEMA # Import the schema

def handler(event, lambda_context):
    """
    Lambda handler for the State Reactor.
    Analyzes current sensor data and historical context to determine pet's state.
    """
    user_id = event.get('user_id')
    if not user_id:
        print("Error: user_id missing in event")
        return {'statusCode': 400, 'body': json.dumps({'error': 'Missing user_id'})}

    print(f"Starting State Reactor for user {user_id}")

    # 1. PERCEPTION: Gather Sensor Data
    last_reading = database.get_last_health_reading(user_id)
    if not last_reading:
         print("No recent sensor data found.")
         return {'statusCode': 200, 'message': 'No data'}

    # Invoke Context Retriever Lambda to get historical context
    context_data = context.get_historical_context(user_id)
    history_context = "No historical context available." # Default
    if context_data and context_data.get('context_data'):
        history_context = context_data['context_data']

    # Get recent history for predictive analysis
    recent_history = database.get_recent_history(user_id, limit=7) # last 7 entries
    predictive_context = predictions.get_predictive_context(user_id, recent_history)

    # 2. REASONING: Invoke Bedrock Model for State Analysis
    system_prompt = f"""You are the Lead Health Coach for a Tamagotchi-like health companion.
Your goal is to analyze the user's health data and determine the Pet's state.

Here is relevant historical context for the user:
{history_context}

Here is a predictive analysis based on recent trends:
{json.dumps(predictive_context, cls=DecimalEncoder)}

Based on the current, historical, and predictive data, call the 'pet_state_analyzer' tool to output the pet's state.
"""

    user_message = f"""
    Current Sensor Data:
    {json.dumps(last_reading, cls=DecimalEncoder)}
    
    Analyze the user's state based on this data and the historical context provided. Output your response by calling the 'pet_state_analyzer' tool.
    """

    # Invoke structured model
    analysis = llm.invoke_model_structured(system_prompt, user_message, PET_STATE_TOOL_SCHEMA, temperature=0.5)
    
    if not analysis:
        print("Failed to get structured model response from State Reactor.")
        return {'statusCode': 500, 'error': 'Invalid Model Response from State Reactor'}
            
    new_state_enum = analysis.get('state', 'UNKNOWN')
    
    # 4. STATE DIFFING
    last_state_item = database.get_last_state(user_id)
    last_state_enum = last_state_item.get('stateEnum', 'NONE') if last_state_item else 'NONE'
    
    should_trigger = (new_state_enum != last_state_enum)
    
    last_update_ts = last_state_item.get('timestamp', 0) if last_state_item else 0
    time_since_update = (int(datetime.now().timestamp() * 1000) - last_update_ts) / 1000
    
    # Force refresh rules
    if time_since_update > 3600: should_trigger = True
    if new_state_enum in ['STRESS', 'SICKNESS', 'EXERCISE'] and new_state_enum != last_state_enum:
        should_trigger = True

    if should_trigger:
        print(f"State Change Detected: {last_state_enum} -> {new_state_enum}")
        database.update_state_db(user_id, analysis, time_since_update)
        actions.invoke_avatar_generator(user_id)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'UPDATED',
                'old_state': last_state_enum,
                'new_state': new_state_enum,
                'reasoning': analysis.get('reasoning')
            }, cls=DecimalEncoder)
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'STABLE', 'state': new_state_enum}, cls=DecimalEncoder)
        }