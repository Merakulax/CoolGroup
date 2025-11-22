"""
Agentic Loop Orchestrator
The "Brain" of the system.
1. Fetches recent health history.
2. Uses Bedrock (Claude) to analyze trends and determine state.
3. Updates state and triggers Avatar Generator ONLY if state changes.
"""

import json
import os
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key
from decimal import Decimal

# Clients
dynamodb = boto3.resource('dynamodb')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='eu-central-1')
lambda_client = boto3.client('lambda')

# Tables
user_state_table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'user_state'))
health_table = dynamodb.Table(os.environ.get('HEALTH_TABLE', 'health_data'))
users_table = dynamodb.Table(os.environ.get('USERS_TABLE', 'users'))

def handler(event, context):
    """
    Orchestrate the agentic AI loop
    """
    try:
        user_id = event.get('user_id')
        if not user_id:
            print("No user_id provided.")
            return {'statusCode': 400, 'error': 'Missing user_id'}

        print(f"Starting Brain for user {user_id}")

        # 1. PERCEPTION: Gather History
        # Fetch last 15 minutes / 20 items
        history = get_health_history(user_id, limit=20)
        if not history:
            print("No recent health data found.")
            return {'statusCode': 200, 'message': 'No data'}

        # Fetch User Profile (Name, Pet Name)
        user_profile = get_user_profile(user_id)

        # 2. REASONING: Analyze Trend with Bedrock
        # We send the raw data to LLM to detect "Stress" vs "Exercise" vs "Sleep"
        analysis = analyze_with_bedrock(history, user_profile)
        
        print(f"AI Analysis: {json.dumps(analysis)}")
        
        new_state_enum = analysis.get('state', 'UNKNOWN')
        new_mood = analysis.get('mood', 'Neutral')
        reasoning = analysis.get('reasoning', 'No reasoning provided')
        
        # 3. STATE DIFFING
        last_state_item = get_last_state(user_id)
        last_state_enum = last_state_item.get('stateEnum', 'NONE') if last_state_item else 'NONE'
        
        # Logic: Update if State Enum changes OR Mood changes significantly OR it's been > 1 hour
        should_trigger = (new_state_enum != last_state_enum)
        
        # Optional: Time-based refresh (e.g., every hour even if state matches)
        last_update_ts = last_state_item.get('timestamp', 0) if last_state_item else 0
        time_since_update = (int(datetime.now().timestamp() * 1000) - last_update_ts) / 1000
        if time_since_update > 3600: 
            should_trigger = True

        if should_trigger:
            print(f"State Change Detected: {last_state_enum} -> {new_state_enum}")
            
            # 4. ACTION: Persist & Visualize
            
            # Update DB
            update_state_db(user_id, analysis, time_since_update)
            
            # Trigger Avatar Generator (Fire and Forget)
            invoke_avatar_generator(user_id)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'UPDATED',
                    'old_state': last_state_enum,
                    'new_state': new_state_enum
                })
            }
        else:
            print(f"State Stable ({new_state_enum}). No visual update needed.")
            return {
                'statusCode': 200,
                'body': json.dumps({'status': 'STABLE'})
            }

    except Exception as e:
        print(f"Error in Orchestrator: {str(e)}")
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
        # Reverse to chronological order for LLM
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

def analyze_with_bedrock(history, user_profile):
    """
    Send data to Claude to determine state.
    """
    model_id = "anthropic.claude-sonnet-4-5-20250929-v1:0"
    
    # Format data for prompt
    data_str = ""
    for item in history:
        # Simple format: Time: HR=X, Steps=Y, Stress=Z
        ts = datetime.fromtimestamp(int(item['timestamp'])/1000).strftime('%H:%M:%S')
        hr = item.get('heartRate', 'N/A')
        steps = item.get('stepCount', '0')
        stress = item.get('stressLevel', 'N/A')
        data_str += f"[{ts}] HR={hr}, Steps={steps}, Stress={stress}\n"
        
    pet_name = user_profile.get('pet_name', 'Pet')
    
    system_prompt = f"""You are the brain of a Tamagotchi. Your job is to analyze the user's physiological data and determine their STATE.
    
    Possible States:
    - REST: Low HR, Low movement.
    - WORK: Moderate HR, Low movement, maybe high Stress.
    - EXERCISE: High HR, High movement.
    - STRESSED: High HR, Low movement (Critical distinction!).
    - SLEEP: Very low HR, no movement, night time.
    
    Analyze the trend. Is HR rising? Is it stable?
    
    Output JSON ONLY:
    {{
        "state": "STATE_ENUM",
        "mood": "Adjective for the pet (e.g. Tired, Energetic, Anxious)",
        "reasoning": "Short explanation"
    }}
    """
    
    user_prompt = f"Data History (Last few minutes):\n{data_str}\n\nDetermine the current state."

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 300,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_prompt}
        ]
    })

    try:
        response = bedrock_runtime.invoke_model(
            body=body, 
            modelId=model_id, 
            accept='application/json', 
            contentType='application/json'
        )
        response_body = json.loads(response.get('body').read())
        text = response_body['content'][0]['text']
        
        # Parse JSON from text (Claude usually puts it in markdown block or plain)
        # Simple extraction
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = text[start:end]
            return json.loads(json_str)
        else:
            print(f"Failed to parse JSON from Claude: {text}")
            return {"state": "UNKNOWN", "mood": "Confused", "reasoning": "Parse Error"}
            
    except Exception as e:
        print(f"Bedrock Error: {e}")
        return {"state": "UNKNOWN", "mood": "Offline", "reasoning": str(e)}

def update_state_db(user_id, analysis, time_gap):
    """Update user state table with new analysis"""
    item = {
        'user_id': user_id,
        'timestamp': int(datetime.now().timestamp() * 1000),
        'stateEnum': analysis.get('state'),
        'mood': analysis.get('mood'),
        'reasoning': analysis.get('reasoning'),
        'last_updated': datetime.now().isoformat()
    }
    user_state_table.put_item(Item=item)

def invoke_avatar_generator(user_id):
    """Trigger the visual update"""
    project = os.environ.get('ENV', 'dev') # Simplified logic, usually passed in
    # Function name construction:
    # Terraform naming: ${var.project_name}-avatar-generator-${var.environment}
    # I need the project name. I'll assume 'tamagotchi-health' or fetch from env if passed.
    # Better: pass function name via Env Var in Terraform.
    # For now, I'll use the pattern I know.
    
    # Check context.function_name to guess project prefix?
    # Or just hardcode the pattern for now as it's Hackathon.
    # "tamagotchi-health-avatar-generator-dev"
    
    function_name = "tamagotchi-health-avatar-generator-dev" 
    
    try:
        lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='Event',
            Payload=json.dumps({'user_id': user_id})
        )
    except Exception as e:
        print(f"Failed to invoke avatar generator: {e}")