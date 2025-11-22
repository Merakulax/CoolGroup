import boto3
import json
import time
from decimal import Decimal

# Config
REGION = 'eu-central-1'
PROJECT = 'tamagotchi-health'
ENV = 'dev'

# Resource Names
HEALTH_TABLE = f"{PROJECT}-health-data-{ENV}"
USER_STATE_TABLE = f"{PROJECT}-user-state-{ENV}"
USERS_TABLE = f"{PROJECT}-users-{ENV}"
ORCHESTRATOR_FUNC = f"{PROJECT}-orchestrator-{ENV}"

# Clients
dynamodb = boto3.resource('dynamodb', region_name=REGION)
lambda_client = boto3.client('lambda', region_name=REGION)

def test_state_reactor(user_id="test_user_agent"):
    print(f"\n--- Testing State Reactor (Structured Output) User: {user_id} ---")
    
    # 1. Seed Health Data
    print("Seeding Health Data...")
    table = dynamodb.Table(HEALTH_TABLE)
    item = {
        'user_id': user_id,
        'timestamp': int(time.time() * 1000),
        'heart_rate': 80,
        'steps': 5000,
        'activity_type': 'walking',
        'sleep_score': 85
    }
    table.put_item(Item=item)
    
    # 2. Invoke Orchestrator
    print("Invoking Orchestrator for State Reactor...")
    payload = {'user_id': user_id}
    
    start_time = time.time()
    response = lambda_client.invoke(
        FunctionName=ORCHESTRATOR_FUNC,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    duration = time.time() - start_time
    
    result = json.loads(response['Payload'].read())
    print(f"Result ({duration:.2f}s): {json.dumps(result, indent=2)}")
    
    # 3. Check State Table
    print("Verifying DB State...")
    state_table = dynamodb.Table(USER_STATE_TABLE)
    state = state_table.get_item(Key={'user_id': user_id}).get('Item')
    if state:
        print(f"Current State: {state.get('stateEnum')} | Reason: {state.get('reasoning')}")
    else:
        print("No state found (might be STABLE/Unchanged).")

def test_proactive_coach(user_id="test_user_agent"):
    print(f"\n--- Testing Proactive Coach (Structured Output) User: {user_id} ---")
    
    # Ensure user exists for coach to find them
    users_table = dynamodb.Table(USERS_TABLE)
    users_table.put_item(Item={'user_id': user_id, 'name': 'Test User'})

    # Seed some dummy history to give coach something to analyze
    for i in range(1, 4):
        item = {
            'user_id': user_id,
            'timestamp': int(time.time() * 1000) - (i * 86400 * 1000), # Days ago
            'heart_rate': 90 + i, # Slightly increasing HR
            'steps': 2000 + (i * 100), # Low steps
            'activity_type': 'sedentary',
            'sleep_score': 50 - (i * 5) # Decreasing sleep
        }
        dynamodb.Table(HEALTH_TABLE).put_item(Item=item)

    # Invoke Orchestrator with Schedule Payload
    print("Invoking Orchestrator for Proactive Coach (Scheduled Event)...")
    payload = {'source': 'aws.events'}
    
    start_time = time.time()
    response = lambda_client.invoke(
        FunctionName=ORCHESTRATOR_FUNC,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    duration = time.time() - start_time
    
    result = json.loads(response['Payload'].read())
    print(f"Result ({duration:.2f}s): {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    test_state_reactor()
    test_proactive_coach()
