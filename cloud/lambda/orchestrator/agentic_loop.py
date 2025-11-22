"""
Orchestrator Lambda: Direct Bedrock Model Invocation (Modular)
Routes events to specific 'Agent' Lambda functions.
"""

import json
import os
import boto3

lambda_client = boto3.client('lambda')

# Environment Variables for Child Agents
PROACTIVE_COACH_FUNCTION = os.environ.get('PROACTIVE_COACH_FUNCTION')
STATE_REACTOR_FUNCTION = os.environ.get('STATE_REACTOR_FUNCTION')

def handler(event, context):
    """
    Router for the multi-agent AI loop.
    """
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # --- ROUTING LOGIC ---
        # Check if this is a scheduled event (e.g., CloudWatch EventBridge)
        if event.get('source') == 'aws.events':
            print("Triggered by Schedule: Invoking Proactive Coach Agent")
            if not PROACTIVE_COACH_FUNCTION:
                print("Error: PROACTIVE_COACH_FUNCTION env var not set")
                return {'statusCode': 500, 'error': 'Configuration Error'}
            return invoke_agent(PROACTIVE_COACH_FUNCTION, event)

        # Otherwise, assume it's triggered by sensor data for a specific user
        user_id = event.get('user_id')
        if not user_id:
            print("No user_id provided in event.")
            return {'statusCode': 400, 'error': 'Missing user_id'}

        print(f"Triggered by Sensor Data: Invoking State Reactor Agent for {user_id}")
        if not STATE_REACTOR_FUNCTION:
            print("Error: STATE_REACTOR_FUNCTION env var not set")
            return {'statusCode': 500, 'error': 'Configuration Error'}
            
        return invoke_agent(STATE_REACTOR_FUNCTION, event)

    except Exception as e:
        print(f"Error in Orchestrator handler: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def invoke_agent(function_name, payload):
    """Helper to invoke child agent lambdas synchronously"""
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        response_payload = json.loads(response['Payload'].read().decode('utf-8'))
        return response_payload
        
    except Exception as e:
        print(f"Failed to invoke agent {function_name}: {e}")
        return {
            'statusCode': 500,
            'error': f"Failed to invoke agent {function_name}: {str(e)}"
        }