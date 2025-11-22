"""
Agentic Loop Orchestrator
The "Brain" of the system.
1. Fetches recent health history.
2. Invokes the AWS Bedrock Supervisor Agent (Multi-Agent System).
3. Updates state and triggers Avatar Generator ONLY if state changes.
"""

import json
import os
import boto3
import re
from datetime import datetime
from boto3.dynamodb.conditions import Key

# Clients
dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')

# Environment Variables
USER_STATE_TABLE = os.environ.get('DYNAMODB_TABLE', 'user_state')
HEALTH_TABLE = os.environ.get('HEALTH_TABLE', 'health_data')
USERS_TABLE = os.environ.get('USERS_TABLE', 'users')
SUPERVISOR_AGENT_ID = os.environ.get('SUPERVISOR_AGENT_ID')
SUPERVISOR_AGENT_ALIAS_ID = os.environ.get('SUPERVISOR_AGENT_ALIAS_ID')

# Tables
user_state_table = dynamodb.Table(USER_STATE_TABLE)
health_table = dynamodb.Table(HEALTH_TABLE)
users_table = dynamodb.Table(USERS_TABLE)

def handler(event, context):
    """
    Orchestrate the multi-agent AI loop via AWS Bedrock Agents
    """
    try:
        user_id = event.get('user_id')
        if not user_id:
            print("No user_id provided.")
            return {'statusCode': 400, 'error': 'Missing user_id'}

        if not SUPERVISOR_AGENT_ID or not SUPERVISOR_AGENT_ALIAS_ID:
            print("Missing Bedrock Agent Config")
            return {'statusCode': 500, 'error': 'Configuration Error'}

        print(f"Starting Brain for user {user_id}")

        # 1. PERCEPTION: Gather History
        history = get_health_history(user_id, limit=20)
        if not history:
            print("No recent health data found.")
            return {'statusCode': 200, 'message': 'No data'}

        user_profile = get_user_profile(user_id)
        
        # 2. REASONING: Invoke Bedrock Agent
        prompt = construct_prompt(user_profile, history)
        
        print(f"Invoking Bedrock Agent: {SUPERVISOR_AGENT_ID} (Alias: {SUPERVISOR_AGENT_ALIAS_ID})")
        
        response = bedrock_agent_runtime.invoke_agent(
            agentId=SUPERVISOR_AGENT_ID,
            agentAliasId=SUPERVISOR_AGENT_ALIAS_ID,
            sessionId=user_id, # Use user_id as session_id to maintain context
            inputText=prompt
        )
        
        completion = ""
        for event in response.get('completion'):
            chunk = event['chunk']
            if chunk:
                completion += chunk['bytes'].decode('utf-8')
                
        print(f"Agent Response: {completion}")
        
        # 3. SYNTHESIS: Parse JSON
        analysis = parse_agent_response(completion)
        if not analysis:
            print("Failed to parse agent response.")
            return {'statusCode': 500, 'error': 'Invalid Agent Response'}
            
        new_state_enum = analysis.get('state', 'UNKNOWN')
        
        # 4. STATE DIFFING
        last_state_item = get_last_state(user_id)
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

def construct_prompt(profile, history):
    """Format data for the Agent"""
    # Serialize Decimal types if necessary, but simple dicts should be fine
    return f"""
    Analyze the following user health data and determine the current state.
    
    User Profile:
    {json.dumps(profile, default=str)}
    
    Recent Health History (Most recent first):
    {json.dumps(history, default=str)}
    
    Remember to output ONLY valid JSON with keys: state, mood, reasoning.
    """

def parse_agent_response(text):
    """Extract JSON from potential markdown"""
    try:
        # Try direct parse
        return json.loads(text)
    except json.JSONDecodeError:
        # Try finding JSON block
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
    return None

def get_health_history(user_id, limit=20):
    try:
        response = health_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id),
            ScanIndexForward=False,
            Limit=limit
        )
        items = response.get('Items', [])
        return items[::-1]
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
    # Dynamic function name based on env would be better, but keeping simple for now
    # We should really look up the function ARN or name from env vars if passed, 
    # currently hardcoded in original file as 'tamagotchi-health-avatar-generator-dev'
    # Let's try to construct it from project/env if possible, or fallback.
    
    # Using the naming convention from terraform: "${var.project_name}-avatar-generator-${var.environment}"
    project = os.environ.get('PROJECT_NAME', 'tamagotchi-health') # Assuming default from variables.tf
    env = os.environ.get('ENV', 'dev')
    function_name = f"{project}-avatar-generator-{env}"
    
    try:
        lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='Event',
            Payload=json.dumps({'user_id': user_id})
        )
    except Exception as e:
        print(f"Failed to invoke avatar generator ({function_name}): {e}")