import json
import os
import boto3
import asyncio
from datetime import datetime
from core import database, context, actions, predictions
from core.utils import DecimalEncoder

lambda_client = boto3.client('lambda')

# Env Vars for Child Lambdas
ACTIVITY_FUNCTION = os.environ.get('ACTIVITY_FUNCTION')
VITALS_FUNCTION = os.environ.get('VITALS_FUNCTION')
WELLBEING_FUNCTION = os.environ.get('WELLBEING_FUNCTION')
SUPERVISOR_FUNCTION = os.environ.get('SUPERVISOR_FUNCTION')

def handler(event, lambda_context):
    """
    Orchestrator for the State Reactor Sub-System.
    Fans out to 3 Expert Lambdas, then calls Supervisor Lambda.
    """
    user_id = event.get('user_id')
    if not user_id:
        return {'statusCode': 400, 'body': json.dumps({'error': 'Missing user_id'})}

    print(f"State Reactor Orchestrator for {user_id}")

    # 1. PERCEPTION & CONTEXT GATHERING
    # Check if sensor_data was passed in event (fast path)
    sensor_batch = event.get('sensor_data')
    last_reading = None
    if sensor_batch and isinstance(sensor_batch, list) and len(sensor_batch) > 0:
        # Assuming the last item in batch is the latest
        last_reading = sensor_batch[-1]
    
    if not last_reading:
        last_reading = database.get_last_health_reading(user_id)
        
    if not last_reading:
         return {'statusCode': 200, 'message': 'No data'}

    context_data = context.get_historical_context(user_id) or {}
    history_context = context_data.get('context_data', "No historical context.")
    
    recent_history = database.get_recent_history(user_id, limit=7)
    predictive_context = predictions.get_predictive_context(user_id, recent_history)

    # 2. FAN-OUT TO EXPERTS
    # We use a helper to invoke them in parallel if possible, or sequential.
    # Since Lambda `handler` is synchronous usually, we can use a simple thread pool or just sequential for now to keep it simple and robust, 
    # OR use the asyncio loop if the runtime supports it (Python 3.11 does).
    
    try:
        experts_result = asyncio.run(invoke_experts_parallel(last_reading, history_context))
    except Exception as e:
        print(f"Expert Fan-Out Failed: {e}")
        return {'statusCode': 500, 'error': str(e)}

    SUPERVISOR_FUNCTION = os.environ.get('SUPERVISOR_FUNCTION')
    CHARACTERIZER_FUNCTION = os.environ.get('CHARACTERIZER_FUNCTION')

    # 3. SUPERVISOR SYNTHESIS
    supervisor_payload = {
        'experts_result': experts_result,
        'predictive_context': predictive_context
    }
    
    try:
        supervisor_resp = invoke_lambda(SUPERVISOR_FUNCTION, supervisor_payload)
    except Exception as e:
        print(f"Supervisor Failed: {e}")
        return {'statusCode': 500, 'error': str(e)}
        
    if 'error' in supervisor_resp:
        return {'statusCode': 500, 'error': f"Supervisor Error: {supervisor_resp['error']}"}

    analysis = supervisor_resp # The supervisor returns the structured analysis directly
    
    # 4. CHARACTERIZER (New Step)
    # Fetch Profile
    user_profile = database.get_user_profile(user_id)
    
    char_payload = {
        'analysis': analysis,
        'user_profile': user_profile
    }
    
    final_message = None
    try:
        if CHARACTERIZER_FUNCTION:
            char_resp = invoke_lambda(CHARACTERIZER_FUNCTION, char_payload)
            if 'message' in char_resp:
                final_message = char_resp['message']
                print(f"Characterized Message: {final_message}")
            else:
                print(f"Characterizer returned no message: {char_resp}")
                analysis['char_error_resp'] = char_resp
        else:
             print("CHARACTERIZER_FUNCTION env var not set.")
             analysis['char_error_env'] = "Env var not set"
             
    except Exception as e:
        print(f"Characterizer Failed (Non-blocking): {e}")
        analysis['char_error'] = str(e)

    # Fallback if no character message
    if not final_message:
        final_message = analysis.get('reasoning', 'State updated.')

    analysis['message'] = final_message

    # 5. STATE UPDATE (Legacy Logic)
    new_state_enum = analysis.get('state', 'UNKNOWN')
    
    last_state_item = database.get_last_state(user_id)
    last_state_enum = last_state_item.get('stateEnum', 'NONE') if last_state_item else 'NONE'
    
    should_trigger = (new_state_enum != last_state_enum)
    
    last_update_ts = last_state_item.get('timestamp', 0) if last_state_item else 0
    time_since_update = (int(datetime.now().timestamp() * 1000) - last_update_ts) / 1000
    
    if time_since_update > 3600: should_trigger = True
    if new_state_enum in ['STRESS', 'SICKNESS', 'EXERCISE'] and new_state_enum != last_state_enum:
        should_trigger = True

    if should_trigger:
        print(f"State Change: {last_state_enum} -> {new_state_enum}")
        database.update_state_db(user_id, analysis, time_since_update)
        actions.invoke_avatar_generator(user_id, analysis)
    
    # Always fetch the latest state from DB for the response
    final_state_item = database.get_last_state(user_id)

    # Handle case where final_state_item might still be None (e.g., first run, or DB error)
    if not final_state_item:
        final_state_item = {'message': analysis.get('message', 'State updated.'), 'last_updated': datetime.now().isoformat(), 'image_url': ''}

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': final_state_item.get('message', analysis.get('message', 'State updated.')),
            'image_url': final_state_item.get('image_url', ''),
            'last_updated': final_state_item.get('last_updated', datetime.now().isoformat())
        }, cls=DecimalEncoder)
    }

async def invoke_experts_parallel(sensor_data, history):
    # Convert data to JSON-ready dicts
    # (sensor_data is likely a DynamoDB item with Decimals, need handling before sending to other Lambdas if they expect JSON)
    # Ideally we send the raw dict and let boto3 serialize it, but boto3 default serializer fails on Decimal.
    # So we convert to JSON string and parse it back or just cast Decimals.
    # Actually, we can just pass the data and let the helper handle it.
    
    # Payload construction
    # Activity & Vitals only need sensor data
    payload_activity = {'sensor_data': json.loads(json.dumps(sensor_data, cls=DecimalEncoder))}
    payload_vitals = {'sensor_data': json.loads(json.dumps(sensor_data, cls=DecimalEncoder))}
    
    # Wellbeing needs history
    payload_wellbeing = {
        'sensor_data': json.loads(json.dumps(sensor_data, cls=DecimalEncoder)),
        'history': history
    }

    loop = asyncio.get_running_loop()
    
    # Run invokes in parallel threads
    f1 = loop.run_in_executor(None, invoke_lambda, ACTIVITY_FUNCTION, payload_activity)
    f2 = loop.run_in_executor(None, invoke_lambda, VITALS_FUNCTION, payload_vitals)
    f3 = loop.run_in_executor(None, invoke_lambda, WELLBEING_FUNCTION, payload_wellbeing)
    
    r1, r2, r3 = await asyncio.gather(f1, f2, f3)
    
    return {
        "activity": r1,
        "vitals": r2,
        "wellbeing": r3
    }

def invoke_lambda(func_name, payload):
    if not func_name:
        print(f"Error: Function name missing for payload keys: {payload.keys()}")
        return {"error": "Configuration Error: Missing Function Name"}
        
    response = lambda_client.invoke(
        FunctionName=func_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    return json.loads(response['Payload'].read())