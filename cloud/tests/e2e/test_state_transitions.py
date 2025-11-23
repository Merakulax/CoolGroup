import pytest
import time
import uuid
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCENARIOS = [
    {
        "name": "Deep Sleep",
        "expected_states": ["TIRED", "NEUTRAL"], # TIRED/NEUTRAL is the closest proxy for Sleep in our Enum
        "payload": {
            "heartRate": 55,
            "accelerometer": {"x": 0.0, "y": 0.0, "z": 1.0},
            "sleep_status": "ASLEEP",
            "step_count": 0
        }
    },
    {
        "name": "Intense Run",
        "expected_states": ["EXERCISE"],
        "payload": {
            "heartRate": 160,
            "accelerometer": {"x": 1.5, "y": 1.2, "z": 0.8},
            "step_count": 5000,
            "activity_type": "RUNNING"
        }
    },
    {
        "name": "Panic/Stress",
        "expected_states": ["STRESS", "ANXIOUS"],
        "payload": {
            "heartRate": 130,
            "accelerometer": {"x": 0.01, "y": 0.02, "z": 0.99}, # Stationary
            "step_count": 0,
            "stress_score": 90
        }
    },
    {
        "name": "Casual Walk",
        "expected_states": ["HAPPY", "NEUTRAL", "EXERCISE"],
        "payload": {
            "heartRate": 95,
            "accelerometer": {"x": 0.2, "y": 0.3, "z": 0.9},
            "step_count": 1000
        }
    }
]

def test_state_transitions(api_url, http_session, db_resource, dynamodb_table):
    """
    Iterates through defined scenarios and verifies if the Cloud Brain
    transitions the Pet to the expected state.
    """
    table = db_resource.Table(dynamodb_table)
    
    for scenario in SCENARIOS:
        logger.info(f"--- Testing Scenario: {scenario['name']} ---")
        
        # 1. Create a fresh user for each scenario to avoid history pollution
        user_id = f"e2e_{uuid.uuid4().hex[:8]}"
        create_user(api_url, http_session, user_id)
        
        # 2. Ingest Data
        ingest_data(api_url, http_session, user_id, scenario['payload'])
        
        # 3. Verify State
        verify_state(table, user_id, scenario['expected_states'])

def create_user(api_url, session, user_id):
    payload = {
        "user_id": user_id,
        "name": f"Test User {user_id}",
        "pet_name": "Bot",
        "goals": ["GENERAL_HEALTH"]
    }
    resp = session.post(f"{api_url}/api/v1/users", json=payload)
    assert resp.status_code in [200, 201]

def ingest_data(api_url, session, user_id, data):
    ts = int(time.time() * 1000)
    payload = {
        "batch": [
            {
                "timestamp": ts,
                **data
            }
        ]
    }
    resp = session.post(f"{api_url}/api/v1/user/{user_id}/data", json=payload)
    assert resp.status_code == 200

def verify_state(table, user_id, allowed_states):
    logger.info(f"Waiting for state to become one of {allowed_states}...")
    
    max_retries = 45 # 90 seconds
    
    for i in range(max_retries):
        time.sleep(2)
        try:
            item_resp = table.get_item(Key={'user_id': user_id})
            item = item_resp.get('Item')
            
            if item:
                current_state = item.get('stateEnum')
                reasoning = item.get('reasoning', 'No reasoning')
                logger.info(f"  [Attempt {i+1}] Current: {current_state} (Reason: {reasoning})")
                
                if current_state in allowed_states:
                    # Verify message content
                    message = item.get('message') or item.get('reasoning', '')
                    if not message:
                        logger.warning("  ⚠️ State matched but message is empty!")
                    else:
                        logger.info(f"  ✅ State Match! Message: {message}")
                        return
        except Exception as e:
            logger.warning(f"  Error polling: {e}")
            
    pytest.fail(f"State failed to transition to {allowed_states} for user {user_id}")
