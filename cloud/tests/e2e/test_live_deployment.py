import pytest
import time
import uuid
import json
from decimal import Decimal

def test_api_connectivity(api_url, http_session):
    """
    Simple health check.
    """
    print(f"Testing connectivity to: {api_url}")
    # Echo endpoint is defined in terraform
    payload = {"message": "Hello E2E"}
    response = http_session.post(f"{api_url}/api/v1/echo", json=payload)
    assert response.status_code == 200
    
    # The Echo lambda returns: {"message": "Echo", "received": {"message": "Hello E2E"}, ...}
    body = response.json()
    assert body.get('message') == "Echo"
    assert body.get('received', {}).get('message') == "Hello E2E"

def test_user_flow_and_state_reaction(api_url, http_session, db_resource, dynamodb_table):
    """
    End-to-End Test:
    1. Create User
    2. Ingest Stress Data
    3. Verify DB State Change (Async)
    """
    # 1. Create User
    user_id = f"e2e_user_{uuid.uuid4().hex[:8]}"
    print(f"Creating E2E User: {user_id}")
    
    user_payload = {
        "user_id": user_id,
        "name": "E2E Test User",
        "pet_name": "TestBot",
        "goals": ["STRESS_MANAGEMENT"]
    }
    
    resp = http_session.post(f"{api_url}/api/v1/users", json=user_payload)
    assert resp.status_code in [200, 201]
    
    # 2. Ingest Stress Data (High HR, Low Motion)
    # This should trigger the Orchestrator -> State Reactor -> Bedrock
    print("Injecting 'Stress' sensor data...")
    
    ts = int(time.time() * 1000)
    sensor_payload = {
        # user_id is now in path, but we can leave it in body too, or remove it. 
        # Keeping it doesn't hurt if logic handles it, but let's verify path priority works by not relying on body user_id effectively?
        # Actually, the payload usually just has 'batch'.
        "batch": [
            {
                "timestamp": ts,
                "heartRate": 120, # Stress level
                "accelerometer": {"x": 0.01, "y": 0.02, "z": 0.99} # Stationary
            }
        ]
    }
    
    resp = http_session.post(f"{api_url}/api/v1/user/{user_id}/data", json=sensor_payload)
    assert resp.status_code == 200
    
    # 3. Poll DynamoDB for State Change
    # The Lambda chain is async, so we might need to wait a few seconds.
    print("Waiting for AI State Reactor...")
    table = db_resource.Table(dynamodb_table)
    
    max_retries = 30
    found_state = False
    
    for i in range(max_retries):
        print(f"  [Attempt {i+1}/{max_retries}] Polling DynamoDB...")
        time.sleep(2)
        
        # Get User State
        try:
            item_resp = table.get_item(Key={'user_id': user_id})
            item = item_resp.get('Item')
            
            if item:
                print(f"    -> Current State: {item.get('stateEnum')}")
                if item.get('stateEnum') in ['STRESS', 'EXERCISE']:
                    print(f"    ✅ SUCCESS: State transitioned to {item.get('stateEnum')}")
                    found_state = True
                    break
            else:
                print("    -> No state record found yet.")
        except Exception as e:
            print(f"    -> Error polling DB: {e}")
        
    assert found_state, "Failed to detect state change to STRESS within timeout."

def test_demo_trigger_override(api_url, http_session):
    """
    Test the manual override trigger used for demos.
    """
    payload = {
        "user_id": "demo_override_user",
        "force_state": "EXERCISE",
        "custom_message": "Forced by E2E"
    }
    
    resp = http_session.post(f"{api_url}/api/v1/demo/trigger", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    
    # The demo trigger invokes the orchestrator which returns the result in the body
    orch_result = body.get('orchestrator_result', {})
    
    # The Orchestrator response body is usually a JSON string
    if 'body' in orch_result:
        inner_body = json.loads(orch_result['body'])
        assert inner_body.get('new_state') == "EXERCISE"