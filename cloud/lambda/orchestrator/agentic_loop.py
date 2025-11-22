"""
Orchestrator Lambda: Direct Bedrock Model Invocation (Modular)
Routes events to specific 'Agent' modules (State Reactor, Proactive Coach).
"""

import json
from agents import state_reactor, proactive_coach

def handler(event, context):
    """
    Router for the multi-agent AI loop.
    """
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # --- ROUTING LOGIC ---
        # Check if this is a scheduled event (e.g., CloudWatch EventBridge)
        if event.get('source') == 'aws.events':
            print("Triggered by Schedule: Running Proactive Coach Loop")
            return proactive_coach.run()

        # Otherwise, assume it's triggered by sensor data for a specific user
        user_id = event.get('user_id')
        if not user_id:
            print("No user_id provided in event.")
            return {'statusCode': 400, 'error': 'Missing user_id'}

        return state_reactor.run(user_id)

    except Exception as e:
        print(f"Error in Orchestrator handler: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }