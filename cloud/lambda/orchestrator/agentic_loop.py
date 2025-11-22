"""
Agentic Loop Orchestrator
The "Brain" of the system.
1. Fetches recent health history.
2. Uses "Council of Experts" (Multi-Agent) to analyze trends.
3. Updates state and triggers Avatar Generator ONLY if state changes.
"""

import json
import os
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import Agents
from agents.activity_agent import ActivityAgent
from agents.vitals_agent import VitalsAgent
from agents.wellbeing_agent import WellbeingAgent
from agents.supervisor_agent import SupervisorAgent

# Clients
dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')

# Tables
user_state_table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'user_state'))
health_table = dynamodb.Table(os.environ.get('HEALTH_TABLE', 'health_data'))
users_table = dynamodb.Table(os.environ.get('USERS_TABLE', 'users'))

def handler(event, context):
    """
    Orchestrate the multi-agent AI loop
    """
    try:
        user_id = event.get('user_id')
        if not user_id:
            print("No user_id provided.")
            return {'statusCode': 400, 'error': 'Missing user_id'}

        print(f"Starting Brain for user {user_id}")

        # 1. PERCEPTION: Gather History
        history = get_health_history(user_id, limit=20)
        if not history:
            print("No recent health data found.")
            return {'statusCode': 200, 'message': 'No data'}

        user_profile = get_user_profile(user_id)

        # 2. MULTI-AGENT REASONING
        # Initialize Agents
        activity_agent = ActivityAgent()
        vitals_agent = VitalsAgent()
        wellbeing_agent = WellbeingAgent()
        supervisor_agent = SupervisorAgent()
        
        # Run Agents in Parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_activity = executor.submit(activity_agent.analyze, history, user_profile)
            future_vitals = executor.submit(vitals_agent.analyze, history, user_profile)
            future_wellbeing = executor.submit(wellbeing_agent.analyze, history, user_profile)
            
            activity_res = future_activity.result()
            vitals_res = future_vitals.result()
            wellbeing_res = future_wellbeing.result()
            
        print(f"Activity Analysis: {json.dumps(activity_res)}")
        print(f"Vitals Analysis: {json.dumps(vitals_res)}")
        print(f"Wellbeing Analysis: {json.dumps(wellbeing_res)}")
        
        # Synthesis
        analysis = supervisor_agent.analyze(activity_res, vitals_res, wellbeing_res, user_profile)
        print(f"Supervisor Synthesis: {json.dumps(analysis)}")
        
        new_state_enum = analysis.get('state', 'UNKNOWN')
        # new_mood = analysis.get('mood', 'Neutral') 
        
        # 3. STATE DIFFING
        last_state_item = get_last_state(user_id)
        last_state_enum = last_state_item.get('stateEnum', 'NONE') if last_state_item else 'NONE'
        
        should_trigger = (new_state_enum != last_state_enum)
        
        last_update_ts = last_state_item.get('timestamp', 0) if last_state_item else 0
        time_since_update = (int(datetime.now().timestamp() * 1000) - last_update_ts) / 1000
        
        # Force refresh every hour
        if time_since_update > 3600: 
            should_trigger = True
            
        # Force refresh if specific critical states are detected (e.g. PANIC, FEVER)
        if new_state_enum in ['STRESS', 'SICKNESS', 'EXERCISE'] and new_state_enum != last_state_enum:
            should_trigger = True

        if should_trigger:
            print(f"State Change Detected: {last_state_enum} -> {new_state_enum}")
            
            # 4. ACTION: Persist & Visualize
            update_state_db(user_id, analysis, time_since_update)
            invoke_avatar_generator(user_id)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'UPDATED',
                    'old_state': last_state_enum,
                    'new_state': new_state_enum,
                    'reasoning': analysis.get('reasoning')
                })
            }
        else:
            print(f"State Stable ({new_state_enum}). No visual update needed.")
            return {
                'statusCode': 200,
                'body': json.dumps({'status': 'STABLE', 'state': new_state_enum})
            }

    except Exception as e:
        print(f"Error in Orchestrator: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def get_health_history(user_id, limit=20):
    """Fetch recent health records"""
    try:
        response = health_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id),
            ScanIndexForward=False, # Newest first
            Limit=limit
        )
        items = response.get('Items', [])
        return items[::-1] # Chronological order
    except Exception as e:
        print(f"DB Query Error: {e}")
        return []

def get_user_profile(user_id):
    try:
        resp = users_table.get_item(Key={'user_id': user_id})
        return resp.get('Item', {})
    except:
        return {}

def get_last_state(user_id):
    try:
        resp = user_state_table.get_item(Key={'user_id': user_id})
        return resp.get('Item')
    except:
        return None

def update_state_db(user_id, analysis, time_gap):
    """Update user state table with new analysis"""
    item = {
        'user_id': user_id,
        'timestamp': int(datetime.now().timestamp() * 1000),
        'stateEnum': analysis.get('state'),
        'mood': analysis.get('mood', 'Neutral'),
        'reasoning': analysis.get('reasoning', 'No reasoning provided'),
        'last_updated': datetime.now().isoformat()
    }
    try:
        user_state_table.put_item(Item=item)
    except Exception as e:
        print(f"Failed to update DB: {e}")

def invoke_avatar_generator(user_id):
    """Trigger the visual update"""
    # Hardcoded function name for Hackathon
    function_name = "tamagotchi-health-avatar-generator-dev" 
    
    try:
        lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='Event',
            Payload=json.dumps({'user_id': user_id})
        )
    except Exception as e:
        print(f"Failed to invoke avatar generator: {e}")
