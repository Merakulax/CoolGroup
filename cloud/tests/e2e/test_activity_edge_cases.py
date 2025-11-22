import pytest
import time
import uuid
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EDGE_SCENARIOS = [
    {
        "name": "Sickness / Fever",
        "description": "High Body Temp + Resting High HR + Stationary",
        "payload": {
            "heartRate": 95,
            "bodyTemperature": 38.5,
            "accelerometer": {"x": 0.01, "y": 0.01, "z": 0.99},
            "step_count": 0
        },
        "expected_keywords": ["resting", "sleeping"] # Sick maps to Resting
    },
    {
        "name": "Commute / Driving",
        "description": "High Speed + Low Steps",
        "payload": {
            "heartRate": 75,
            "speed": 25.0, # ~90 km/h
            "step_count": 0,
            "accelerometer": {"x": 0.1, "y": 0.1, "z": 0.9} # Mild vibration
        },
        "expected_keywords": ["commuting"]
    },
    {
        "name": "Meditation",
        "description": "Low HR + Low Stress + Stationary",
        "payload": {
            "heartRate": 58,
            "stress_score": 15,
            "accelerometer": {"x": 0.0, "y": 0.0, "z": 1.0},
            "sleep_status": "AWAKE", # Explicitly awake to differentiate from Sleep
            "step_count": 0
        },
        "expected_keywords": ["meditating", "resting"]
    }
]

def test_activity_edge_cases(api_url, http_session, db_resource, dynamodb_table):
    """
    Tests if the AI can infer complex activities from specific sensor combinations.
    """
    table = db_resource.Table(dynamodb_table)
    
    for scenario in EDGE_SCENARIOS:
        logger.info(f"--- Testing Edge Case: {scenario['name']} ---")
        user_id = f"e2e_edge_{uuid.uuid4().hex[:8]}"
        
        create_user(api_url, http_session, user_id)
        
        ingest_data(api_url, http_session, user_id, scenario['payload'])
        
        verify_activity(table, user_id, scenario['expected_keywords'])

def create_user(api_url, session, user_id):
    payload = {
        "user_id": user_id,
        "name": f"Edge User {user_id}",
        "pet_name": "EdgeBot",
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

def verify_activity(table, user_id, keywords):
    logger.info(f"Waiting for activity matching: {keywords}")
    max_retries = 30 # 60s
    
    last_activity = "None"
    
    for i in range(max_retries):
        time.sleep(2)
        try:
            item_resp = table.get_item(Key={'user_id': user_id})
            item = item_resp.get('Item')
            
            if item:
                last_activity = item.get('detected_activity', 'Unknown')
                logger.info(f"  [Attempt {i+1}] Detected: {last_activity}")
                
                if any(k in last_activity.lower() for k in keywords):
                    logger.info(f"  ✅ Match found!")
                    return
        except Exception as e:
            logger.warning(f"  Error: {e}")
            
    pytest.fail(f"Failed to detect expected activity. Expected one of {keywords}, got: '{last_activity}'")
